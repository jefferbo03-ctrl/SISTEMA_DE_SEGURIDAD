import os
import datetime as dt
from pathlib import Path
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from werkzeug.security import generate_password_hash, check_password_hash

from db import init_db, get_conn
from importer import load_people_from_excel
from notify import send_email, send_sms

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ============ UTILIDADES ============
def parse_iso_date(s: str):
    if not s:
        return None
    s = s.strip()
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        try:
            return dt.datetime.strptime(s, "%d/%m/%Y").date()
        except ValueError:
            return None

def days_left(vencimiento_iso: str, tzname: str):
    if not vencimiento_iso:
        return None
    tz = pytz.timezone(tzname)
    today = dt.datetime.now(tz).date()
    venc = dt.date.fromisoformat(vencimiento_iso)
    return (venc - today).days

def get_alert_days():
    raw = os.getenv("ALERT_DAYS", "60,30,15,7,1,0")
    out = []
    for x in raw.split(","):
        x = x.strip()
        if not x:
            continue
        try:
            out.append(int(x))
        except ValueError:
            pass
    return sorted(set(out), reverse=True)

def already_sent(conn, person_id, especializacion, fecha_vencimiento, days_before, channel):
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM notifications
        WHERE person_id=? AND especializacion=? AND fecha_vencimiento=? AND days_before=? AND channel=?
        LIMIT 1
    """, (person_id, especializacion, fecha_vencimiento, days_before, channel))
    return cur.fetchone() is not None

def mark_sent(conn, person_id, especializacion, fecha_vencimiento, days_before, channel):
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO notifications (person_id, especializacion, fecha_vencimiento, days_before, channel)
        VALUES (?,?,?,?,?)
    """, (person_id, especializacion, fecha_vencimiento, days_before, channel))
    conn.commit()

# ============ AUTENTICACIÓN ============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debes iniciar sesión primero.", "warn")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debes iniciar sesión primero.", "warn")
            return redirect(url_for('login'))
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE id=?", (session['user_id'],))
        user = cur.fetchone()
        conn.close()
        
        if not user or user['role'] not in ['admin', 'superuser']:
            flash("No tienes permisos para acceder a esta sección.", "warn")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============ ALERTAS ============
def run_alert_check():
    tzname = os.getenv("TIMEZONE", "America/Bogota")
    alerts = get_alert_days()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM people")
    people = cur.fetchall()

    sent_count = 0
    errors = 0

    for p in people:
        d = days_left(p["fecha_vencimiento"], tzname)
        if d is None:
            continue
        if d not in alerts:
            continue

        fecha_v = p["fecha_vencimiento"]
        nombre = f'{p["nombre"]} {p["apellido"]}'.strip()
        esp = p["especializacion"]

        msg = (
            f"Hola {nombre}.\n\n"
            f"Tu especialización: {esp}\n"
            f"Vence el: {fecha_v} (faltan {d} días).\n\n"
            f"Te recomendamos programar el reentrenamiento con anticipación.\n\n"
            f"Saludos,\nSistema de Alerta Temprana"
        )
        subject = f"[Alerta] Vencimiento de especialización en {d} días - {nombre}"

        # Email
        if p["email"]:
            try:
                if not already_sent(conn, p["id"], esp, fecha_v, d, "email"):
                    send_email(p["email"], subject, msg)
                    mark_sent(conn, p["id"], esp, fecha_v, d, "email")
                    sent_count += 1
            except Exception as e:
                print(f"Error enviando email: {e}")
                errors += 1

        # SMS
        if p["celular"]:
            try:
                if not already_sent(conn, p["id"], esp, fecha_v, d, "sms"):
                    send_sms(p["celular"], msg)
                    mark_sent(conn, p["id"], esp, fecha_v, d, "sms")
                    sent_count += 1
            except Exception as e:
                print(f"Error enviando SMS: {e}")
                errors += 1

    conn.close()
    return sent_count, errors

# ============ APP FLASK ============
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-key-change-me")

@app.before_first_request
def _startup():
    init_db()

# ============ AUTENTICACIÓN ============
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Bienvenido, {user['username']}!", "ok")
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos.", "warn")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "ok")
    return redirect(url_for('login'))

