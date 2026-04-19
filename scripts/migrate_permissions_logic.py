
import os
from config.database import get_db_connection

def migrate_permissions():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Starting permissions migration...")

        # 1. Define Permissions
        # Format: (code, name, module)
        all_permissions = [
            ('all', 'Super Admin Permission', 'system'),
            ('create_provisions', 'Create Provisions', 'provision'),
            ('view_provisions_details', 'View Provision Details', 'provision'),
            ('view_history', 'View History', 'provision'),
            ('view_approved_employees', 'View Approved Employees', 'employee'),
            ('view_unapproved', 'View Unapproved Employees', 'employee'),
            ('create_users', 'Create Users', 'auth'),
            ('manage_users', 'Manage Users', 'auth'),
            ('export_data', 'Export Data', 'system'),
            ('configure_system', 'Configure System', 'system')
        ]

        # Insert Permissions if not exist
        for code, name, module in all_permissions:
            cursor.execute("SELECT id FROM permissions WHERE code = %s", (code,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO permissions (code, name, module) VALUES (%s, %s, %s)",
                    (code, name, module)
                )
                print(f"Created permission: {code}")
            else:
                print(f"Permission already exists: {code}")

        # 2. Define Roles and their Permissions
        role_permissions_map = {
            'administrador': ['all', 'create_provisions', 'view_provisions_details', 'manage_users', 'export_data', 'configure_system'],
            'supervisor': ['create_provisions', 'view_history', 'view_approved_employees', 'view_unapproved', 'view_provisions_details', 'export_data'],
            'usuario': ['view_history', 'create_provisions', 'view_approved_employees', 'create_users', 'view_provisions_details'],
            'visualizador': ['view_history', 'view_approved_employees']
        }

        # Insert Roles and Assign Permissions
        for role_name, perms in role_permissions_map.items():
            # Get or Create Role
            cursor.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
            role_row = cursor.fetchone()
            if not role_row:
                cursor.execute("INSERT INTO roles (name, description) VALUES (%s, %s)", (role_name, f"Role for {role_name}"))
                role_id = cursor.lastrowid
                print(f"Created role: {role_name}")
            else:
                role_id = role_row[0]
                print(f"Role exists: {role_name} (ID: {role_id})")

            # Assign Permissions
            for perm_code in perms:
                # Get Permission ID
                cursor.execute("SELECT id FROM permissions WHERE code = %s", (perm_code,))
                perm_row = cursor.fetchone()
                if perm_row:
                    perm_id = perm_row[0]
                    
                    # Check if assignment exists
                    cursor.execute(
                        "SELECT * FROM role_permissions WHERE role_id = %s AND permission_id = %s",
                        (role_id, perm_id)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
                            (role_id, perm_id)
                        )
                        print(f"  -> Assigned {perm_code} to {role_name}")
                else:
                    print(f"  !! Warning: Permission {perm_code} not found in DB")

        conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"Error during migration: {repr(e)}")
        if conn: conn.rollback()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    migrate_permissions()
