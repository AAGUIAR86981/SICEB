
import os
import mariadb
from dotenv import load_dotenv

def test_connection():
    load_dotenv()
    
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = int(os.getenv("DB_PORT", 3306))
    
    result = []
    
    # Test 1: Connect as configured
    try:
        conn = mariadb.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        result.append(f"Test 1 (Configured): SUCCESS. Connected as {user}")
        conn.close()
    except Exception as e:
        result.append(f"Test 1 (Configured): FAILED. Error: {e}")

    # Test 2: Connect with empty password (common for root)
    if password:
        try:
            conn = mariadb.connect(
                host=host,
                user=user,
                password="",
                port=port
            )
            result.append(f"Test 2 (Empty Password): SUCCESS. Connected as {user}")
            conn.close()
        except Exception as e:
            result.append(f"Test 2 (Empty Password): FAILED. Error: {e}")

    # Test 3: Common passwords

    common_passwords = ["root", "1234", "123456", "password", "admin123", "Admin123."]
    for pwd in common_passwords:
        try:
            conn = mariadb.connect(
                host=host,
                user=user,
                password=pwd,
                port=port
            )
            result.append(f"Test 3 (Password '{pwd}'): SUCCESS. Connected as {user}")
            conn.close()
            break # Stop if found
        except Exception as e:
            pass # Keep trying


    with open("connection_result.txt", "w") as f:
        f.write("\n".join(result))

if __name__ == "__main__":
    test_connection()
