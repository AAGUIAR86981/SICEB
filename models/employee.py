from config.database import get_db_connection
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class Employee:
    def __init__(self, id, cedula, nombre, apellido, departamento, tipoNomina, id_empleado, activo):
        self.id = id
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.departamento = departamento
        self.tipoNomina = tipoNomina
        self.id_empleado = id_empleado
        self.activo = activo

    @staticmethod
    def get_all_with_filters(search=None, tipo_nomina=None, estado=None, limit=100, offset=0):
        """Obtiene empleados con filtros de búsqueda y paginación - SCHEMA VERIFICADO"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Query ajustado estrictamente a las columnas VERIFICADAS que existen
            query = """
                SELECT 
                    id,
                    id_empleado,
                    cedula,
                    nombre,
                    apellido,
                    departamento,
                    tipoNomina,
                    boolValidacion
                FROM empleados
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (nombre LIKE %s OR apellido LIKE %s OR cedula LIKE %s OR departamento LIKE %s)"
                search_val = f"%{search}%"
                params.extend([search_val, search_val, search_val, search_val])
            
            if tipo_nomina:
                query += " AND tipoNomina = %s"
                params.append(tipo_nomina)
                
            if estado is not None:
                query += " AND boolValidacion = %s"
                params.append(1 if estado == 'activo' else 0)
                
            # Formatear LIMIT/OFFSET directamente
            query += f" ORDER BY id DESC LIMIT {int(limit)} OFFSET {int(offset)}"
            
            cursor.execute(query, tuple(params))
            empleados = cursor.fetchall()
            
            # Procesar resultados
            for emp in empleados:
                # El campo 'departamento' ya contiene el nombre
                emp['departamento_nombre'] = emp.get('departamento', 'Sin departamento')
                
                # Mapear tipoNomina (int) a nombre
                tn = emp.get('tipoNomina')
                if tn == 1:
                    emp['tipo_nomina_nombre'] = 'Semanal'
                elif tn == 2:
                    emp['tipo_nomina_nombre'] = 'Quincenal'
                else:
                    emp['tipo_nomina_nombre'] = 'Otro'
                    
                # Alias para compatibilidad con plantilla
                emp['departamento_id'] = 0 
                emp['tipo_nomina_id'] = tn
                
                # Campos faltantes en DB pero esperados por código (opcional)
                emp['fecha_ingreso'] = None
                emp['fecha_nacimiento'] = None
                emp['created_at'] = None
                
            return empleados
            
        except Exception as e:
            logger.error(f"Error in get_all_with_filters: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def count_with_filters(search=None, tipo_nomina=None, estado=None):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM empleados WHERE 1=1"
            params = []
            
            if search:
                query += " AND (nombre LIKE %s OR apellido LIKE %s OR cedula LIKE %s OR departamento LIKE %s)"
                search_val = f"%{search}%"
                params.extend([search_val, search_val, search_val, search_val])
            
            if tipo_nomina:
                query += " AND tipoNomina = %s"
                params.append(tipo_nomina)
                
            if estado is not None:
                query += " AND boolValidacion = %s"
                params.append(1 if estado == 'activo' else 0)
                
            cursor.execute(query, tuple(params))
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error in count_with_filters: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_by_id(employee_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Solo columnas existentes
            query = """
                SELECT 
                    id, id_empleado, cedula, nombre, apellido, 
                    departamento, tipoNomina, boolValidacion 
                FROM empleados WHERE id = %s
            """
            cursor.execute(query, (employee_id,))
            emp = cursor.fetchone()
            
            if emp:
                emp['departamento_nombre'] = emp.get('departamento')
                tn = emp.get('tipoNomina')
                emp['tipo_nomina_nombre'] = 'Semanal' if tn == 1 else ('Quincenal' if tn == 2 else 'Otro')
                emp['tipo_nomina_id'] = tn
                
            return emp
        except Exception as e:
            logger.error(f"Error in get_by_id: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create(data):
        """Crea un nuevo empleado"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            departamento_nombre = data['departamento']
            tipo_nomina = int(data.get('tipoNomina', 1))
            
            # Insertar solo en columnas existentes
            query = """
                INSERT INTO empleados (id_empleado, cedula, nombre, apellido, departamento, tipoNomina, boolValidacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['id_empleado'],
                data['cedula'],
                data['nombre'],
                data['apellido'],
                departamento_nombre,
                tipo_nomina,
                data.get('boolValidacion', 1)
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Error creating employee: {e}")
            
            if 'duplicate' in error_msg or '1062' in error_msg:
                if 'cedula' in error_msg:
                    return 'DUPLICATE_CEDULA'
                elif 'id_empleado' in error_msg:
                    return 'DUPLICATE_ID'
                else:
                    return 'DUPLICATE'
            
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update(employee_id, data):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            departamento_nombre = data['departamento']
            tipo_nomina = int(data['tipoNomina'])

            query = """
                UPDATE empleados 
                SET id_empleado = %s, cedula = %s, nombre = %s, apellido = %s, 
                    departamento = %s, tipoNomina = %s, 
                    boolValidacion = %s
                WHERE id = %s
            """
            cursor.execute(query, (
                data['id_empleado'],
                data['cedula'],
                data['nombre'],
                data['apellido'],
                departamento_nombre,
                tipo_nomina,
                data['boolValidacion'],
                employee_id
            ))
            conn.commit()
            return True # Success if no exception occurred
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Error updating employee {employee_id}: {e}")
            if conn: conn.rollback()
            
            if 'duplicate' in error_msg or '1062' in error_msg:
                if 'cedula' in error_msg: return 'DUPLICATE_CEDULA'
                if 'id_empleado' in error_msg: return 'DUPLICATE_ID'
                return 'DUPLICATE'
                
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def toggle_status(employee_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE empleados SET boolValidacion = NOT boolValidacion WHERE id = %s", (employee_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error toggling employee status: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_unique_departments():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT departamento FROM empleados WHERE departamento IS NOT NULL ORDER BY departamento")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error in get_unique_departments: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_payroll_summary(tipo_nomina):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Total Count
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipoNomina = %s", (tipo_nomina,))
            total = cursor.fetchone()[0]
            
            # 2. Active Count
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipoNomina = %s AND boolValidacion = 1", (tipo_nomina,))
            activos = cursor.fetchone()[0]
            
            # 3. Inactive Count (Calculated)
            inactivos = total - activos
            
            # 4. Total Departments Count
            cursor.execute("SELECT COUNT(DISTINCT departamento) FROM empleados WHERE tipoNomina = %s AND departamento IS NOT NULL", (tipo_nomina,))
            total_depts = cursor.fetchone()[0]
            
            return (int(total), int(activos), int(inactivos), int(total_depts))
        except Exception as e:
            logger.error(f"Error in get_payroll_summary: {e}")
            return (0, 0, 0, 0)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_department_summary(tipo_nomina):
        """Obtiene resumen de empleados por departamento para una nómina específica
        Retorna: Lista de tuplas (departamento, activos, inactivos)
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=False)
            
            # Query ajustado para retornar (Departamento, Activos, Inactivos)
            # COINCIDIR con provision.py: depto[0]=nombre, depto[1]=activos, depto[2]=inactivos
            cursor.execute("""
                SELECT 
                    departamento,
                    CAST(SUM(CASE WHEN boolValidacion = 1 THEN 1 ELSE 0 END) AS UNSIGNED) as activos,
                    CAST(SUM(CASE WHEN boolValidacion = 0 THEN 1 ELSE 0 END) AS UNSIGNED) as inactivos
                FROM empleados 
                WHERE tipoNomina = %s AND departamento IS NOT NULL
                GROUP BY departamento
                ORDER BY departamento
            """, (tipo_nomina,))
            
            rows = cursor.fetchall()
            # Asegurar que los conteos sean int y no Decimal para JSON serialization
            return [(row[0], int(row[1]), int(row[2])) for row in rows]
            
        except Exception as e:
            logger.error(f"Error in get_department_summary: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def get_all(tipo_nomina, estado=None, limit=1000):
        """Helper para compatibilidad con provision (devuelve lista de diccionarios)"""
        return Employee.get_all_with_filters(tipo_nomina=tipo_nomina, estado=estado, limit=limit)
