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
        port=int(os.getenv("DB_PORT", 3306)),
cursorclass=pymysql.cursors.DictCursor
    )
         return connection
    except pymysql.MySQLError as err:
        # LOGICA DE EMERGENCIA corregida para PyMySQL
        print(f"Error conectando: {err}")
        # Si el error es que la base de datos no existe (1049)
        if err.args[0] == 1049:
            # Aquí podrías poner la lógica para crearla, 
            # pero en Railway la base de datos ya viene creada.
            pass
        raise err

                # Ahora que ya existe, nos conectamos formalmente a ella
                connection =pymysql.connect((
                    host=os.getenv('DB_HOST'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME'),
                    port=int(os.getenv("DB_PORT", 3306))
                )
                return connection
            except pymysql.MySQLError as err:
        print(f"No pudimos conectar o crear la base de datos: {err}")
        # En Railway, la DB se crea desde el panel, así que aquí solo lanzamos el error
        raise err
    else:
        # Si la conexión fue exitosa, la devolvemos
        return connection
            raise

def init_db_tables():
    """Prepara todas las estanterías (tablas) vacías para empezar a guardar información"""
    from init_database import create_all_tables, insert_initial_data
    # Creamos las tablas y de una vez insertamos los datos iniciales (como el usuario administrador)
    if create_all_tables():
        insert_initial_data()
