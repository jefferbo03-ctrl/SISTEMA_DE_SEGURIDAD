# Sistema de Alerta Temprana para Vencimientos

Sistema completo de gestión y notificación automática para el vencimiento de especializaciones, cursos y certificaciones.

## ✨ Características

- 🔐 **Autenticación de usuarios** con roles (Super Usuario, Admin, Usuario)
- 📊 **Dashboard** con estadísticas y alertas visuales
- 👥 **Gestión de personas** (CRUD completo)
- 📤 **Importación masiva** desde archivos Excel
- 📧 **Notificaciones por email** automáticas
- 📱 **Notificaciones por SMS** (Twilio)
- ⏰ **Chequeos automáticos** diarios programados
- 🔍 **Búsqueda y filtros** avanzados
- 🌍 **Soporte de zonas horarias**

## 🚀 Instalación

### 1. Requisitos previos

- Python 3.8 o superior
- pip

### 2. Clonar o descargar el proyecto

```bash
# Si usas git
git clone <tu-repositorio>
cd sistema-alerta
```

### 3. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto copiando `.env.example`:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus datos:

```env
SECRET_KEY=tu-clave-secreta-aqui
TIMEZONE=America/Bogota
ALERT_DAYS=60,30,15,7,1,0

# Email (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=tu-email@gmail.com

# SMS (Twilio) - Opcional
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_FROM_PHONE=+1234567890
```

#### Configurar Gmail para enviar emails:

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Activa la verificación en 2 pasos
3. Ve a "App Passwords": https://myaccount.google.com/apppasswords
4. Genera una contraseña para "Mail"
5. Usa esa contraseña en `SMTP_PASSWORD`

### 6. Inicializar la base de datos

```bash
python -c "from db import init_db; init_db()"
```

### 7. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

## 🔑 Usuario por defecto

- **Usuario:** admin
- **Contraseña:** admin123

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login.

## 📋 Estructura del proyecto

```
sistema-alerta/
├── app.py                 # Aplicación principal Flask
├── db.py                  # Gestión de base de datos
├── notify.py              # Sistema de notificaciones
├── importer.py            # Importador de Excel
├── requirements.txt       # Dependencias
├── .env                   # Configuración (crear desde .env.example)
├── alerta.db             # Base de datos SQLite (se crea automáticamente)
├── uploads/              # Carpeta para archivos subidos
└── templates/            # Templates HTML
    ├── base.html
    ├── login.html
    ├── index.html
    ├── add_edit.html
    ├── upload.html
    ├── users.html
    ├── add_edit_user.html
    └── settings.html
```

## 👤 Roles de usuario

### Super Usuario
- Acceso completo al sistema
- Gestión de usuarios
- Todas las funciones de Admin

### Admin
- Gestión de personas (crear, editar, eliminar)
- Carga masiva de datos
- Ejecutar chequeos manuales
- Ver configuración

### Usuario
- Solo visualización de la lista de personas
- Ver estadísticas

## 📊 Formato del Excel

El archivo Excel debe contener las siguientes columnas:

| Columna | Tipo | Obligatorio | Ejemplo |
|---------|------|-------------|---------|
| nombre | Texto | Sí | Juan |
| apellido | Texto | Sí | Pérez |
| especializacion | Texto | Sí | Vigilante |
| fecha_expedicion | Fecha | No | 2023-01-15 o 15/01/2023 |
| fecha_vencimiento | Fecha | Sí | 2025-01-15 o 15/01/2025 |
| escuela | Texto | No | Escuela de Seguridad |
| empresa | Texto | No | Empresa XYZ |
| email | Email | No | juan@example.com |
| celular | Texto | No | +57 300 123 4567 |

### Formatos de fecha aceptados:
- `YYYY-MM-DD` (2025-01-15)
- `DD/MM/YYYY` (15/01/2025)
- `DD-MM-YYYY` (15-01-2025)

## 📧 Notificaciones

El sistema envía notificaciones automáticas:

- **Automáticas:** Todos los días a las 8:00 AM
- **Manuales:** Desde el panel de administración

Las notificaciones se envían cuando faltan:
- 60 días
- 30 días
- 15 días
- 7 días
- 1 día
- 0 días (día del vencimiento)

Puedes personalizar estos días en el archivo `.env` con la variable `ALERT_DAYS`.

## 🔧 Personalización

### Cambiar días de alerta

Edita en `.env`:
```env
ALERT_DAYS=90,60,30,15,7,3,1,0
```

### Cambiar hora del chequeo automático

Edita en `app.py`, función `start_scheduler()`:
```python
trigger = CronTrigger(hour=8, minute=0)  # Cambiar hora y minuto
```

### Cambiar zona horaria

Edita en `.env`:
```env
TIMEZONE=America/Bogota
```

Zonas horarias disponibles: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## 🐛 Solución de problemas

### Error al enviar emails

1. Verifica que las credenciales SMTP sean correctas
2. Si usas Gmail, asegúrate de usar una "App Password"
3. Revisa que el puerto sea 587 para TLS

### Error al importar Excel

1. Verifica que el archivo sea .xlsx
2. Asegúrate de que tenga las columnas requeridas
3. Verifica que las fechas estén en formato válido

### Base de datos bloqueada

Si ves errores de base de datos bloqueada, reinicia la aplicación.

## 📝 Licencia

Este proyecto es de uso libre para fines educativos y comerciales.

## 🤝 Soporte

Para reportar bugs o solicitar features, por favor crea un issue en el repositorio.

---

Desarrollado con ❤️ para la gestión eficiente de vencimientos