# ============ PANEL PRINCIPAL ============
@app.route("/")
@login_required
def index():
    tzname = os.getenv("TIMEZONE", "America/Bogota")
    q = (request.args.get("q") or "").strip().lower()
    filtro = (request.args.get("filtro") or "").strip()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM people ORDER BY fecha_vencimiento ASC")
    rows = cur.fetchall()
    conn.close()

    people = []
    proximo_count = 0
    vencido_count = 0
    
    for p in rows:
        dias = days_left(p["fecha_vencimiento"], tzname)
        item = dict(p)
        item["dias"] = dias
        
        # Contadores para estadísticas
        if dias is not None:
            if 0 <= dias <= 30:
                proximo_count += 1
            elif dias < 0:
                vencido_count += 1

        hay = " ".join([
            item.get("nombre",""), item.get("apellido",""),
            item.get("empresa","") or "", item.get("especializacion","")
        ]).lower()
        if q and q not in hay:
            continue
        if filtro == "proximo" and (dias is None or dias > 30 or dias < 0):
            continue
        if filtro == "vencido" and (dias is None or dias >= 0):
            continue

        people.append(item)

    stats = {
        'total': len(rows),
        'proximo': proximo_count,
        'vencido': vencido_count
    }

    return render_template("index.html", people=people, q=q, filtro=filtro, stats=stats)

# ============ GESTIÓN DE PERSONAS ============
@app.route("/add", methods=["GET", "POST"])
@admin_required
def add():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre","").strip(),
            "apellido": request.form.get("apellido","").strip(),
            "especializacion": request.form.get("especializacion","").strip(),
            "fecha_expedicion": request.form.get("fecha_expedicion","").strip(),
            "fecha_vencimiento": request.form.get("fecha_vencimiento","").strip(),
            "escuela": request.form.get("escuela","").strip(),
            "empresa": request.form.get("empresa","").strip(),
            "email": request.form.get("email","").strip(),
            "celular": request.form.get("celular","").strip(),
        }

        fv = parse_iso_date(data["fecha_vencimiento"])
        if not fv:
            flash("Fecha de vencimiento inválida. Usa YYYY-MM-DD o dd/mm/yyyy", "warn")
            return redirect(url_for("add"))

        fe = parse_iso_date(data["fecha_expedicion"])
        data["fecha_expedicion"] = fe.isoformat() if fe else None
        data["fecha_vencimiento"] = fv.isoformat()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO people (nombre, apellido, especializacion, fecha_expedicion, fecha_vencimiento, escuela, empresa, email, celular)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (data["nombre"], data["apellido"], data["especializacion"], data["fecha_expedicion"], data["fecha_vencimiento"],
              data["escuela"], data["empresa"], data["email"], data["celular"]))
        conn.commit()
        conn.close()
        flash("Persona guardada exitosamente.", "ok")
        return redirect(url_for("index"))

    return render_template("add_edit.html", person=None)

@app.route("/edit/<int:pid>", methods=["GET", "POST"])
@admin_required
def edit(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM people WHERE id=?", (pid,))
    person = cur.fetchone()

    if not person:
        conn.close()
        flash("No existe esa persona.", "warn")
        return redirect(url_for("index"))

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre","").strip(),
            "apellido": request.form.get("apellido","").strip(),
            "especializacion": request.form.get("especializacion","").strip(),
            "fecha_expedicion": request.form.get("fecha_expedicion","").strip(),
            "fecha_vencimiento": request.form.get("fecha_vencimiento","").strip(),
            "escuela": request.form.get("escuela","").strip(),
            "empresa": request.form.get("empresa","").strip(),
            "email": request.form.get("email","").strip(),
            "celular": request.form.get("celular","").strip(),
        }

        fv = parse_iso_date(data["fecha_vencimiento"])
        if not fv:
            conn.close()
            flash("Fecha de vencimiento inválida. Usa YYYY-MM-DD o dd/mm/yyyy", "warn")
            return redirect(url_for("edit", pid=pid))

        fe = parse_iso_date(data["fecha_expedicion"])
        data["fecha_expedicion"] = fe.isoformat() if fe else None
        data["fecha_vencimiento"] = fv.isoformat()

        cur.execute("""
            UPDATE people
            SET nombre=?, apellido=?, especializacion=?, fecha_expedicion=?, fecha_vencimiento=?, escuela=?, empresa=?, email=?, celular=?
            WHERE id=?
        """, (data["nombre"], data["apellido"], data["especializacion"], data["fecha_expedicion"], data["fecha_vencimiento"],
              data["escuela"], data["empresa"], data["email"], data["celular"], pid))
        conn.commit()
        conn.close()
        flash("Cambios guardados exitosamente.", "ok")
        return redirect(url_for("index"))

    conn.close()
    return render_template("add_edit.html", person=dict(person))

