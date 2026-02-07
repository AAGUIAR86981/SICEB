from datetime import datetime
from config.database import get_db_connection

def dateformat(value, format="%d/%m/%Y"):
    """Filtro personalizado para formato de fecha (igual que en tu código original)"""
    if value is None:
        return ""

    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return value

    if isinstance(value, datetime):
        return value.strftime(format)

    return value

import json
def from_json(value):
    """Convierte una cadena JSON a un objeto Python"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

def log_user_activity(user_id, username, activity_type, activity_details):
    """Registra actividades de usuario (igual que en tu código original)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Si user_id es None, intentar obtenerlo de la base de datos
        if user_id is None and username:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_id = user_data[0]

        # Insertar la actividad
        cursor.execute(
            'INSERT INTO user_activities (user_id, username, activity_type, activity_details) VALUES (%s, %s, %s, %s)',
            (user_id, username, activity_type, activity_details)
        )
        conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
