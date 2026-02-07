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

        # 5. Provision Configs (Header)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provision_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            week_number VARCHAR(50) NOT NULL,
            provision_type ENUM('semanal', 'quincenal') NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        # 6. Provision Items (Details)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provision_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provision_config_id INT NOT NULL,
            product_name VARCHAR(100) NOT NULL,
            quantity INT NOT NULL,
            FOREIGN KEY (provision_config_id) REFERENCES provision_configs(id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

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

def normalize_provisions():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        print("Normalizing Provisions...")

        # 1. Semanal
        try:
            cursor.execute("SELECT * FROM semana_provision")
            rows = cursor.fetchall()
            
            # Get columns to find rubro/cant indices (assuming standard order or fetching metadata would be safer, 
            # but for this script we'll assume the structure from config/database.py:
            # id, semana, rubro1, cant1, rubro2, cant2... up to 5
            
            # Let's use metadata to be safe
            cursor.execute("SHOW COLUMNS FROM semana_provision")
            cols = [col[0].lower() for col in cursor.fetchall()]
            
            for row in rows:
                week_val = row[1] # semana
                
                # Check if already exists to avoid dupes on re-run
                cursor.execute("SELECT id FROM provision_configs WHERE week_number=%s AND provision_type='semanal'", (week_val,))
                if cursor.fetchone():
                    continue

                # Create Config
                cursor.execute("INSERT INTO provision_configs (week_number, provision_type, active) VALUES (%s, 'semanal', TRUE)", (week_val,))
                config_id = cursor.lastrowid
                
                # Iterate columns to find pairs
                # This is a bit hacky but works for the specific known schema
                # Model logic was dynamic, here we can be a bit more prescriptive or dynamic too.
                # Let's rely on fixed indices based on the CREATE TABLE statement in database.py
                # 0:id, 1:semana, 2:rubro1, 3:cant1, 4:rubro2, 5:cant2...
                
                for i in range(1, 6): # 5 pairs
                    rubro_idx = 2 + (i-1)*2
                    cant_idx = 3 + (i-1)*2
                    
                    if rubro_idx < len(row) and cant_idx < len(row):
                        rubro = row[rubro_idx]
                        cant = row[cant_idx]
                        
                        if rubro and cant is not None:
                            cursor.execute("INSERT INTO provision_items (provision_config_id, product_name, quantity) VALUES (%s, %s, %s)", 
                                         (config_id, rubro, cant))
                            
        except mariadb.Error as e:
            print(f"  Could not read semana_provision (maybe doesn't exist): {e}")


        # 2. Quincenal
        try:
            cursor.execute("SELECT * FROM semana_provision_quincenal")
            rows = cursor.fetchall()
            
            for row in rows:
                week_val = row[1] # semana

                # Check if already exists
                cursor.execute("SELECT id FROM provision_configs WHERE week_number=%s AND provision_type='quincenal'", (week_val,))
                if cursor.fetchone():
                    continue
                
                # Create Config
                cursor.execute("INSERT INTO provision_configs (week_number, provision_type, active) VALUES (%s, 'quincenal', TRUE)", (week_val,))
                config_id = cursor.lastrowid
                
                # Indices: 0:id, 1:semana, 2:producto1, 3:cantidad1...
                for i in range(1, 6): # 5 pairs
                    prod_idx = 2 + (i-1)*2
                    cant_idx = 3 + (i-1)*2
                    
                    if prod_idx < len(row) and cant_idx < len(row):
                        prod = row[prod_idx]
                        cant = row[cant_idx]
                        
                        if prod and cant is not None:
                            cursor.execute("INSERT INTO provision_items (provision_config_id, product_name, quantity) VALUES (%s, %s, %s)", 
                                         (config_id, prod, cant))

        except mariadb.Error as e:
            print(f"  Could not read semana_provision_quincenal: {e}")

        conn.commit()
        print("  Provisions normalized successfully.")

    except mariadb.Error as err:
        print(f"  Error normalizing provisions: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
    migrate_auth_data()
    normalize_provisions()
