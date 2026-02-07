from config.database import get_db_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_birthdays_today():
    """
    Busca empleados que cumplen años hoy.
    Retorna una lista de diccionarios con info del empleado.
    """
    conn = get_db_connection()
    if not conn:
        logging.error("No hay conexión a la base de datos.")
        return []
    
    cursor = conn.cursor()
    employees = []
    try:
        # MYSQL/MariaDB query para comparar mes y día con la fecha actual
        query = """
            SELECT nombre, apellido, email, telefono 
            FROM empleados 
            WHERE fecha_nacimiento IS NOT NULL 
            AND MONTH(fecha_nacimiento) = MONTH(CURRENT_DATE())
            AND DAY(fecha_nacimiento) = DAY(CURRENT_DATE())
            AND boolValidacion = 1
        """
        cursor.execute(query)
        result = cursor.fetchall()
        
        for row in result:
             employees.append({
                 'nombre': row[0],
                 'apellido': row[1],
                 'email': row[2],
                 'telefono': row[3]
             })
    except Exception as e:
        logging.error(f"Error obteniendo cumpleaños: {e}")
    finally:
        conn.close()
    
    return employees

def send_birthday_email(employee):
    """
    Envía correo de cumpleaños usando SMTP.
    Requiere configurar MAIL_USERNAME y MAIL_PASSWORD en .env
    """
    sender_email = os.getenv("MAIL_USERNAME") 
    sender_password = os.getenv("MAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        logging.warning("Faltan credenciales de correo en .env (MAIL_USERNAME, MAIL_PASSWORD)")
        return

    if not employee.get('email'):
        logging.warning(f"El empleado {employee['nombre']} no tiene email registrado.")
        return

    subject = "¡Feliz Cumpleaños!"
    body = f"""
    Hola {employee['nombre']},
    
    ¡Desde Lider Pollo queremos desearte un muy feliz cumpleaños!
    Esperamos que pases un día excelente junto a tus seres queridos.
    
    Atentamente,
    El equipo de RRHH.
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = employee['email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Configuración por defecto para Gmail (port 587)
        # Si usas otro proveedor (Outlook, cPanel), cambia el host y puerto.
        smtp_host = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("MAIL_PORT", 587))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, employee['email'], text)
        server.quit()
        logging.info(f"Email enviado a {employee['nombre']} ({employee['email']})")
    except Exception as e:
        logging.error(f"Error enviando email a {employee['email']}: {e}")

def send_whatsapp_alert(employee):
    """
    Envía mensaje de WhatsApp.
    NOTA: Para WhatsApp automatizado real se requiere la API de Meta (paga/compleja) 
    o servicios de terceros como Twilio o CallMeBot.
    
    Aquí simularemos el envío o usaremos una API simple si se configura.
    """
    if not employee.get('telefono'):
        logging.warning(f"El empleado {employee['nombre']} no tiene teléfono registrado.")
        return

    message = f"¡Feliz Cumpleaños {employee['nombre']}! Te desea Lider Pollo."
    
    # --- LOGICA REAL (Ejemplo con CallMeBot - Servicio Gratuito Personal) ---
    # CallMeBot permite enviar mensajes a ti mismo gratis, o pagando para otros.
    # Twilio es la opción empresarial estándar.
    
    # Por ahora, solo logueamos la acción.
    logging.info(f"[WHATSAPP SIMULADO] Enviando a {employee['telefono']}: {message}")
    
    # Si tuvieras una API Key, aquí harías:
    # requests.post("https://api.whatsapp...", data={...})

def run_daily_birthday_check():
    print("--- Iniciando Chequeo de Cumpleaños ---")
    birthdays = get_birthdays_today()
    if not birthdays:
        print("No hay cumpleaños hoy.")
        return

    print(f"¡Se encontraron {len(birthdays)} cumpleañeros!")
    for emp in birthdays:
        print(f"Procesando: {emp['nombre']} {emp['apellido']}")
        send_birthday_email(emp)
        send_whatsapp_alert(emp)
    print("--- Finalizado ---")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Cargar variables de entorno si se corre manual
    run_daily_birthday_check()
