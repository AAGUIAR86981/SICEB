from config.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class Product:
    """Modelo para gestión de productos en catalogo_productos"""
    
    @staticmethod
    def get_all(include_inactive=False):
        """Obtiene todos los productos, opcionalmente incluyendo inactivos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=1)
            
            query = "SELECT id, nombre, categoria, activo, created_at FROM catalogo_productos"
            if not include_inactive:
                query += " WHERE activo = 1"
            query += " ORDER BY nombre ASC"
            
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def get_by_id(product_id):
        """Obtiene un producto por su ID"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=1)
            cursor.execute("SELECT id, nombre, categoria, activo, created_at FROM catalogo_productos WHERE id = %s", (product_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting product by id: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def search(query, include_inactive=False):
        """Busca productos por nombre o categoría"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=1)
            
            sql = """
                SELECT id, nombre, categoria, activo, created_at FROM catalogo_productos 
                WHERE (nombre LIKE %s OR categoria LIKE %s)
            """
            params = [f"%{query}%", f"%{query}%"]
            
            if not include_inactive:
                sql += " AND activo = TRUE"
            
            sql += " ORDER BY nombre ASC"
            
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def create(nombre, categoria=None):
        """Crea un nuevo producto"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO catalogo_productos (nombre, categoria, activo) VALUES (%s, %s, TRUE)",
                (nombre, categoria)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def update(product_id, nombre, categoria=None, activo=True):
        """Actualiza un producto existente"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE catalogo_productos SET nombre = %s, categoria = %s, activo = %s WHERE id = %s",
                (nombre, categoria, activo, product_id)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def toggle_status(product_id):
        """Activa o desactiva un producto (soft delete)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE catalogo_productos SET activo = NOT activo WHERE id = %s",
                (product_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error toggling product status: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def exists_by_name(nombre, exclude_id=None):
        """Verifica si existe un producto con el mismo nombre"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if exclude_id:
                cursor.execute(
                    "SELECT id FROM catalogo_productos WHERE nombre = %s AND id != %s",
                    (nombre, exclude_id)
                )
            else:
                cursor.execute(
                    "SELECT id FROM catalogo_productos WHERE nombre = %s",
                    (nombre,)
                )
            
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking product existence: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    @staticmethod
    def count_all(include_inactive=False):
        """Cuenta el total de productos"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM catalogo_productos"
            if not include_inactive:
                query += " WHERE activo = TRUE"
            
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error al contar los productos: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_delivery_summary():
        """Genera un reporte acumulado de cuántas unidades de cada producto se han entregado"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # --- LÓGICA ESPECIAL PARA DATOS JSON ---
            # Como los productos entregados se guardan en una lista de texto (JSON) en el historial,
            # usamos 'JSON_TABLE' para abrir esa lista y poder sumar las cantidades entregadas.
            sql = """
                SELECT 
                    jt.nombre_producto AS Producto,
                    SUM(jt.cantidad_entregada * ph.cant_aprobados) AS Total_Unidades,
                    COUNT(DISTINCT ph.id) AS Cantidad_Provisiones
                FROM provisiones_historial ph
                CROSS JOIN JSON_TABLE(
                    ph.productos,
                    '$[*]' COLUMNS (
                        nombre_producto VARCHAR(100) PATH '$[0]',
                        cantidad_entregada INT PATH '$[1]'
                    )
                ) AS jt
                GROUP BY jt.nombre_producto
                ORDER BY Total_Unidades DESC
            """
            
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Hubo un problema al generar el reporte de entregas acumuladas: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
