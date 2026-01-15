# Configuración General
SECRET_KEY=tu-clave-secreta-aqui-cambiar
TIMEZONE=America/Bogota

# Días de Alerta (separados por comas)
# El sistema enviará notificaciones cuando falten estos días para el vencimiento
ALERT_DAYS=60,30,15,7,1,0

# Configuración de Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña-o-app-password
FROM_EMAIL=tu-email@gmail.com

# Configuración de SMS (Twilio) - Opcional
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_FROM_PHONE=+1234567890

# Nota: Para Gmail, necesitas crear una "App Password" desde tu cuenta de Google
# Ve a: https://myaccount.google.com/apppasswords