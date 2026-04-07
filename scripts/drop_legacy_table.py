import mariadb
import os
from dotenv import load_dotenv

load_dotenv()

def drop_table():
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "lider_pollo")
        )
        cursor = connection.cursor()
        print("Dropping table provision_configs...")
        cursor.execute("DROP TABLE IF EXISTS provision_configs;")
        connection.commit()
        print("Table dropped successfully.")
    except mariadb.Error as err:
        print(f"Error connecting to database: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    drop_table()
