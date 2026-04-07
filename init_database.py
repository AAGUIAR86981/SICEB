"""
Script de Inicialización SICEB: Este archivo crea toda la base de datos desde cero
Configura las tablas, los permisos de seguridad y el usuario administrador inicial
"""
import mariadb
import os
from dotenv import load_dotenv

# Cargamos los datos del archivo .env para saber cómo conectarnos a MariaDB
load_dotenv()

def get_db_connection():
    """Establece la conexión principal con el servidor de base de datos"""
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
        # Si la base de datos no existe, intentamos entrar al servidor para crearla
        if err.errno == 1049:
            try:
                conn = mariadb.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", "")
                )
                cursor = conn.cursor()
                db_name = os.getenv("DB_NAME", "lider_pollo")
                print(f"La base de datos no existe. Creando {db_name}...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin")
                cursor.close()
                conn.close()
                
                # Una vez creada, volvemos a intentar la conexión normal
                return mariadb.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", ""),
                    database=db_name
                )
            except mariadb.Error as err2:
                print(f"Error crítico: No pudimos crear la base de datos: {err2}")
                return None
        else:
            print(f"Error de conexión: {err}")
            return None

def repair_all_schemas(cursor):
    """Esta función se encarga de 'arreglar' las tablas si son de una versión vieja o les faltan columnas"""
    
    # 1. Aseguramos que la tabla de Usuarios tenga la columna 'activo' y 'last_login'
    try:
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [row[0] for row in cursor.fetchall()]
        if 'active' in columns and 'activo' not in columns:
            print("  ! Cambiando nombre de columna 'active' a 'activo' en Usuarios")
            cursor.execute("ALTER TABLE users CHANGE active activo BOOLEAN DEFAULT TRUE")
        if 'activo' not in columns:
            print("  ! Agregando registro de estado 'activo' a Usuarios")
            cursor.execute("ALTER TABLE users ADD COLUMN activo BOOLEAN DEFAULT TRUE")
            
        if 'last_login' not in columns:
            print("  ! Agregando registro de 'última entrada' a Usuarios")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL AFTER created_at")
            
    except mariadb.Error as e:
        if e.errno != 1146: print(f"  ⚠️ Error en Usuarios: {e}")

    # 2. Nos aseguramos que las tablas de catálogos tengan la opción de activarse/desactivarse
    tables_needing_activo = ['cat_departamentos', 'cat_tipos_nomina', 'catalogo_productos', 'combos']
    for table in tables_needing_activo:
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row[0] for row in cursor.fetchall()]
            if 'activo' not in columns:
                print(f"  ! Agregando columna 'activo' a la tabla {table}")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN activo BOOLEAN DEFAULT TRUE")
        except mariadb.Error as e:
            if e.errno != 1146: print(f"  ⚠️ Error en {table}: {e}")

    # 3. Verificamos que los Empleados estén conectados correctamente con sus departamentos (Normalización 3NF)
    try:
        cursor.execute("SHOW COLUMNS FROM empleados")
        columns = [row[0] for row in cursor.fetchall()]
        if 'departamento_id' not in columns:
            print("  ! Actualizando Empleados para usar identificadores de departamento modernos")
            cursor.execute("ALTER TABLE empleados ADD COLUMN departamento_id INT AFTER departamento")
            # Relacionamos los nombres viejos con los IDs nuevos automáticamente
            cursor.execute("""
                UPDATE empleados e
                JOIN cat_departamentos cd ON e.departamento = cd.nombre
                SET e.departamento_id = cd.id
            """)
        
        if 'tipo_nomina_id' not in columns:
            print("  ! Agregando identificadores modernos para Tipos de Nómina")
            cursor.execute("ALTER TABLE empleados ADD COLUMN tipo_nomina_id INT AFTER tipoNomina")
            # Mapeamos los valores viejos (1 y 2) a la nueva estructura
            cursor.execute("UPDATE empleados SET tipo_nomina_id = tipoNomina WHERE tipoNomina IN (1, 2)")

    except mariadb.Error as e:
        if e.errno != 1146: print(f"  ⚠️ Error reparando tabla de Empleados: {e}")

    # 4. Agregamos registro de dirección IP en todas las bitácoras para saber desde dónde se hicieron los cambios
    log_tables = ['user_activities', 'empleadosaudit', 'provisiones_historial', 'users']
    for table in log_tables:
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row[0] for row in cursor.fetchall()]
            column_to_add = 'ip_address' if table != 'users' else 'last_ip'
            if column_to_add not in columns:
                print(f"  ! Agregando registro de dirección IP a la tabla {table}")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_to_add} VARCHAR(45)")
        except mariadb.Error as e:
            if e.errno != 1146: print(f"  ⚠️ Error de IP en {table}: {e}")