@app.route("/delete/<int:pid>")
@admin_required
def delete(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM people WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    flash("Persona eliminada exitosamente.", "ok")
    return redirect(url_for("index"))

# ============ CARGA MASIVA ============
@app.route("/upload", methods=["GET", "POST"])
@admin_required
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename.lower().endswith(".xlsx"):
            flash("Sube un archivo .xlsx válido", "warn")
            return redirect(url_for("upload"))

        path = UPLOAD_DIR / f.filename
        f.save(path)

        try:
            people = load_people_from_excel(str(path))
        except Exception as e:
            flash(f"Error leyendo el Excel: {e}", "warn")
            return redirect(url_for("upload"))

        conn = get_conn()
        cur = conn.cursor()
        inserted = 0
        for p in people:
            cur.execute("""
                INSERT INTO people (nombre, apellido, especializacion, fecha_expedicion, fecha_vencimiento, escuela, empresa, email, celular)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (p["nombre"], p["apellido"], p["especializacion"], p["fecha_expedicion"], p["fecha_vencimiento"],
                  p.get("escuela",""), p.get("empresa",""), p.get("email",""), p.get("celular","")))
            inserted += 1
        conn.commit()
        conn.close()
        flash(f"Importación exitosa. {inserted} registros cargados.", "ok")
        return redirect(url_for("index"))

    return render_template("upload.html")

# ============ GESTIÓN DE USUARIOS ============
@app.route("/users")
@admin_required
def users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users ORDER BY role, username")
    users_list = cur.fetchall()
    conn.close()
    return render_template("users.html", users=users_list)

@app.route("/users/add", methods=["GET", "POST"])
@admin_required
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()

        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "warn")
            return redirect(url_for("add_user"))

        conn = get_conn()
        cur = conn.cursor()
        
        # Verificar si el usuario ya existe
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone():
            conn.close()
            flash("El nombre de usuario ya existe.", "warn")
            return redirect(url_for("add_user"))

        hashed = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES (?,?,?,?)
        """, (username, hashed, email, role))
        conn.commit()
        conn.close()
        flash(f"Usuario '{username}' creado exitosamente.", "ok")
        return redirect(url_for("users"))

    return render_template("add_edit_user.html", user=None)

@app.route("/users/edit/<int:uid>", methods=["GET", "POST"])
@admin_required
def edit_user(uid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (uid,))
    user = cur.fetchone()

    if not user:
        conn.close()
        flash("Usuario no encontrado.", "warn")
        return redirect(url_for("users"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()

        if password:
            hashed = generate_password_hash(password)
            cur.execute("""
                UPDATE users SET username=?, email=?, password=?, role=?
                WHERE id=?
            """, (username, email, hashed, role, uid))
        else:
            cur.execute("""
                UPDATE users SET username=?, email=?, role=?
                WHERE id=?
            """, (username, email, role, uid))
        
        conn.commit()
        conn.close()
        flash("Usuario actualizado exitosamente.", "ok")
        return redirect(url_for("users"))

    conn.close()
    return render_template("add_edit_user.html", user=dict(user))

@app.route("/users/delete/<int:uid>")
@admin_required
def delete_user(uid):
    if uid == session.get('user_id'):
        flash("No puedes eliminar tu propio usuario.", "warn")
        return redirect(url_for("users"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    flash("Usuario eliminado exitosamente.", "ok")
    return redirect(url_for("users"))

# ============ CONFIGURACIÓN ============
@app.route("/settings")
@admin_required
def settings():
    tz = os.getenv("TIMEZONE", "America/Bogota")
    alert_days = ",".join(map(str, get_alert_days()))
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM notifications")
    notif_count = cur.fetchone()['total']
    conn.close()
    
    return render_template("settings.html", tz=tz, alert_days=alert_days, notif_count=notif_count)

@app.route("/run-check")
@admin_required
def run_check():
    sent, err = run_alert_check()
    flash(f"Chequeo ejecutado. Alertas enviadas: {sent}. Errores: {err}.", "ok" if err == 0 else "warn")
    return redirect(url_for("index"))

# ============ SCHEDULER ============
def start_scheduler():
    tzname = os.getenv("TIMEZONE", "America/Bogota")
    tz = pytz.timezone(tzname)
    sched = BackgroundScheduler(timezone=tz)
    trigger = CronTrigger(hour=8, minute=0)
    sched.add_job(run_alert_check, trigger, id="daily_check", replace_existing=True)
    sched.start()
    return sched

if __name__ == "__main__":
    init_db()
    start_scheduler()
    app.run(host="127.0.0.1", port=5000, debug=True)