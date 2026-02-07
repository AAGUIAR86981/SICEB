# models/roles.py - FUNCIONES BÁSICAS PRIMERO
from config.database import get_db_connection

def get_user_roles(user_id):
    """Obtiene los roles de un usuario - VERSIÓN SIMPLE"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.name 
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = %s
        ''', (user_id,))
        
        roles = cursor.fetchall()
        # Devolver lista de diccionarios simples
        return [{'id': r[0], 'name': r[1]} for r in roles]
        
    except Exception as e:
        print(f"⚠️ Error obteniendo roles (continuando): {e}")
        return []  # Devolver lista vacía en caso de error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_user_permissions(user_id):
    """Obtiene los permisos de un usuario - VERSIÓN SIMPLE"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT p.code 
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = %s
        ''', (user_id,))
        
        permissions = cursor.fetchall()
        return [p[0] for p in permissions]
        
    except Exception as e:
        print(f"⚠️ Error obteniendo permisos (continuando): {e}")
        return []  # Devolver lista vacía
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Funciones adicionales (las agregaremos después)
def get_all_roles():
    """Obtiene todos los roles disponibles"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM roles ORDER BY name")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error en get_all_roles: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_user_roles(user_id, role_ids):
    """Actualiza los roles asignados a un usuario"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primero eliminar roles actuales
        cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
        
        # Insertar nuevos roles
        for rid in role_ids:
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, rid))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en update_user_roles: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def assign_role_to_user(user_id, role_name):
    """Asigna un rol a un usuario"""
    # La implementaremos después
    return True
