from config.database import get_db_connection

def get_all_permissions():
    """Obtener todos los permisos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, code, module FROM permissions ORDER BY module, name')
    permissions = cursor.fetchall()
    cursor.close()
    conn.close()
    return permissions

def get_permissions_by_role(role_id):
    """Obtener permisos de un rol específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.name, p.code 
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = %s
    ''', (role_id,))
    permissions = cursor.fetchall()
    cursor.close()
    conn.close()
    return permissions