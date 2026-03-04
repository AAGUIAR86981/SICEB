import mariadb
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_db_connection():
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "lider_pollo")
        )
        return connection
    except mariadb.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_tables():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        print("Creating Authentication Tables...")
        
        # 1. Roles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(255)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        # 2. Permissions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(100) NOT NULL UNIQUE,
            module VARCHAR(50)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        # 3. User Roles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INT NOT NULL,
            role_id INT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        # 4. Role Permissions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INT NOT NULL,
            permission_id INT NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        print("Creating Provision Tables (Normalized)...")



        conn.commit()
        print("  Tables created successfully.")

    except mariadb.Error as err:
        print(f"  Error creating tables: {err}")
    finally:
        cursor.close()
        conn.close()

def migrate_auth_data():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        print("Migrating Auth Data...")

        # 1. Insert Default Roles
        roles = [
            ('administrador', 'Acceso total al sistema'),
            ('supervisor', 'Gestión de provisiones y empleados'),
            ('visualizador', 'Solo lectura de reportes'),
            ('usuario', 'Usuario estándar')
        ]
        
        for role_name, desc in roles:
            try:
                cursor.execute("INSERT INTO roles (name, description) VALUES (%s, %s)", (role_name, desc))
            except mariadb.IntegrityError:
                pass # Already exists

        conn.commit()

        # 2. Get Roles IDs
        cursor.execute("SELECT id, name FROM roles")
        role_map = {name: id for id, name in cursor.fetchall()}

        # 3. Migrate Users (isAdmin -> Role)
        cursor.execute("SELECT id, isAdmin FROM users")
        users = cursor.fetchall()

        for user_id, is_admin in users:
            role_id = role_map['administrador'] if is_admin == 1 else role_map['usuario']
            
            # Check if assignment exists
            cursor.execute("SELECT 1 FROM user_roles WHERE user_id = %s AND role_id = %s", (user_id, role_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, role_id))

        conn.commit()
        print("  Auth data migrated successfully.")

    except mariadb.Error as err:
        print(f"  Error migrating auth data: {err}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_tables()
    migrate_auth_data()
