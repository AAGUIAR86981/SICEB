
from config.database import get_db_connection
from passlib.hash import pbkdf2_sha256
import logging
import random

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def seed_test_data():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("="*50)
        print("      GENERATING TEST DATA")
        print("="*50)

        # 1. Create Sample Users (if not exist)
        print("\n1. Creating Sample Users...")
        # (username, password, role_name, name, lastname)
        sample_users = [
            ('supervisor1', 'Sup123.', 'supervisor', 'Carlos', 'Supervisor'),
            ('usuario1', 'User123.', 'usuario', 'Maria', 'Usuario'),
            ('visor1', 'Visor123.', 'visualizador', 'Luis', 'Visualizador')
        ]

        for username, pwd, role_name, name, lastname in sample_users:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                hashed_pw = pbkdf2_sha256.hash(pwd)
                cursor.execute("""
                    INSERT INTO users (username, password, email, name, lastname, isAdmin, activo)
                    VALUES (%s, %s, %s, %s, %s, 0, 1)
                """, (username, hashed_pw, f"{username}@test.com", name, lastname))
                user_id = cursor.lastrowid
                
                # Assign role
                cursor.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                role_row = cursor.fetchone()
                if role_row:
                    role_id = role_row[0]
                    cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, role_id))
                    print(f"   + Created user: {username} ({role_name})")
            else:
                print(f"   . User {username} already exists")


        # 2. Create Sample Employees
        print("\n2. Creating Sample Employees...")
        
        departments = ['Ventas', 'Almacen', 'Administracion', 'Recursos Humanos', 'Logistica']
        nombres = ['Jose', 'Ana', 'Pedro', 'Laura', 'Miguel', 'Carmen', 'David', 'Sofia', 'Jorge', 'Elena']
        apellidos = ['Garcia', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Perez', 'Sanchez', 'Ramirez', 'Torres']
        
        # We want around 50 employees
        count = 0
        for i in range(1, 51):
            id_empleado = 1000 + i
            cedula = 20000000 + i
            
            # Check existence
            cursor.execute("SELECT id FROM empleados WHERE id_empleado = %s", (id_empleado,))
            if not cursor.fetchone():
                nombre = random.choice(nombres)
                apellido = random.choice(apellidos)
                depto = random.choice(departments)
                tipo_nomina = random.randint(1, 4) # 1=Semanal usually
                bool_validacion = random.choice([0, 1]) # 0=inactivo/invalidado, 1=activo/validado? (Wait, schema says boolValidacion probably means validated/approved)
                
                # Checking schema: boolValidacion INT(1) NOT NULL DEFAULT 0
                # Let's assume 1 is approved/active
                
                cursor.execute("""
                    INSERT INTO empleados 
                    (id_empleado, cedula, nombre, apellido, departamento, tipoNomina, boolValidacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (id_empleado, cedula, nombre, apellido, depto, tipo_nomina, 1)) # Defaulting to 1 (active) for easier testing
                count += 1
        
        print(f"   + Created {count} new employees.")
        
        # Create some 'invalidated' employees for testing alerts/exports
        # Invalidated usually means they didn't pass some check
        print("\n3. Creating Invalidated Employees...")
        for i in range(51, 56):
            id_empleado = 1000 + i
            cedula = 20000000 + i
            cursor.execute("SELECT id FROM empleados WHERE id_empleado = %s", (id_empleado,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO empleados 
                    (id_empleado, cedula, nombre, apellido, departamento, tipoNomina, boolValidacion)
                    VALUES (%s, %s, %s, %s, %s, %s, 0)
                """, (id_empleado, cedula, "INVALIDO", f"TEST_{i}", 'Sin Asignar', 1))
                print(f"   + Created invalidated employee {id_empleado}")

        conn.commit()
        print("\n" + "="*50)
        print("   DATA GENERATION COMPLETED")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Error generating data: {e}")
        if conn: conn.rollback()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    seed_test_data()
