from config.database import get_db_connection
from datetime import datetime
import json
import logging
import mariadb
from models.employee import Employee

logger = logging.getLogger(__name__)

class Provision:
    @staticmethod
    def get_type_and_week():
        """Determina el tipo de provisión y el número de semana/quincena real.
        
        Retorna:
          - semana_iso: número de semana ISO del año (1–53), único dentro del año
          - quincena:   entero MES*10 + Q, donde Q=1 (días 1-15) o Q=2 (días 16-31).
                        Ej: febrero 2ª quincena → 22, enero 1ª quincena → 11.
                        Esto lo hace único por mes dentro de un mismo año.
        """
        serverDatetime = datetime.now()
        dia_del_mes = serverDatetime.day
        mes = serverDatetime.month
        
        # Para Semanal: número de semana ISO (1-53), único por año
        semana_iso = serverDatetime.isocalendar()[1]
        
        # Para Quincenal: codificado como MES*10 + Q para ser único por mes/año
        mitad = 1 if dia_del_mes <= 15 else 2
        quincena = mes * 10 + mitad   # ej: feb-2ª = 22, ene-1ª = 11
        
        return semana_iso, quincena



    @staticmethod
    def save_log(semProv, tipo_nomina, user_name, asignados_count, invalidados_count):
        """Metodo deprecado. Ahora se usa save_history para todo."""
        return True

    @staticmethod
    def save_history(tipo_provision, semana, tipo_nomina, productos, asignados, invalidados, usuario_id, usuario_nombre):
        """Guarda la provisión en el historial con información completa de otras tablas"""
        conn = None
        cursor = None
        try:
            # Obtener información detallada usando Employee Model
            departamentos_detallados = Employee.get_department_summary(tipo_nomina)
            resumen_nomina = Employee.get_payroll_summary(tipo_nomina)

            # Preparar datos para el historial
            datos_historial = {
                'productos': productos,
                'tipo_nomina': 'Semanal' if tipo_nomina == '1' else 'Quincenal',
                'empleados_asignados': len(asignados),
                'empleados_invalidados': len(invalidados),
                'resumen_nomina': {
                    'total_empleados': resumen_nomina[0] if resumen_nomina else 0,
                    'empleados_activos': resumen_nomina[1] if resumen_nomina else 0,
                    'empleados_inactivos': resumen_nomina[2] if resumen_nomina else 0,
                    'total_departamentos': resumen_nomina[3] if resumen_nomina else 0
                },
                'departamentos_detallados': [
                    {
                        'departamento': depto[0],
                        'activos': depto[1],
                        'inactivos': depto[2]
                    } for depto in departamentos_detallados
                ],
                'fecha_procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'usuario': usuario_nombre
            }

            productos_json = json.dumps(productos, ensure_ascii=False)
            datos_completos_json = json.dumps(datos_historial, ensure_ascii=False)

            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Start transaction explicitly if needed (mariadb connector usually handles it if autocommit is off)
            
            from utils.helpers import get_client_ip
            ip = get_client_ip()

            cursor.execute('''
                INSERT INTO provisiones_historial
                (tipo_provision, semana, tipo_nomina, productos, cant_aprobados, cant_rechazados, datos_completos, usuario_id, usuario_nombre, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                tipo_provision,
                semana,
                'Semanal' if tipo_nomina == '1' else 'Quincenal',
                productos_json,
                len(asignados),
                len(invalidados),
                datos_completos_json,
                usuario_id,
                usuario_nombre,
                ip
            ))
            
            provision_id = cursor.lastrowid

            # Insert into the new relational detail table (products)
            for item in productos:
                # productos item format could be (name, qty) or [name, qty]
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    cursor.execute('''
                        INSERT INTO provision_productos_historial (provision_id, producto_nombre, cantidad)
                        VALUES (%s, %s, %s)
                    ''', (provision_id, item[0], item[1]))

            # --- NUEVO: Insertar beneficiarios individuales ---
            # 1. Asignados (recibieron el beneficio)
            for emp in asignados:
                nombre_completo = f"{emp.get('nombre', '')} {emp.get('apellido', '')}".strip()
                cursor.execute('''
                    INSERT INTO provision_beneficiarios 
                    (provision_id, empleado_id, cedula, nombre_completo, departamento, recibio)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (provision_id, emp.get('id'), emp.get('cedula'), nombre_completo, emp.get('departamento'), True))

            # 2. Invalidados (no recibieron el beneficio)
            for emp in invalidados:
                nombre_completo = f"{emp.get('nombre', '')} {emp.get('apellido', '')}".strip()
                cursor.execute('''
                    INSERT INTO provision_beneficiarios 
                    (provision_id, empleado_id, cedula, nombre_completo, departamento, recibio)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (provision_id, emp.get('id'), emp.get('cedula'), nombre_completo, emp.get('departamento'), False))

            conn.commit()
            return provision_id
        except mariadb.Error as e:
            logger.error(f"Error de base de datos en save_history: {e}")
            if conn: conn.rollback()
            # Relanzar para que el controlador pueda manejar errores específicos como el 1062
            raise e
        except Exception as e:
            logger.error(f"Error inesperado en save_history: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_history(limit=100):
        # ... lógica para obtener historial ...
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, tipo_provision, semana, tipo_nomina, productos, datos_completos, 
                       fecha_creacion, usuario_nombre, cant_aprobados, cant_rechazados, ip_address
                FROM provisiones_historial
                ORDER BY fecha_creacion DESC
                LIMIT %s
            ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
             logger.error(f"Error getting history: {e}")
             return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_last_provision_date():
        """Obtiene la fecha de la última provisión registrada para cualquier nómina"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fecha_creacion 
                FROM provisiones_historial 
                ORDER BY fecha_creacion DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting last provision date: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_active_combos():
        """Obtiene los combos activos para el selector de provisión"""
        conn = None
        cursor = None
        item_cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, descripcion FROM combos WHERE activo = TRUE")
            combos = cursor.fetchall()
            
            item_cursor = conn.cursor(dictionary=True)
            for combo in combos:
                item_cursor.execute("""
                    SELECT cp.nombre, ci.cantidad
                    FROM combo_items ci
                    JOIN catalogo_productos cp ON ci.producto_id = cp.id
                    WHERE ci.combo_id = %s
                """, (combo['id'],))
                combo['items'] = item_cursor.fetchall()
                
            return combos
        except Exception as e:
            logger.error(f"Error getting combos for provision: {e}")
            return []
        finally:
            if item_cursor: item_cursor.close()
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def exists(semana, tipo_nomina):
        """Verifica si ya existe una provisión cargada para ese tipo de nómina HOY"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # tipo_nomina viene como '1' (Semanal) o '2' (Quincenal)
            nomina_str = 'Semanal' if tipo_nomina == '1' else 'Quincenal'
            
            # Verificar si ya existe una provisión de este tipo HOY
            query = """
                SELECT id FROM provisiones_historial 
                WHERE tipo_nomina = %s 
                AND DATE(fecha_creacion) = CURDATE()
                LIMIT 1
            """
            params = (nomina_str,)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking provision existence: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_beneficiary_report(filters=None):
        """Obtiene el reporte detallado de beneficiarios con filtros opcionales"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    pb.cedula, pb.nombre_completo, pb.departamento, pb.recibio, pb.fecha_entrega,
                    ph.tipo_nomina, ph.tipo_provision, ph.semana, ph.productos,
                    e.id_empleado
                FROM provision_beneficiarios pb
                JOIN provisiones_historial ph ON pb.provision_id = ph.id
                LEFT JOIN empleados e ON pb.empleado_id = e.id
            """
            params = []
            where_clauses = []
            
            if filters:
                if filters.get('provision_id'):
                    where_clauses.append("pb.provision_id = %s")
                    params.append(filters['provision_id'])
                if filters.get('recibio') is not None:
                    where_clauses.append("pb.recibio = %s")
                    params.append(filters['recibio'])
                if filters.get('cedula'):
                    where_clauses.append("pb.cedula LIKE %s")
                    params.append(f"%{filters['cedula']}%")
                if filters.get('nombre'):
                    where_clauses.append("pb.nombre_completo LIKE %s")
                    params.append(f"%{filters['nombre']}%")
                if filters.get('semana'):
                    where_clauses.append("ph.semana = %s")
                    params.append(filters['semana'])
                if filters.get('tipo_nomina'):
                    where_clauses.append("ph.tipo_nomina = %s")
                    params.append(filters['tipo_nomina'])
                if filters.get('fecha'):
                    where_clauses.append("DATE(pb.fecha_entrega) = %s")
                    params.append(filters['fecha'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " ORDER BY pb.fecha_entrega DESC LIMIT 500"
            
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting beneficiary report: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
