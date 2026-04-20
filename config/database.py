import pymysql
from passlib.hash import pbkdf2_sha256
import os
from dotenv import load_dotenv

# Conexión Central: Aquí configuramos el acceso al 'cerebro' del sistema (la base de datos MariaDB)
load_dotenv()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error de conexion: {e}")
        return None

def init_db_tables():
    """Prepara todas las estanterías (tablas) vacías para empezar a guardar información"""
    from init_database import create_all_tables, insert_initial_data
    # Creamos las tablas y de una vez insertamos los datos iniciales (como el usuario administrador)
    if create_all_tables():
        insert_initial_data()
