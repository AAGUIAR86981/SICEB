# migrate_users.py
from config.database import get_db_connection

def migrate_existing_users():
    """Asigna rol 'user' a todos los usuarios existentes"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔄 Migrando usuarios existentes...")
        
        # 1. Obtener ID del rol 'user'
        cursor.execute("SELECT id FROM roles WHERE name = 'user'")
        user_role = cursor.fetchone()
        
        if not user_role:
            print("❌ Error: No existe el rol 'user'")
            return
        
        user_role_id = user_role[0]
        
        # 2. Obtener todos los usuarios
        cursor.execute('SELECT id, username, isAdmin FROM users')
        users = cursor.fetchall()
        
        print(f"📊 Total usuarios encontrados: {len(users)}")
        
        # 3. Asignar rol 'user' a cada usuario
        for user_id, username, is_admin in users:
            # Verificar si ya tiene el rol
            cursor.execute('''
                SELECT COUNT(*) FROM user_roles 
                WHERE user_id = %s AND role_id = %s
            ''', (user_id, user_role_id))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    'INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)',
                    (user_id, user_role_id)
                )
                print(f"  ✅ {username} -> rol 'user'")
            
            # Si es admin, también asignar rol 'administrator'
            if is_admin == 1:
                cursor.execute("SELECT id FROM roles WHERE name = 'administrator'")
                admin_role = cursor.fetchone()
                if admin_role:
                    cursor.execute('''
                        SELECT COUNT(*) FROM user_roles 
                        WHERE user_id = %s AND role_id = %s
                    ''', (user_id, admin_role[0]))
                    
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(
                            'INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)',
                            (user_id, admin_role[0])
                        )
                        print(f"  👑 {username} -> también rol 'administrator'")
        
        conn.commit()
        print("\n✅ Migración completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_existing_users()