def create_all_tables():
    """Construye todas las piezas del sistema (Tablas) si aún no existen"""
    conn = get_db_connection()
    if not conn:
        print("No se pudo iniciar la creación de tablas por falta de conexión")
        return False
    
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("PREPARANDO EL TERRENO: CREANDO Y REPARANDO TABLAS")
        print("=" * 60)
        
        # Primero arreglamos lo que ya existe si es necesario
        repair_all_schemas(cursor)

        # Creación de catálogos (Departamentos, Nóminas, Productos)
        print("\n[1/5] Creando catálogos de la empresa...")
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
        
        # Creación de Usuarios y Control de Acceso
        print("\n[2/5] Configurando Usuarios y Seguridad...")
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
            last_ip VARCHAR(45),
            activo BOOLEAN DEFAULT TRUE
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        cursor.execute("CREATE TABLE IF NOT EXISTS roles (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) NOT NULL UNIQUE, description VARCHAR(255))")
        cursor.execute("CREATE TABLE IF NOT EXISTS permissions (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, code VARCHAR(100) NOT NULL UNIQUE, module VARCHAR(50))")
        
        # Tablas de relación (qué usuario tiene qué cargo y qué cargo tiene qué permiso)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INT NOT NULL, role_id INT NOT NULL, assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INT NOT NULL, permission_id INT NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        )
        """)
        
        # Registro Central de Empleados
        print("\n[3/5] Organizando la base de datos de Personal...")
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
            fecha_nacimiento DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (departamento_id) REFERENCES cat_departamentos(id),
            FOREIGN KEY (tipo_nomina_id) REFERENCES cat_tipos_nomina(id),
            UNIQUE KEY unique_emp_ced (id_empleado, cedula)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)
        
        # Gestión de Provisiones e Historial de entregas
        print("\n[4/5] Preparando las tablas de Provisiones y Beneficios...")
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
            ip_address VARCHAR(45),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """)
        
        # Bitácoras de Auditoría (Para saber qué cambió y quién lo hizo)
        print("\n[5/5] Activando los registros de seguridad (Bitácoras)...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(100),
            activity_type VARCHAR(50),
            activity_details TEXT,
            ip_address VARCHAR(45),
            activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """)

        conn.commit()
        print("\n✅ ¡Tablas creadas y reparadas con éxito!")
        return True
        
    except mariadb.Error as err:
        print(f"\n❌ Error al crear las tablas: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def insert_initial_data():
    """Carga la información básica necesaria para que el sistema empiece a funcionar"""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    
    try:
        print("\nCargando datos iniciales (Cargos y Usuarios)...")
        
        # Cargamos los cargos estándar de la empresa
        roles = [
            (1, 'administrador', 'Dueño del sistema con acceso total'),
            (2, 'supervisor', 'Encargado de revisar y aprobar beneficios'),
            (3, 'usuario', 'Personal administrativo estándar'),
            (4, 'visualizador', 'Solo puede ver reportes sin cambiar nada')
        ]
        for rid, name, desc in roles:
            cursor.execute("INSERT IGNORE INTO roles (id, name, description) VALUES (%s, %s, %s)", (rid, name, desc))

        # Creamos al usuario 'admin' maestro si el sistema es nuevo
        from passlib.hash import pbkdf2_sha256
        cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
        row = cursor.fetchone()
        if not row:
            # Clave por defecto: Admin123. (Se recomienda cambiarla al entrar)
            hashed_pw = pbkdf2_sha256.hash("Admin123.")
            cursor.execute("""
                INSERT INTO users (username, email, password, isAdmin, name, lastname, activo)
                VALUES ('admin', 'admin@liderpollo.com', %s, 1, 'Administrador', 'SICEB', 1)
            """, (hashed_pw,))
            user_id = cursor.lastrowid
            # Le asignamos el rol de administrador formalmente
            cursor.execute("INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, 1)", (user_id,))
            print("  ✓ Usuario 'admin' creado con éxito.")
        
        conn.commit()
        print("✅ Configuración inicial completada.")
        return True
        
    except mariadb.Error as err:
        print(f"❌ Error al cargar datos iniciales: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("--- INICIANDO CONFIGURACIÓN DEL SISTEMA SICEB ---")
    if create_all_tables():
        insert_initial_data()
        print("\n¡Listo! El sistema ya tiene su base de datos preparada.")
    else:
        print("\nHubo un problema y no se pudo terminar la configuración.")
