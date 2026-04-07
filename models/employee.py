from config.database import get_db_connection
import logging

# Sistema de gestión de Empleados: Aquí es donde Vive toda la lógica de datos del personal
logger = logging.getLogger(__name__)

class Employee:
    """Clase para representar y manejar la información de un trabajador"""
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
        """Busca empleados en la base de datos usando filtros (nombre, cédula, cargo, etc.)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Traemos los datos del empleado conectándolos con su departamento y tipo de nómina real
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
            
            # Filtro por texto: Si el usuario escribió algo en el buscador
            if search:
                query += " AND (e.nombre LIKE %s OR e.apellido LIKE %s OR e.cedula LIKE %s OR cd.nombre LIKE %s)"
                search_val = f"%{search}%"
                params.extend([search_val, search_val, search_val, search_val])
            
            # Filtro por nómina (Semanal o Quincenal)
            if tipo_nomina:
                query += " AND e.tipo_nomina_id = %s"
                params.append(tipo_nomina)
                
            # Filtro por estado: Solo activos o solo inactivos
            if estado is not None:
                query += " AND e.boolValidacion = %s"
                params.append(1 if estado == 'activo' else 0)
                
            # Agregamos el orden y la paginación (cuántos resultados mostrar por vez)
            query += f" ORDER BY e.id DESC LIMIT {int(limit)} OFFSET {int(offset)}"
            
            cursor.execute(query, tuple(params))
            empleados = cursor.fetchall()
            
            # Ajustamos un poco los datos para que sean fáciles de usar en las pantallas de la web
            for emp in empleados:
                emp['departamento'] = emp['departamento_nombre']
                emp['tipo_nomina_id'] = emp['tipoNomina']
                
            return empleados
            
        except Exception as e:
            logger.error(f"Error al intentar buscar empleados: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def count_with_filters(search=None, tipo_nomina=None, estado=None):
        """Cuenta cuántos empleados coinciden con los filtros (sin traer sus datos, solo el número)"""
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
            logger.error(f"Error al contar empleados: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_by_id(employee_id):
        """Busca toda la ficha de un empleado usando su número de registro único (ID)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Consultamos los datos uniendo las tablas de catálogos para tener nombres legibles
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
            logger.error(f"Error al buscar empleado por ID: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create(data):
        """Guarda un nuevo trabajador en el sistema"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Si el departamento que escribieron es nuevo, lo registramos automáticamente
            departamento_id = data.get('departamento_id')
            if not departamento_id and data.get('departamento'):
                departamento_id = Employee.get_or_create_department(data['departamento'])
            
            tipo_nomina_id = int(data.get('tipoNomina', 1))
            
            # Insertamos el registro en la base de datos
            query = """
                INSERT INTO empleados (id_empleado, cedula, nombre, apellido, departamento_id, tipo_nomina_id, boolValidacion, departamento, tipoNomina)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['id_empleado'],
                data['cedula'],
                data['nombre'],
                data['apellido'],
                departamento_id,
                tipo_nomina_id,
                data.get('boolValidacion', 1),
                data.get('departamento'),
                tipo_nomina_id
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Error creando empleado: {e}")
            
            # Avisamos si el error fue porque ya existe esa cédula o ese número de ficha
            if 'duplicate' in error_msg or '1062' in error_msg:
                if 'cedula' in error_msg: return 'DUPLICATE_CEDULA'
                if 'id_empleado' in error_msg: return 'DUPLICATE_ID'
                return 'DUPLICATE'
            
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update(employee_id, data):
        """Actualiza la información de un empleado existente"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verificamos el departamento (crearlo si es nuevo)
            departamento_id = data.get('departamento_id')
            if not departamento_id and data.get('departamento'):
                departamento_id = Employee.get_or_create_department(data['departamento'])
            
            tipo_nomina_id = int(data['tipoNomina'])
            
            # Para la auditoría, guardamos la IP de quien está haciendo el cambio
            from utils.helpers import get_client_ip
            cursor.execute("SET @client_ip = %s", (get_client_ip(),))

            # Ejecutamos la actualización
            query = """
                UPDATE empleados 
                SET id_empleado = %s, cedula = %s, nombre = %s, apellido = %s, 
                    departamento_id = %s, tipo_nomina_id = %s, 
                    boolValidacion = %s, departamento = %s, tipoNomina = %s
                WHERE id = %s
            """
            cursor.execute(query, (
                data['id_empleado'], data['cedula'], data['nombre'], data['apellido'],
                departamento_id, tipo_nomina_id, data['boolValidacion'],
                data.get('departamento'), tipo_nomina_id, employee_id
            ))
            conn.commit()
            return True 
        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Error actualizando empleado: {e}")
            if conn: conn.rollback()
            if 'duplicate' in error_msg or '1062' in error_msg:
                if 'cedula' in error_msg: return 'DUPLICATE_CEDULA'
                if 'id_empleado' in error_msg: return 'DUPLICATE_ID'
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_or_create_department(name):
        """Busca el número de ID de un departamento por su nombre; si no existe, lo crea de una vez"""
        if not name: return None
        name = name.strip()
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscamos si ya existe alguien con ese nombre de departamento
            cursor.execute("SELECT id FROM cat_departamentos WHERE nombre = %s", (name,))
            res = cursor.fetchone()
            if res:
                return res[0]
            
            # Si es nuevo, lo guardamos en el catálogo de departamentos
            cursor.execute("INSERT INTO cat_departamentos (nombre) VALUES (%s)", (name,))
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
        except Exception as e:
            logger.error(f"Error al manejar departamentos: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def toggle_status(employee_id):
        """Cambia el estado de un empleado (de activo a inactivo o viceversa)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Usamos una operación lógica NOT para invertir el valor actual
            cursor.execute("UPDATE empleados SET boolValidacion = NOT boolValidacion WHERE id = %s", (employee_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al cambiar estado del empleado: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_unique_departments():
        """Obtiene una lista limpia de todos los departamentos registrados en el sistema"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM cat_departamentos WHERE activo = TRUE ORDER BY nombre")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al listar departamentos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_payroll_summary(tipo_nomina):
        """Saca cuentas rápidas sobre la nómina consultada (totales, activos, departamentos)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Contamos el total general de esta nómina
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipo_nomina_id = %s", (tipo_nomina,))
            total = cursor.fetchone()[0]
            
            # Contamos cuántos de ellos pueden recibir beneficios (activos)
            cursor.execute("SELECT COUNT(*) FROM empleados WHERE tipo_nomina_id = %s AND boolValidacion = 1", (tipo_nomina,))
            activos = cursor.fetchone()[0]
            
            # Contamos en cuántos departamentos distintos están repartidos
            cursor.execute("SELECT COUNT(DISTINCT departamento_id) FROM empleados WHERE tipo_nomina_id = %s AND departamento_id IS NOT NULL", (tipo_nomina,))
            total_depts = cursor.fetchone()[0]
            
            return (int(total), int(activos), int(total - activos), int(total_depts))
        except Exception as e:
            logger.error(f"Error al calcular resumen de nómina: {e}")
            return (0, 0, 0, 0)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_department_summary(tipo_nomina):
        """Genera un reporte de cuántos activos e inactivos hay por cada departamento"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Hacemos una consulta agrupando por departamento y sumando los estados
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
            return [(row[0], int(row[1]), int(row[2])) for row in rows]
            
        except Exception as e:
            logger.error(f"Error al generar resumen por departamento: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def get_all(tipo_nomina, estado=None, limit=1000):
        """Función rápida para traer a todo el personal de una nómina (se usa mucho en provisiones)"""
        return Employee.get_all_with_filters(tipo_nomina=tipo_nomina, estado=estado, limit=limit)
