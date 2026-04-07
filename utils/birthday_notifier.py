from config.database import get_db_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging
import requests

# Sistema de Notificaciones de Cumpleaños: Para que nadie se quede sin su felicitación
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_birthdays_today():
    """Busca en la base de datos a los empleados que están de fiesta hoy"""
    conn = get_db_connection()
    if not conn:
        logging.error("No pudimos conectar con la base de datos para ver los cumpleaños.")
        return []
    
    cursor = conn.cursor()
    employees = []
    try:
        # Buscamos a los trabajadores cuya fecha de nacimiento coincida con el día y mes actual
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
        logging.error(f"Error al intentar leer la lista de cumpleañeros: {e}")
    finally:
        conn.close()
    
    return employees

def send_birthday_email(employee):
    """Prepara y envía un correo electrónico bonito deseando un feliz cumpleaños"""
    sender_email = os.getenv("MAIL_USERNAME") 
    sender_password = os.getenv("MAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        logging.warning("No podemos enviar correos porque faltan las credenciales en el archivo .env")
        return

    if not employee.get('email'):
        logging.warning(f"El cumpleañero {employee['nombre']} no tiene un correo registrado.")
        return

    subject = "¡Feliz Cumpleaños!"
    body = f"""
    Hola {employee['nombre']},
    
    ¡Desde Lider Pollo queremos desearte un muy feliz cumpleaños!
    Esperamos que pases un día excelente junto a tus seres queridos y que este nuevo año de vida venga cargado de éxitos.
    
    Atentamente,
    El equipo de Recursos Humanos.
    """

    # Configuramos el mensaje con el remitente, destinatario y el asunto
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = employee['email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Usamos el servidor de correo configurado o el de Gmail por defecto
        smtp_host = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("MAIL_PORT", 587))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls() # Seguridad para la conexión
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, employee['email'], msg.as_string())
        server.quit()
        logging.info(f"Correo de felicitación enviado con éxito a {employee['nombre']}.")
    except Exception as e:
        logging.error(f"No pudimos enviar el correo a {employee['email']}: {e}")

def send_whatsapp_alert(employee):
    """Simula el envío de un mensaje de WhatsApp para felicitar al trabajador"""
    if not employee.get('telefono'):
        logging.warning(f"No tenemos el número de teléfono de {employee['nombre']} para enviarle el WhatsApp.")
        return

    message = f"¡Feliz Cumpleaños {employee['nombre']}! Te desea Lider Pollo. 🎂🎉"
    
    # Por ahora solo lo registramos en el sistema, ya que requiere una API de pago para enviarse de verdad
    logging.info(f"[WHATSAPP SIMULADO] Se enviaría a {employee['telefono']}: {message}")

def run_daily_birthday_check():
    """Esta es la función principal que se debe correr todos los días para felicitar al personal"""
    print("--- Iniciando el proceso diario de felicitaciones ---")
    birthdays = get_birthdays_today()
    if not birthdays:
        print("Hoy no hay ningún trabajador de cumpleaños.")
        return

    print(f"¡Qué alegría! Encontramos a {len(birthdays)} personas cumpliendo años hoy.")
    for emp in birthdays:
        print(f"Felicitando a: {emp['nombre']} {emp['apellido']}")
        send_birthday_email(emp)
        send_whatsapp_alert(emp)
    print("--- Proceso terminado con éxito ---")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Cargamos las configuraciones si lo corremos manualmente
    run_daily_birthday_check()
