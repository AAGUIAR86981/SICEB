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
            
            # Query ajustado para usar JOINs con catálogos (3NF)
            query = """
                SELECT 
                    e.id,
                    e.id_empleado,
                    e.cedula,
                    e.nombre,
                    e.apellido,
                    cd.nombre as departamento_nombre,
                    ctn.nombre as tipo_nomina_nombre,
                    e.departamento_id,
                    e.tipo_nomina_id as tipoNomina,
                    e.boolValidacion
                FROM empleados e
                LEFT JOIN cat_departamentos cd ON e.departamento_id = cd.id
                LEFT JOIN cat_tipos_nomina ctn ON e.tipo_nomina_id = ctn.id
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (e.nombre LIKE %s OR e.apellido LIKE %s OR e.cedula LIKE %s OR cd.nombre LIKE %s)"
                search_val = f"%{search}%"
                params.extend([search_val, search_val, search_val, search_val])
            
            if tipo_nomina:
                query += " AND e.tipo_nomina_id = %s"
                params.append(tipo_nomina)
                
            if estado is not None:
                query += " AND e.boolValidacion = %s"
                params.append(1 if estado == 'activo' else 0)
                
            # Formatear LIMIT/OFFSET directamente
            query += f" ORDER BY e.id DESC LIMIT {int(limit)} OFFSET {int(offset)}"
            
            cursor.execute(query, tuple(params))
            empleados = cursor.fetchall()
            
            # Procesar resultados para compatibilidad
            for emp in empleados:
                # Alias para compatibilidad con plantillas antiguas
                emp['departamento'] = emp['departamento_nombre']
                emp['tipo_nomina_id'] = emp['tipoNomina']
                
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
            # Query 3NF con JOINs
            query = """
                SELECT 
                    e.id, e.id_empleado, e.cedula, e.nombre, e.apellido, 
                    cd.nombre as departamento_nombre, e.departamento_id,
                    e.tipo_nomina_id as tipoNomina, e.boolValidacion,
                    ctn.nombre as tipo_nomina_nombre
                FROM empleados e
                LEFT JOIN cat_departamentos cd ON e.departamento_id = cd.id
                LEFT JOIN cat_tipos_nomina ctn ON e.tipo_nomina_id = ctn.id
                WHERE e.id = %s
            """
            cursor.execute(query, (employee_id,))
            emp = cursor.fetchone()
            
            if emp:
                emp['departamento'] = emp['departamento_nombre']
                emp['tipo_nomina_id'] = emp['tipoNomina']
                
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
            
            # Obtener o crear ID del departamento a partir del nombre (mantiene funcionalidad UI)
            departamento_id = data.get('departamento_id')
            if not departamento_id and data.get('departamento'):
                departamento_id = Employee.get_or_create_department(data['departamento'])
            
            tipo_nomina_id = int(data.get('tipoNomina', 1))
            
            # Insertar en columnas normalizadas y mantener legacy por seguridad
            query = """
                INSERT INTO empleados (id_empleado, cedula, nombre, apellido, departamento_id, tipo_nomina_id, boolValidacion, departamento, tipoNomina)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Obtenemos el nombre final del departamento para la columna legacy
            dept_name = data.get('departamento')
            
            cursor.execute(query, (
                data['id_empleado'],
                data['cedula'],
                data['nombre'],
                data['apellido'],
                departamento_id,
                tipo_nomina_id,
                data.get('boolValidacion', 1),
                dept_name,
                tipo_nomina_id
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

            # Obtener o crear ID del departamento (mantiene funcionalidad UI)
            departamento_id = data.get('departamento_id')
            if not departamento_id and data.get('departamento'):
                departamento_id = Employee.get_or_create_department(data['departamento'])
            
            tipo_nomina_id = int(data['tipoNomina'])
            from utils.helpers import get_client_ip
            ip = get_client_ip()
            cursor.execute("SET @client_ip = %s", (ip,))

            query = """
                UPDATE empleados 
                SET id_empleado = %s, cedula = %s, nombre = %s, apellido = %s, 
                    departamento_id = %s, tipo_nomina_id = %s, 
                    boolValidacion = %s,
                    departamento = %s,
                    tipoNomina = %s
                WHERE id = %s
            """
            cursor.execute(query, (
                data['id_empleado'],
                data['cedula'],
                data['nombre'],
                data['apellido'],
                departamento_id,
                tipo_nomina_id,
                data['boolValidacion'],
                dept_name,
                tipo_nomina_id,
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
    def get_or_create_department(name):
        """Busca el ID de un departamento por nombre o lo crea si no existe"""
        if not name: return None
        name = name.strip()
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar ID
            cursor.execute("SELECT id FROM cat_departamentos WHERE nombre = %s", (name,))
            res = cursor.fetchone()
            if res:
                return res[0]
            
            # Si no existe, crear
            cursor.execute("INSERT INTO cat_departamentos (nombre) VALUES (%s)", (name,))
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
        except Exception as e:
            logger.error(f"Error in get_or_create_department: {e}")
            return None
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
        """Obtiene todos los departamentos del catálogo (ID y Nombre)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM cat_departamentos WHERE activo = TRUE ORDER BY nombre")
            return cursor.fetchall()
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
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipo_nomina_id = %s", (tipo_nomina,))
            total = cursor.fetchone()[0]
            
            # 2. Active Count
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipo_nomina_id = %s AND boolValidacion = 1", (tipo_nomina,))
            activos = cursor.fetchone()[0]
            
            # 3. Inactive Count (Calculated)
            inactivos = total - activos
            
            # 4. Total Departments Count
            cursor.execute("SELECT COUNT(DISTINCT departamento_id) FROM empleados WHERE tipo_nomina_id = %s AND departamento_id IS NOT NULL", (tipo_nomina,))
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
            
            # Query 3NF con JOIN para obtener nombres reales
            cursor.execute("""
                SELECT 
                    cd.nombre,
                    CAST(SUM(CASE WHEN e.boolValidacion = 1 THEN 1 ELSE 0 END) AS UNSIGNED) as activos,
                    CAST(SUM(CASE WHEN e.boolValidacion = 0 THEN 1 ELSE 0 END) AS UNSIGNED) as inactivos
                FROM empleados e
                JOIN cat_departamentos cd ON e.departamento_id = cd.id
                WHERE e.tipo_nomina_id = %s
                GROUP BY e.departamento_id
                ORDER BY cd.nombre
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
