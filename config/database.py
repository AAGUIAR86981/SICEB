import pymysql
from passlib.hash import pbkdf2_sha256
import os
from dotenv import load_dotenv

# Conexión Central: Aquí configuramos el acceso al 'cerebro' del sistema (la base de datos MariaDB)
load_dotenv()

def get_connection():
    # Railway nos da la DATABASE_URL, pero si prefieres desglosarla:
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv("DB_PORT", 3306))
    )

          # return connection
    except mariadb.Error as err:
        # LOGICA DE EMERGENCIA: Si la base de datos no existe (Error 1049), intentamos crearla automáticamente
        if err.errno == 1049:
            try:
                # Nos conectamos al servidor sin especificar base de datos para poder crearla desde cero
                connection = mariadb.connect(
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                )
                cursor = connection.cursor()
                db_name = os.getenv("DB_NAME")
                if not db_name:
                    raise ValueError("Falta definir DB_NAME en el archivo .env")
                
                # Creamos la base de datos con soporte para caracteres especiales (emojis, tildes, etc.)
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin")
                cursor.close()
                connection.close()

                # Ahora que ya existe, nos conectamos formalmente a ella
                connection = mariadb.connect(
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    database=os.getenv("DB_NAME")
                )
                return connection
            except mariadb.Error as err:
                print(f"No pudimos crear la base de datos automáticamente: {err}")
                raise
        else:
            raise

def init_db_tables():
    """Prepara todas las estanterías (tablas) vacías para empezar a guardar información"""
    from init_database import create_all_tables, insert_initial_data
    # Creamos las tablas y de una vez insertamos los datos iniciales (como el usuario administrador)
    if create_all_tables():
        insert_initial_data()
