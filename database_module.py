import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "alerta.db"

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con todas las tablas necesarias"""
    conn = get_conn()
    cur = conn.cursor()

    # Tabla de personas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            especializacion TEXT NOT NULL,
            fecha_expedicion TEXT,
            fecha_vencimiento TEXT NOT NULL,
            escuela TEXT,
            empresa TEXT,
            email TEXT,
            celular TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabla de notificaciones enviadas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            especializacion TEXT NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            days_before INTEGER NOT NULL,
            channel TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
            UNIQUE(person_id, especializacion, fecha_vencimiento, days_before, channel)
        )
    """)

    # Tabla de usuarios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # Crear usuario admin por defecto si no existe
    cur.execute("SELECT id FROM users WHERE username='admin'")
    if not cur.fetchone():
        admin_pass = generate_password_hash("admin123")
        cur.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES ('admin', ?, 'admin@sistema.com', 'superuser')
        """, (admin_pass,))
        print("✓ Usuario admin creado (usuario: admin, contraseña: admin123)")

    conn.commit()
    conn.close()
    print("✓ Base de datos inicializada correctamente")