from config.database import get_db_connection

def check_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM provisiones_historial")
        columns = cursor.fetchall()
        print("Columns in provisiones_historial:")
        for col in columns:
            print(f"  {col[0]} ({col[1]})")

        print("-" * 20)

        cursor.execute("SHOW COLUMNS FROM prov_logs")
        columns = cursor.fetchall()
        print("Columns in prov_logs:")
        for col in columns:
            print(f"  {col[0]} ({col[1]})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_schema()
