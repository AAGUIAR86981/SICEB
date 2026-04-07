# models/roles.py - Funciones para controlar los cargos y permisos del personal en el sistema
from config.database import get_db_connection

def get_user_roles(user_id):
    """Busca qué cargos (roles) tiene asignados una persona en el sistema"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hacemos un cruce (JOIN) entre cargos y la tabla de asignaciones para saber los nombres de sus roles
        cursor.execute('''
            SELECT r.id, r.name 
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = %s
        ''', (user_id,))
        
        roles = cursor.fetchall()
        # Devolvemos una lista limpia con el número de ID y el nombre de cada cargo
        return [{'id': r[0], 'name': r[1]} for r in roles]
        
    except Exception as e:
        print(f"Error técnico al buscar los cargos del usuario: {e}")
        return [] 
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_user_permissions(user_id):
    """Obtiene la lista de todas las acciones permitidas para un usuario según sus cargos"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscamos los códigos secretos de permisos (ej: 'manage_employees') que tienen sus roles asignados
        cursor.execute('''
            SELECT DISTINCT p.code 
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = %s
        ''', (user_id,))
        
        permissions = cursor.fetchall()
        # Devolvemos solo la lista de códigos de permisos (sin números de ID innecesarios)
        return [p[0] for p in permissions]
        
    except Exception as e:
        print(f"Error al intentar leer los permisos del usuario: {e}")
        return [] 
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_roles():
    """Trae una lista completa de todos los cargos existentes en la empresa (Admin, Supervisor, etc.)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Los ordenamos alfabéticamente para que se vean bien en los menús desplegables
        cursor.execute("SELECT id, name, description FROM roles ORDER BY name")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al listar todos los cargos disponibles: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_user_roles(user_id, role_ids):
    """Le cambia los cargos a un usuario por los nuevos que el administrador decidió"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Paso 1: Primero borramos todos los cargos que tenía antes para no mezclarlos con los nuevos
        cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
        
        # Paso 2: Insertamos uno por uno los nuevos cargos que marcamos en el panel administrativo
        for rid in role_ids:
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, rid))
            
        conn.commit() # Guardamos los cambios definitivamente
        return True
    except Exception as e:
        print(f"Error al intentar actualizar los cargos del usuario: {e}")
        if conn: conn.rollback() # Si algo salió mal, deshacemos los cambios para seguridad
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def assign_role_to_user(user_id, role_name):
    """Asignación rápida de un rol específico a un usuario (uso interno del sistema)"""
    # Esta función se usará en futuras actualizaciones automáticas
    return True
