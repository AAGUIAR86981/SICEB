from config.database import get_db_connection
import logging

# Configuramos el sistema de alertas para registrar cualquier problema que ocurra en este archivo
logger = logging.getLogger(__name__)

class ComboModel:
    @staticmethod
    def get_catalog():
        """Trae la lista completa de productos individuales (como pollo, mortadela, etc.) que están activos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            # Usamos dictionary=True para que los resultados vengan con nombres de columna (ej. 'nombre') en vez de números
            cursor = conn.cursor(dictionary=True)
            # Buscamos solo los que tienen el interruptor 'activo' encendido y los ordenamos alfabéticamente
            cursor.execute("SELECT id, nombre, categoria, unidad, activo, created_at FROM catalogo_productos WHERE activo = TRUE ORDER BY nombre ASC")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hubo un problema al pedir el catálogo a la base de datos: {e}")
            return []
        finally:
            # Siempre cerramos la conexión para no dejar la puerta abierta innecesariamente
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_all_combos():
        """Obtiene una lista de todos los combos registrados, estén prendidos o apagados"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Listamos todos los combos creados para mostrarlos en el panel de administración
            cursor.execute("SELECT id, nombre, descripcion, activo, created_by, created_at, updated_at FROM combos ORDER BY nombre ASC")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al intentar listar todos los combos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_active_combos():
        """Busca solo los combos que están listos para usarse y les pega la lista de productos que cada uno contiene"""
        conn = None
        cursor = None
        item_cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Primero buscamos los encabezados de los combos activos
            cursor.execute("SELECT id, nombre, descripcion, activo, created_by, created_at, updated_at FROM combos WHERE activo = TRUE ORDER BY nombre ASC")
            combos = cursor.fetchall()
            
            # Ahora, para cada combo, buscamos por separado qué productos lleva dentro (item por item)
            item_cursor = conn.cursor(dictionary=True)
            for combo in combos:
                item_cursor.execute("""
                    SELECT ci.id, ci.producto_id, ci.cantidad, cp.nombre, cp.unidad 
                    FROM combo_items ci
                    JOIN catalogo_productos cp ON ci.producto_id = cp.id
                    WHERE ci.combo_id = %s
                """, (combo['id'],))
                combo['items'] = item_cursor.fetchall()
                
            return combos
        except Exception as e:
            logger.error(f"Error al buscar los combos activos y sus detalles: {e}")
            return []
        finally:
            if item_cursor: item_cursor.close()
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_combo_by_id(combo_id):
        """Busca toda la información de un combo específico usando su número de identificación (ID)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Buscamos el nombre y la descripción general del combo
            cursor.execute("SELECT id, nombre, descripcion, activo, created_by, created_at, updated_at FROM combos WHERE id = %s", (combo_id,))
            combo = cursor.fetchone()
            
            if not combo:
                return None
                
            # Luego traemos la lista de productos que lo componen (la receta del combo)
            cursor.execute("""
                SELECT ci.id, ci.producto_id, ci.cantidad, cp.nombre, cp.unidad 
                FROM combo_items ci
                JOIN catalogo_productos cp ON ci.producto_id = cp.id
                WHERE ci.combo_id = %s
            """, (combo_id,))
            combo['items'] = cursor.fetchall()
            
            return combo
        except Exception as e:
            logger.error(f"Error al intentar obtener el combo número {combo_id}: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create_combo(nombre, descripcion, items):
        """Guarda un combo nuevo en la base de datos, incluyendo la lista de productos que lo forman"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Primero guardamos el nombre y la descripción general del combo
            cursor.execute(
                "INSERT INTO combos (nombre, descripcion, activo) VALUES (%s, %s, TRUE)",
                (nombre, descripcion)
            )
            # Recuperamos el ID que la base de datos le asignó automáticamente a este nuevo combo
            combo_id = cursor.lastrowid
            
            # Ahora guardamos uno por uno los productos que forman parte de este combo
            for item in items:
                cursor.execute(
                    "INSERT INTO combo_items (combo_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                    (combo_id, item['producto_id'], item['cantidad'])
                )
            
            # Confirmamos la operación (commit) para que los cambios se guarden para siempre
            conn.commit()
            return combo_id
        except Exception as e:
            logger.error(f"No se pudo crear el combo nuevo: {e}")
            # Si algo falló, deshacemos todo para no dejar datos a medias (rollback)
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_combo(combo_id, nombre, descripcion, activo, items):
        """Sobreescribe la información de un combo existente y actualiza su lista de productos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Actualizamos los datos principales (nombre, descripción y si está activo)
            cursor.execute(
                "UPDATE combos SET nombre = %s, descripcion = %s, activo = %s WHERE id = %s",
                (nombre, descripcion, activo, combo_id)
            )
            
            # Para actualizar los productos, la forma más limpia es borrar los que tenía antes...
            cursor.execute("DELETE FROM combo_items WHERE combo_id = %s", (combo_id,))
            
            # ...y volver a insertar la nueva lista que nos enviaron
            for item in items:
                cursor.execute(
                    "INSERT INTO combo_items (combo_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                    (combo_id, item['producto_id'], item['cantidad'])
                )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al intentar actualizar el combo {combo_id}: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def toggle_combo(combo_id, active_status):
        """Enciende o apaga un combo (activo/inactivo) sin borrarlo de la base de datos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Simplemente cambiamos el estado de 'activo' al nuevo valor (True o False)
            cursor.execute("UPDATE combos SET activo = %s WHERE id = %s", (active_status, combo_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al intentar cambiar el estado del combo {combo_id}: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
