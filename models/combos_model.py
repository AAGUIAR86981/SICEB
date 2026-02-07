from config.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class ComboModel:
    @staticmethod
    def get_catalog():
        """Obtiene el catálogo de productos disponibles"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM catalogo_productos WHERE activo = TRUE ORDER BY nombre ASC")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting catalog: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_all_combos():
        """Obtiene todos los combos con su estado"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM combos ORDER BY nombre ASC")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting combos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_active_combos():
        """Obtiene solo los combos activos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM combos WHERE activo = TRUE ORDER BY nombre ASC")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting active combos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_combo_by_id(combo_id):
        """Obtiene un combo y sus productos asociados"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Info del combo
            cursor.execute("SELECT * FROM combos WHERE id = %s", (combo_id,))
            combo = cursor.fetchone()
            
            if not combo:
                return None
                
            # Items del combo
            cursor.execute("""
                SELECT ci.id, ci.producto_id, ci.cantidad, cp.nombre, cp.unidad 
                FROM combo_items ci
                JOIN catalogo_productos cp ON ci.producto_id = cp.id
                WHERE ci.combo_id = %s
            """, (combo_id,))
            combo['items'] = cursor.fetchall()
            
            return combo
        except Exception as e:
            logger.error(f"Error getting combo by ID: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def create_combo(nombre, descripcion, items):
        """Crea un nuevo combo con sus productos
        items: lista de diccionarios {'producto_id': id, 'cantidad': qty}
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insertar combo
            cursor.execute(
                "INSERT INTO combos (nombre, descripcion, activo) VALUES (%s, %s, TRUE)",
                (nombre, descripcion)
            )
            combo_id = cursor.lastrowid
            
            # Insertar items
            for item in items:
                cursor.execute(
                    "INSERT INTO combo_items (combo_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                    (combo_id, item['producto_id'], item['cantidad'])
                )
            
            conn.commit()
            return combo_id
        except Exception as e:
            logger.error(f"Error creating combo: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_combo(combo_id, nombre, descripcion, activo, items):
        """Actualiza un combo y sus productos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Actualizar info básica
            cursor.execute(
                "UPDATE combos SET nombre = %s, descripcion = %s, activo = %s WHERE id = %s",
                (nombre, descripcion, activo, combo_id)
            )
            
            # Reemplazar items: eliminar viejos e insertar nuevos
            cursor.execute("DELETE FROM combo_items WHERE combo_id = %s", (combo_id,))
            
            for item in items:
                cursor.execute(
                    "INSERT INTO combo_items (combo_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                    (combo_id, item['producto_id'], item['cantidad'])
                )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating combo: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def toggle_combo(combo_id, active_status):
        """Activa o desactiva un combo"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE combos SET activo = %s WHERE id = %s", (active_status, combo_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error toggling combo: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
