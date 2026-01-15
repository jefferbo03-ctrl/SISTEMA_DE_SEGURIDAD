import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

def send_email(to_email: str, subject: str, body: str):
    """
    Envía un correo electrónico usando SMTP
    Configurar las siguientes variables de entorno:
    - SMTP_HOST (ej: smtp.gmail.com)
    - SMTP_PORT (ej: 587)
    - SMTP_USER (tu email)
    - SMTP_PASSWORD (tu contraseña o app password)
    - FROM_EMAIL (email remitente)
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", smtp_user)

    if not smtp_user or not smtp_password:
        print("⚠ Credenciales SMTP no configuradas. No se puede enviar email.")
        return

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"✓ Email enviado a {to_email}")
    except Exception as e:
        print(f"✗ Error enviando email a {to_email}: {e}")
        raise

def send_sms(to_phone: str, message: str):
    """
    Envía un SMS usando Twilio
    Configurar las siguientes variables de entorno:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_FROM_PHONE (número de Twilio)
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_FROM_PHONE")

    if not account_sid or not auth_token or not from_phone:
        print("⚠ Credenciales Twilio no configuradas. No se puede enviar SMS.")
        return

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        print(f"✓ SMS enviado a {to_phone} (SID: {msg.sid})")
    except Exception as e:
        print(f"✗ Error enviando SMS a {to_phone}: {e}")
        raise