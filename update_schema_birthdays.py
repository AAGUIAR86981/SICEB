from config.database import get_db_connection

def update_schema():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    cursor = conn.cursor()
    try:
        print("Checking/Updating schema for 'empleados'...")
        
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM empleados LIKE 'fecha_nacimiento'")
        if not cursor.fetchone():
            print("Adding fecha_nacimiento...")
            cursor.execute("ALTER TABLE empleados ADD COLUMN fecha_nacimiento DATE NULL")
        else:
            print("fecha_nacimiento already exists.")

        cursor.execute("SHOW COLUMNS FROM empleados LIKE 'email'")
        if not cursor.fetchone():
            print("Adding email...")
            cursor.execute("ALTER TABLE empleados ADD COLUMN email VARCHAR(100) NULL")
        else:
            print("email already exists.")

        cursor.execute("SHOW COLUMNS FROM empleados LIKE 'telefono'")
        if not cursor.fetchone():
            print("Adding telefono...")
            cursor.execute("ALTER TABLE empleados ADD COLUMN telefono VARCHAR(20) NULL")
        else:
            print("telefono already exists.")

        conn.commit()
        print("Schema updated successfully.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
