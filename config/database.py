import mariadb
from passlib.hash import pbkdf2_sha256
import os
from dotenv import load_dotenv

load_dotenv()


# CONEXIÓN DE LA BASE DE DATOS Y VERIFICACION
def get_db_connection():
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except mariadb.Error as err:
        if err.errno == 1049:  # Database doesn't exist
            try:
                # Try connecting without database to create it
                connection = mariadb.connect(
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                )
                cursor = connection.cursor()
                # Sanitize DB_NAME to avoid SQL injection, though unlikely from env
                db_name = os.getenv("DB_NAME")
                if not db_name:
                    raise ValueError("DB_NAME not set in environment")
                
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin")
                cursor.close()
                connection.close()

                connection = mariadb.connect(
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    database=os.getenv("DB_NAME")
                )
                return connection
            except mariadb.Error as err:
                print(f"Error creating database: {err}")
                raise
        else:
            raise


# Creacion de las TABLAS DE LA BASE DE DATOS
def init_db_tables():
    """Inicializa las tablas usando el script consolidado"""
    from init_database import create_all_tables, insert_initial_data
    if create_all_tables():
        insert_initial_data()
