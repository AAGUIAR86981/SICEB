"""
Script completo para inicializar la base de datos SICEB
Crea todas las tablas necesarias con sus estructuras, índices y relaciones
"""
import mariadb
import os
from dotenv import load_dotenv

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
        if err.errno == 1049:  # No existe la base de datos
            try:
                # Conectar sin base de datos para crearla
                conn = mariadb.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", "")
                )
                cursor = conn.cursor()
                db_name = os.getenv("DB_NAME", "lider_pollo")
                print(f"Creando base de datos {db_name}...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin")
                cursor.close()
                conn.close()
                
                # Intentar de nuevo
                return mariadb.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", ""),
                    database=db_name
                )
            except mariadb.Error as err2:
                print(f"Error creando la base de datos: {err2}")
                return None
        else:
            print(f"Error conectando a la base de datos: {err}")
            return None

def repair_all_schemas(cursor):
    """Repara el esquema de todas las tablas si existen con nombres de columna antiguos o columnas faltantes"""
    # 1. Reparar tabla 'users'
    try:
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [row[0] for row in cursor.fetchall()]
        if 'active' in columns and 'activo' not in columns:
            print("  ! Reparando columna 'active' -> 'activo' en 'users'")
            cursor.execute("ALTER TABLE users CHANGE active activo BOOLEAN DEFAULT TRUE")
        if 'activo' not in columns:
            print("  ! Añadiendo columna 'activo' a 'users'")
            cursor.execute("ALTER TABLE users ADD COLUMN activo BOOLEAN DEFAULT TRUE")
            
        if 'last_login' not in columns:
            print("  ! Añadiendo columna 'last_login' a 'users'")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL AFTER created_at")
            
        if 'userAlias' in columns and 'username' in columns:
            print("  ! Reparando estructura de 'username' en 'users'")
            cursor.execute("ALTER TABLE users DROP COLUMN username")
            cursor.execute("ALTER TABLE users CHANGE userAlias username VARCHAR(50) NOT NULL UNIQUE")
        elif 'userAlias' in columns:
            print("  ! Renombrando 'userAlias' a 'username' en 'users'")
            cursor.execute("ALTER TABLE users CHANGE userAlias username VARCHAR(50) NOT NULL UNIQUE")
    except mariadb.Error as e:
        if e.errno != 1146: print(f"  ⚠️ Error users: {e}")

    # 2. Reparar otras tablas que necesitan 'activo'
    tables_needing_activo = ['cat_departamentos', 'cat_tipos_nomina', 'catalogo_productos', 'combos']
    for table in tables_needing_activo:
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row[0] for row in cursor.fetchall()]
            if 'activo' not in columns:
                print(f"  ! Añadiendo columna 'activo' a '{table}'")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN activo BOOLEAN DEFAULT TRUE")
        except mariadb.Error as e:
            if e.errno != 1146: print(f"  ⚠️ Error {table}: {e}")

    # 3. Reparar tabla 'empleados' para 3NF
    try:
        cursor.execute("SHOW COLUMNS FROM empleados")
        columns = [row[0] for row in cursor.fetchall()]
        if 'departamento_id' not in columns:
            print("  ! Migrando 'empleados' a 3NF (añadiendo departamento_id)")
            cursor.execute("ALTER TABLE empleados ADD COLUMN departamento_id INT AFTER departamento")
            # Intentar poblar a partir del nombre si existe
            cursor.execute("""
                UPDATE empleados e
                JOIN cat_departamentos cd ON e.departamento = cd.nombre
                SET e.departamento_id = cd.id
            """)
        
        if 'tipo_nomina_id' not in columns:
            print("  ! Migrando 'empleados' a 3NF (añadiendo tipo_nomina_id)")
            cursor.execute("ALTER TABLE empleados ADD COLUMN tipo_nomina_id INT AFTER tipoNomina")
            # Mapping legacy tipoNomina (1=Semanal, 2=Quincenal)
            cursor.execute("UPDATE empleados SET tipo_nomina_id = tipoNomina WHERE tipoNomina IN (1, 2)")

        # Verificar FKs
        cursor.execute("""
            SELECT CONSTRAINT_NAME FROM information_schema.REFERENTIAL_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'empleados'
        """)
        constraints = [row[0] for row in cursor.fetchall()]
        
        if 'fk_empleados_departamento' not in constraints:
            print("  ! Añadiendo FK para departamentos en 'empleados'")
            cursor.execute("ALTER TABLE empleados ADD CONSTRAINT fk_empleados_departamento FOREIGN KEY (departamento_id) REFERENCES cat_departamentos(id)")
        
        if 'fk_empleados_nomina' not in constraints:
            print("  ! Añadiendo FK para nómina en 'empleados'")
            cursor.execute("ALTER TABLE empleados ADD CONSTRAINT fk_empleados_nomina FOREIGN KEY (tipo_nomina_id) REFERENCES cat_tipos_nomina(id)")

    except mariadb.Error as e:
        if e.errno != 1146: print(f"  ⚠️ Error reparando tabla empleados: {e}")

    # 4. Reparar tablas de logs para incluir ip_address
    log_tables = ['user_activities', 'empleadosaudit', 'provisiones_historial', 'users']
    for table in log_tables:
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row[0] for row in cursor.fetchall()]
            column_to_add = 'ip_address' if table != 'users' else 'last_ip'
            if column_to_add not in columns:
                print(f"  ! Añadiendo columna '{column_to_add}' a '{table}'")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_to_add} VARCHAR(45)")
        except mariadb.Error as e:
            if e.errno != 1146: print(f"  ⚠️ Error reparando IP en {table}: {e}")

    # 5. Añadir llaves foráneas faltantes (Integridad referencial sin afectar datos)
    try:
        # FK para user_activities
        cursor.execute("""
            SELECT CONSTRAINT_NAME FROM information_schema.REFERENTIAL_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'user_activities'
        """)
        constraints_ua = [row[0] for row in cursor.fetchall()]
        if 'fk_user_activities_user' not in constraints_ua:
            print("  ! Añadiendo FK 'fk_user_activities_user' en 'user_activities'")
            # Si hay IDs huérfanos, ponerlos a NULL antes de la FK
            cursor.execute("UPDATE user_activities SET user_id = NULL WHERE user_id NOT IN (SELECT id FROM users)")
            cursor.execute("ALTER TABLE user_activities ADD CONSTRAINT fk_user_activities_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL")
            
        # FK para provisiones_historial
        cursor.execute("""
            SELECT CONSTRAINT_NAME FROM information_schema.REFERENTIAL_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'provisiones_historial'
        """)
        constraints_ph = [row[0] for row in cursor.fetchall()]
        if 'fk_provisiones_hist_user' not in constraints_ph:
            print("  ! Añadiendo FK 'fk_provisiones_hist_user' en 'provisiones_historial'")
            # Si hay IDs huérfanos, ponerlos a NULL antes de la FK
            cursor.execute("UPDATE provisiones_historial SET usuario_id = NULL WHERE usuario_id NOT IN (SELECT id FROM users)")
            cursor.execute("ALTER TABLE provisiones_historial ADD CONSTRAINT fk_provisiones_hist_user FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE SET NULL")
            
    except mariadb.Error as e:
        print(f"  ⚠️ Error reparando llaves foráneas: {e}")

