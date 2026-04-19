from config.database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)

def seed_permissions():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        print("Seeding Permissions...")

        # 1. Define Standard Permissions
        permissions = [
            # Code, Name, Module
            ('create_provisions', 'Crear Provisiones', 'provisions'),
            ('view_history', 'Ver Historial', 'provisions'),
            ('view_approved_employees', 'Ver Empleados Aprobados', 'employees'),
            ('view_unapproved', 'Ver Empleados No Aprobados', 'employees'),
            ('create_users', 'Crear Usuarios', 'auth'),
            ('manage_roles', 'Gestionar Roles', 'auth')
        ]

        perm_ids = {}
        for code, name, module in permissions:
            # Insert if not exists
            cursor.execute("SELECT id FROM permissions WHERE code = %s", (code,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("INSERT INTO permissions (code, name, module) VALUES (%s, %s, %s)", (code, name, module))
                perm_ids[code] = cursor.lastrowid
            else:
                perm_ids[code] = row[0]

        # 2. Assign to Roles
        # Get Role IDs
        cursor.execute("SELECT id, name FROM roles")
        role_map = {row[1]: row[0] for row in cursor.fetchall()}

        # Define Role-Permission Mappings
        role_permissions = {
            'administrador': ['create_provisions', 'view_history', 'view_approved_employees', 'view_unapproved', 'create_users', 'manage_roles'],
            'supervisor': ['create_provisions', 'view_history', 'view_approved_employees', 'view_unapproved'],
            'usuario': ['create_provisions', 'view_history', 'view_approved_employees', 'create_users'], # Manteniendo lógica legacy
            'visualizador': ['view_history', 'view_approved_employees']
        }

        for role_name, perms in role_permissions.items():
            if role_name not in role_map: continue
            role_id = role_map[role_name]
            
            for perm_code in perms:
                if perm_code not in perm_ids: continue
                perm_id = perm_ids[perm_code]
                
                # Check existence
                cursor.execute("SELECT 1 FROM role_permissions WHERE role_id=%s AND permission_id=%s", (role_id, perm_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)", (role_id, perm_id))

        conn.commit()
        print("  Permissions seeded successfully.")

    except Exception as e:
        print(f"  Error seeding permissions: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_permissions()
