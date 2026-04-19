from config.database import get_db_connection

def create_audit_trigger():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    cursor = conn.cursor()
    try:
        print("Creating Audit Table...")
        # 1. Crear tabla de auditoría
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados_audit (
                audit_id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT,
                old_cedula INT,
                old_nombre VARCHAR(50),
                old_apellido VARCHAR(50),
                old_tipoNomina INT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_type VARCHAR(20) DEFAULT 'UPDATE'
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
        """)

        print("Creating/Updating Trigger...")
        # 2. Crear Trigger
        # Nota: MariaDB/MySQL requiere delimitadores si se hace desde cliente SQL, 
        # pero desde Python execute() se manda el string directo.
        
        # Primero borramos si existe para evitar errores al recrear
        cursor.execute("DROP TRIGGER IF EXISTS before_empleado_update")
        
        cursor.execute("""
            CREATE TRIGGER before_empleado_update
            BEFORE UPDATE ON empleados
            FOR EACH ROW
            BEGIN
                -- Solo insertar si hay cambios relevantes (auditoría inteligente)
                IF OLD.cedula != NEW.cedula OR 
                   OLD.nombre != NEW.nombre OR 
                   OLD.apellido != NEW.apellido OR
                   OLD.tipoNomina != NEW.tipoNomina THEN
                   
                    INSERT INTO empleados_audit 
                    (employee_id, old_cedula, old_nombre, old_apellido, old_tipoNomina)
                    VALUES 
                    (OLD.id, OLD.cedula, OLD.nombre, OLD.apellido, OLD.tipoNomina);
                END IF;
            END
        """)
        
        conn.commit()
        print("Audit Trigger created successfully.")
        
    except Exception as e:
        print(f"Error creating trigger: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_audit_trigger()
