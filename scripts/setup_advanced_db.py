from config.database import get_db_connection

def setup_advanced_features():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    cursor = conn.cursor()
    try:
        print("--- 1. Mejorando Integridad (Cascadas) ---")
        # Muchos desarrolladores olvidan esto: Si borras un empleado, sus logs deben irse
        # Primero revisamos si podemos agregar FK a prov_emp_logs
        try:
            # Asegurarse que no haya datos huérfanos antes de poner la FK
            cursor.execute("DELETE FROM prov_emp_logs WHERE idEmpleado NOT IN (SELECT id FROM empleados)")
            
            # Intentar agregar la Foreign Key (si no existe)
            # Nota: En MariaDB/MySQL a veces es mejor verificar INFORMATION_SCHEMA
            cursor.execute("""
                ALTER TABLE prov_emp_logs 
                ADD CONSTRAINT fk_empleado_logs 
                FOREIGN KEY (idEmpleado) REFERENCES empleados(id) 
                ON DELETE CASCADE
            """)
            print("Foreign Key con CASCADE agregada a 'prov_emp_logs'.")
        except Exception as e:
            print(f"Nota: La FK ya existe o no se pudo crear: {e}")

        print("\n--- 2. Creando Vistas (Views) para Reportes ---")
        # Una VISTA es como una tabla "virtual" que guarda una consulta compleja.
        
        # A) Vista de Cumpleaños Próximos (Próximos 7 días)
        cursor.execute("DROP VIEW IF EXISTS v_proximos_cumpleanos")
        cursor.execute("""
            CREATE VIEW v_proximos_cumpleanos AS
            SELECT nombre, apellido, fecha_nacimiento, email,
                   FLOOR(DATEDIFF(
                       STR_TO_DATE(CONCAT(YEAR(CURDATE()), '-', MONTH(fecha_nacimiento), '-', DAY(fecha_nacimiento)), '%Y-%m-%d'),
                       CURDATE()
                   )) AS dias_faltantes
            FROM empleados
            WHERE fecha_nacimiento IS NOT NULL
            AND (
                MONTH(fecha_nacimiento) > MONTH(CURDATE()) 
                OR (MONTH(fecha_nacimiento) = MONTH(CURDATE()) AND DAY(fecha_nacimiento) >= DAY(CURDATE()))
            )
            ORDER BY dias_faltantes ASC
            LIMIT 10
        """)
        print("Vista 'v_proximos_cumpleanos' creada.")

        # B) Vista Resumen de Auditoría (Usuarios que más cambian datos)
        cursor.execute("DROP VIEW IF EXISTS v_resumen_auditoria")
        cursor.execute("""
            CREATE VIEW v_resumen_auditoria AS
            SELECT e.nombre, e.apellido, COUNT(a.audit_id) as total_cambios, MAX(a.changed_at) as ultimo_cambio
            FROM empleados e
            JOIN empleados_audit a ON e.id = a.employee_id
            GROUP BY e.id
            ORDER BY total_cambios DESC
        """)
        print("Vista 'v_resumen_auditoria' creada.")

        conn.commit()
    except Exception as e:
        print(f"Error en setup avanzado: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_advanced_features()
