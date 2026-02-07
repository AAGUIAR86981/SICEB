from config.database import get_db_connection
from passlib.hash import pbkdf2_sha256

class User:
    def __init__(self, id, username, email, password, is_admin, name=None, lastname=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.name = name
        self.lastname = lastname
        self.created_at = created_at

    @staticmethod
    def get_by_username(username):
        conn = None
        cursor = None
        user = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            row = cursor.fetchone()
            if row:
                # Assuming row order matches: id, username, email, password, isAdmin, name, lastname, created_at...
                # Adjust indices based on actual DB schema if needed. 
                # Based on creating code: id, username, email, password, isAdmin, name, lastname, created_at
                user = User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password=row[3],
                    is_admin=row[4],
                    name=row[5] if len(row) > 5 else None,
                    lastname=row[6] if len(row) > 6 else None,
                    created_at=row[7] if len(row) > 7 else None
                )
                # Store extra fields if needed, or handle defaults
                user.original_row = row 
        except Exception as e:
            print(f"Error getting user by username: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        return user

    @staticmethod
    def get_by_id(user_id):
        conn = None
        cursor = None
        user = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            row = cursor.fetchone()
            if row:
                user = User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password=row[3],
                    is_admin=row[4],
                    name=row[5] if len(row) > 5 else None,
                    lastname=row[6] if len(row) > 6 else None,
                    created_at=row[7] if len(row) > 7 else None
                )
                user.original_row = row
        except Exception as e:
            print(f"Error getting user by id: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        return user

    @staticmethod
    def verify_credentials(username, password):
        user = User.get_by_username(username)
        if user and pbkdf2_sha256.verify(password, user.password):
            return user
        return None

    @staticmethod
    def get_user_roles(user_id):
        conn = None
        cursor = None
        roles = []
        role_ids = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, r.name
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = %s
            ''', (user_id,))
            results = cursor.fetchall()
            for r in results:
                role_ids.append(r[0])
                roles.append(r[1])
            
            # Fallback logic mirroring auth.py
            if not roles:
                # Fetch user to check default role (legacy logic support)
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                user_row = cursor.fetchone()
                if user_row and len(user_row) > 8: # default_role_id index
                     cursor.execute('SELECT id, name FROM roles WHERE id = %s', (user_row[8],))
                     def_role = cursor.fetchone()
                     if def_role:
                         role_ids.append(def_role[0])
                         roles.append(def_role[1])
                
            if not roles:
                roles = ['usuario'] 
        except Exception as e:
            print(f"Error getting user roles: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        return roles, role_ids

    @staticmethod
    def get_user_permissions(role_ids, is_admin=False):
        conn = None
        cursor = None
        permissions = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Obtener permisos desde base de datos (si existen)
            if role_ids:
                placeholders = ','.join(['%s'] * len(role_ids))
                cursor.execute(f'''
                    SELECT DISTINCT p.code
                    FROM permissions p
                    JOIN role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id IN ({placeholders})
                ''', tuple(role_ids))
                permissions = [p[0] for p in cursor.fetchall()]

            # 2. Agregar permisos HARDCODED según roles (Lógica de Negocio Específica)
            # Esto asegura que los roles funcionen como se espera incluso si la BD de permisos está vacía o incompleta
            
            # Obtener nombres de roles para aplicar lógica
            role_names = []
            if role_ids:
                 placeholders = ','.join(['%s'] * len(role_ids))
                 cursor.execute(f'SELECT name FROM roles WHERE id IN ({placeholders})', tuple(role_ids))
                 role_names = [r[0].lower() for r in cursor.fetchall()]

            for role in role_names:
                if role == 'administrador':
                    permissions.append('all')
                elif role == 'usuario':
                    # User: Generar provisiones, ver aprobados, ver historial, CREAR USUARIOS
                    permissions.extend([
                        'create_provisions', 
                        'view_approved_employees', 
                        'view_history',
                        'create_users'  # Solicitud específica
                    ])
                elif role == 'supervisor':
                    permissions.extend([
                        'create_provisions',
                        'view_history',
                        'view_approved_employees',
                        'view_unapproved' # Often supervisors need to see everything
                    ])
                elif role == 'visualizador':
                    # Viewer: Ver historial, ver aprobados
                    permissions.extend([
                        'view_history',
                        'view_approved_employees'
                    ])

            # 3. Si es admin flag en users table, dar todo
            if is_admin and 'all' not in permissions:
                permissions.append('all')
                
        except Exception as e:
            print(f"Error getting permissions: {e}")
        finally:
             if cursor: cursor.close()
             if conn: conn.close()
        return list(set(permissions))

    @staticmethod
    def create(username, email, password, name, lastname, is_admin, role_id=3):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            hashed_pw = pbkdf2_sha256.hash(password)
            
            cursor.execute('''
                INSERT INTO users (username, password, email, name, lastname, isAdmin)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (username, hashed_pw, email, name, lastname, is_admin))
            
            new_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO user_roles (user_id, role_id, assigned_at)
                VALUES (%s, %s, NOW())
            ''', (new_id, role_id))
            
            conn.commit()
            return new_id
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def update_password_by_reset_id(reset_id, new_password):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            hashed = pbkdf2_sha256.hash(new_password)
            cursor.execute('UPDATE users SET password=%s WHERE id=%s', (hashed, reset_id))
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def get_id_by_username_email(username, email):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = %s AND email = %s', (username, email))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        except Exception as e:
             raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def get_all_users_with_roles():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            # Try to use dictionary cursor if possible, but standard fetchall is safer for now across environments
            cursor = conn.cursor(dictionary=True) 
            cursor.execute('''
                SELECT
                    u.id,
                    u.username,
                    u.email,
                    u.name,
                    u.lastname,
                    u.created_at,
                    u.isAdmin,
                    u.activo,
                    GROUP_CONCAT(DISTINCT r.name ORDER BY r.name SEPARATOR ', ') as roles,
                    COUNT(DISTINCT ur.role_id) as num_roles
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.id
                GROUP BY u.id
                ORDER BY u.created_at DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def delete_user_fully(user_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Roles
            cursor.execute('DELETE FROM user_roles WHERE user_id = %s', (user_id,))
            # Logs (try/except ignored in original, we can check table existence or just try)
            try:
                cursor.execute('DELETE FROM user_logs WHERE userID = %s', (user_id,))
            except: pass
            
            # User
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
             if cursor: cursor.close()
             if conn: conn.close()
             
    @staticmethod
    def toggle_active_status(user_id, status):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET activo = %s WHERE id = %s', (status, user_id))
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
