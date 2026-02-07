from config.database import get_db_connection
from datetime import datetime
import json
import logging
from models.employee import Employee

logger = logging.getLogger(__name__)

class Provision:
    @staticmethod
    def get_type_and_week():
        """Determina el tipo de provisión y el número de semana/quincena real"""
        serverDatetime = datetime.now()
        dia_del_mes = serverDatetime.day
        
        # Para Semanal: Usamos el número de semana ISO del año (1-53)
        semana_iso = serverDatetime.isocalendar()[1]
        
        # Para Quincenal: 1 (primera mitad) o 2 (segunda mitad)
        quincena = 1 if dia_del_mes <= 15 else 2
        
        return semana_iso, quincena

    @staticmethod
    def get_available_tables():
        """Obtiene las configuraciones activas de provisión"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True) # Use dictionary cursor for easier access
            
            # Obtener configs activas
            cursor.execute("SELECT * FROM provision_configs WHERE active = TRUE")
            configs = cursor.fetchall()
            
            config_semanal = next((c for c in configs if c['provision_type'] == 'semanal'), None)
            config_quincenal = next((c for c in configs if c['provision_type'] == 'quincenal'), None)

            return config_semanal, config_quincenal
        except Exception as e:
            logger.error(f"Error checking provision configs: {e}")
            return None, None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_products(config_id, semProv):
        """Obtiene los productos de la provisión basada en el ID de configuración"""
        if not config_id:
            return []

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Obtener items de la config
            # Nota: semProv (week_number) debería coincidir con la config, pero confiamos en el ID
            cursor.execute('''
                SELECT product_name, quantity 
                FROM provision_items 
                WHERE provision_config_id = %s
            ''', (config_id,))
            
            items = cursor.fetchall()
            # items format: [(name, qty), (name, qty)...] which matches expected [(rubro, cant)...]
            
            # Convertir a formato lista de tuplas (Nombre, Cantidad)
            prodCant = [(item[0], str(item[1])) for item in items]

            return prodCant

        except Exception as e:
            logger.error(f"Error obteniendo productos de provisión: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

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
            
            cursor.execute('''
                INSERT INTO provisiones_historial
                (tipo_provision, semana, tipo_nomina, productos, cant_aprobados, cant_rechazados, datos_completos, usuario_id, usuario_nombre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                tipo_provision,
                semana,
                'Semanal' if tipo_nomina == '1' else 'Quincenal',
                productos_json,
                len(asignados),
                len(invalidados),
                datos_completos_json,
                usuario_id,
                usuario_nombre
            ))
            
            provision_id = cursor.lastrowid

            # Insert into the new relational detail table
            for item in productos:
                # productos item format could be (name, qty) or [name, qty]
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    cursor.execute('''
                        INSERT INTO provision_productos_historial (provision_id, producto_nombre, cantidad)
                        VALUES (%s, %s, %s)
                    ''', (provision_id, item[0], item[1]))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error guardando en historial: {e}")
            if conn: conn.rollback()
            return False
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
                       fecha_creacion, usuario_nombre, cant_aprobados, cant_rechazados
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
    def get_active_combos():
        """Obtiene los combos activos para el selector de provisión"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, descripcion FROM combos WHERE activo = TRUE")
            combos = cursor.fetchall()
            
            for combo in combos:
                cursor.execute("""
                    SELECT cp.nombre, ci.cantidad
                    FROM combo_items ci
                    JOIN catalogo_productos cp ON ci.producto_id = cp.id
                    WHERE ci.combo_id = %s
                """, (combo['id'],))
                combo['items'] = cursor.fetchall()
                
            return combos
        except Exception as e:
            logger.error(f"Error getting combos for provision: {e}")
            return []
        finally:
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