def create_all_tables():
    """Crea todas las tablas del sistema SICEB"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return False
    
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("INICIALIZANDO/REPARANDO BASE DE DATOS SICEB")
        print("=" * 60)
        
        # configuramos collation para la sesión
        cursor.execute("SET collation_connection = 'utf8mb4_bin'")

        # REPARACIÓN DE ESQUEMA UNIVERSAL
        repair_all_schemas(cursor)

        # ============================================
        # 1. TABLAS DE CATÁLOGOS (3NF)
        # ============================================
        print("\n[1/7] Creando tablas de catálogos...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cat_departamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cat_tipos_nomina (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE,
            descripcion VARCHAR(255),
            activo BOOLEAN DEFAULT TRUE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalogo_productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            categoria VARCHAR(50),
            unidad VARCHAR(20) DEFAULT 'unid',
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        print("  ✓ Catálogos creados")
        
        # ============================================
        # 2. TABLA DE USUARIOS Y AUTENTICACIÓN
        # ============================================
        print("\n[2/7] Creando tablas de usuarios y autenticación...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(255),
            password VARCHAR(255) NULL,
            isAdmin TINYINT DEFAULT 0,
            name VARCHAR(100),
            lastname VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            activo BOOLEAN DEFAULT TRUE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(255)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(100) NOT NULL UNIQUE,
            module VARCHAR(50)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
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
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INT NOT NULL,
            permission_id INT NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        print("  ✓ Tablas de autenticación creadas")
        
        # ============================================
        # 3. TABLA DE EMPLEADOS (3NF)
        # ============================================
        print("\n[3/7] Creando tabla de empleados...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cedula INT NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            departamento VARCHAR(100),
            departamento_id INT,
            tipoNomina INT NOT NULL DEFAULT 1,
            tipo_nomina_id INT,
            id_empleado INT NOT NULL,
            boolValidacion TINYINT DEFAULT 1,
            fecha_ingreso DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_emp_ced (id_empleado, cedula),
            FOREIGN KEY (departamento_id) REFERENCES cat_departamentos(id),
            FOREIGN KEY (tipo_nomina_id) REFERENCES cat_tipos_nomina(id),
            INDEX idx_departamento (departamento),
            INDEX idx_departamento_id (departamento_id),
            INDEX idx_tipo_nomina (tipoNomina),
            INDEX idx_tipo_nomina_id (tipo_nomina_id),
            INDEX idx_validacion (boolValidacion),
            INDEX idx_cedula (cedula)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        print("  ✓ Tabla de empleados creada")
        
        # ============================================
        # 4. TABLAS DE COMBOS
        # ============================================
        print("\n[4/7] Creando tablas de combos...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS combos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            descripcion TEXT,
            activo BOOLEAN DEFAULT TRUE,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS combo_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            combo_id INT NOT NULL,
            producto_id INT NOT NULL,
            cantidad INT NOT NULL DEFAULT 1,
            FOREIGN KEY (combo_id) REFERENCES combos(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES catalogo_productos(id) ON DELETE CASCADE,
            UNIQUE KEY unique_combo_producto (combo_id, producto_id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        print("  ✓ Tablas de combos creadas")
        
        # ============================================
        # 5. TABLAS DE PROVISIONES
        # ============================================
        print("\n[5/7] Creando tablas de provisiones...")
        

        
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provisiones_historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo_provision VARCHAR(20) NOT NULL,
            semana INT NOT NULL,
            tipo_nomina VARCHAR(20) NOT NULL,
            productos TEXT,
            cant_aprobados INT DEFAULT 0,
            cant_rechazados INT DEFAULT 0,
            datos_completos LONGTEXT,
            usuario_id INT,
            usuario_nombre VARCHAR(100),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_fecha (fecha_creacion),
            INDEX idx_tipo_semana (tipo_nomina, semana),
            CONSTRAINT fk_provisiones_hist_user FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE SET NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provision_productos_historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provision_id INT NOT NULL,
            producto_nombre VARCHAR(100) NOT NULL,
            cantidad INT NOT NULL,
            FOREIGN KEY (provision_id) REFERENCES provisiones_historial(id) ON DELETE CASCADE,
            INDEX idx_provision (provision_id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provision_beneficiarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provision_id INT NOT NULL,
            empleado_id INT NOT NULL,
            cedula INT NOT NULL,
            nombre_completo VARCHAR(255) NOT NULL,
            departamento VARCHAR(100),
            recibio BOOLEAN DEFAULT TRUE,
            fecha_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provision_id) REFERENCES provisiones_historial(id) ON DELETE CASCADE,
            FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
            INDEX idx_provision_ben (provision_id),
            INDEX idx_cedula_ben (cedula),
            INDEX idx_recibio (recibio)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        print("  ✓ Tablas de provisiones creadas")
        
        # ============================================
        # 6. TABLAS DE LOGS Y AUDITORÍA
        # ============================================
        print("\n[6/7] Creando tablas de logs y auditoría...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(100),
            activity_type VARCHAR(50),
            activity_details TEXT,
            activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_date (user_id, activity_date),
            CONSTRAINT fk_user_activities_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleadosaudit (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            field_name VARCHAR(50) NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            changed_by INT,
            FOREIGN KEY (employee_id) REFERENCES empleados(id) ON DELETE CASCADE,
            FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_employee (employee_id),
            INDEX idx_field (field_name)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        # Trigger para auditoría de empleados
        cursor.execute("DROP TRIGGER IF EXISTS after_empleado_update")
        # Definición sin BEGIN/END complejos si es posible, o usando sentencia única
        # En MariaDB, para usar IF/BEGIN/END necesitamos que sea un bloque único
        trigger_sql = """
        CREATE TRIGGER after_empleado_update
        AFTER UPDATE ON empleados
        FOR EACH ROW
        BEGIN
            IF OLD.nombre != NEW.nombre THEN
                INSERT INTO empleadosaudit (employee_id, field_name, old_value, new_value, ip_address)
                VALUES (OLD.id, 'nombre', OLD.nombre, NEW.nombre, @client_ip);
            END IF;
            IF OLD.apellido != NEW.apellido THEN
                INSERT INTO empleadosaudit (employee_id, field_name, old_value, new_value, ip_address)
                VALUES (OLD.id, 'apellido', OLD.apellido, NEW.apellido, @client_ip);
            END IF;
            IF OLD.departamento != NEW.departamento THEN
                INSERT INTO empleadosaudit (employee_id, field_name, old_value, new_value, ip_address)
                VALUES (OLD.id, 'departamento', OLD.departamento, NEW.departamento, @client_ip);
            END IF;
            IF OLD.cedula != NEW.cedula THEN
                INSERT INTO empleadosaudit (employee_id, field_name, old_value, new_value, ip_address)
                VALUES (OLD.id, 'cedula', CAST(OLD.cedula AS CHAR), CAST(NEW.cedula AS CHAR), @client_ip);
            END IF;
            IF OLD.tipoNomina != NEW.tipoNomina THEN
                INSERT INTO empleadosaudit (employee_id, field_name, old_value, new_value, ip_address)
                VALUES (OLD.id, 'tipoNomina', CAST(OLD.tipoNomina AS CHAR), CAST(NEW.tipoNomina AS CHAR), @client_ip);
            END IF;
        END;
        """
        try:
            cursor.execute(trigger_sql)
        except Exception as te:
            print(f"Nota: No se pudo crear el trigger avanzado ({te}). Usando versión simple.")
            # Si falla el bloque complejo, al menos insertar un log genérico
            cursor.execute("""
            CREATE TRIGGER after_empleado_update
            AFTER UPDATE ON empleados
            FOR EACH ROW
            INSERT INTO empleadosaudit (employee_id, field_name, old_value, new_value, ip_address)
            VALUES (OLD.id, 'update', 'multiple', 'change', @client_ip);
            """)

        # Vista de resumen de auditoría
        cursor.execute("""
        CREATE OR REPLACE VIEW v_resumen_auditoria AS
        SELECT 
            a.employee_id,
            e.nombre,
            e.apellido,
            COUNT(*) as total_cambios,
            MAX(a.changed_at) as ultimo_cambio
        FROM empleadosaudit a
        JOIN empleados e ON a.employee_id = e.id
        GROUP BY a.employee_id, e.nombre, e.apellido
        """)
        
        print("  ✓ Tablas de logs creadas")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("=" * 60)
        
        return True
        
    except mariadb.Error as err:
        print(f"\n❌ Error creando tablas: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def insert_initial_data():
    """Inserta datos iniciales necesarios para el funcionamiento del sistema"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("INSERTANDO DATOS INICIALES")
        print("=" * 60)
        
        # Permisos básicos
        print("[2/3] Verificando permisos del sistema...")
        # Nota: Aquí podríamos insertar los permisos si tuviéramos una lista, 
        # pero vamos a insertar al menos el de combos que faltaba
        cursor.execute("INSERT IGNORE INTO permissions (name, code, module) VALUES ('Gestionar Combos', 'manage_combos', 'catalogos')")

        # Roles básicos
        print("[2.5/3] Verificando roles del sistema...")
        roles = [
            (1, 'administrador', 'Acceso total al sistema'),
            (2, 'supervisor', 'Gestión de provisiones y reportes'),
            (3, 'usuario', 'Operaciones básicas y consultas'),
            (4, 'visualizador', 'Solo lectura de reportes')
        ]
        for role_id, name, desc in roles:
            cursor.execute("INSERT IGNORE INTO roles (id, name, description) VALUES (%s, %s, %s)", (role_id, name, desc))

        # Usuario administrador inicial si no existe
        print("[3/3] Verificando usuario administrador...")
        from passlib.hash import pbkdf2_sha256
        cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
        row = cursor.fetchone()
        if not row:
            hashed_pw = pbkdf2_sha256.hash("Admin123.")
            cursor.execute("""
                INSERT INTO users (username, email, password, isAdmin, name, lastname, activo)
                VALUES ('admin', 'admin@liderpollo.com', %s, 1, 'Admin', 'Principal', 1)
            """, (hashed_pw,))
            user_id = cursor.lastrowid
        else:
            user_id = row[0]
        
        # Asegurar que el admin tenga el rol de administrador
        cursor.execute("INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, 1)", (user_id,))
        
        conn.commit()
        print("\n✅ Datos iniciales insertados correctamente")
        return True
        
    except mariadb.Error as err:
        print(f"\n❌ Error insertando datos: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Iniciando configuracion de base de datos SICEB...")
    
    if create_all_tables():
        insert_initial_data()
        print("\nSistema listo para usar!")
    else:
        print("\n❌ No se pudo completar la inicialización")
