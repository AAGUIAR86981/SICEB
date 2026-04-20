from config.database import get_connection as get_db_connection
from passlib.hash import pbkdf2_sha256
import secrets
from datetime import datetime, timedelta

# Sistema de gestión de Usuarios: Aquí controlamos quién puede entrar y qué puede hacer
class User:
    """Clase para manejar a las personas que usan el sistema administrativo"""
    def __init__(self, id, username, email, password, is_admin, name=None, lastname=None, created_at=None, last_login=None, activo=None, original_row=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.name = name
        self.lastname = lastname
        self.created_at = created_at
        self.last_login = last_login
        self.activo = activo
        self.original_row = original_row

    @staticmethod
    def get_by_username(username):
        """Busca a un usuario por su nombre de acceso (el nombre que escribe para entrar)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, password, isAdmin, name, lastname, created_at, last_login, last_ip, activo FROM users WHERE username = %s', (username,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0], username=row[1], email=row[2], password=row[3], 
                    is_admin=row[4], name=row[5], lastname=row[6], created_at=row[7],
                    last_login=row[8], activo=row[10], original_row=row
                )
        except Exception as e:
            print(f"Error al buscar usuario por nombre: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        return None
    
    @staticmethod
    def get_id_by_username_email(username, email):
        """Busca un usuario por username y email, retorna su ID si existe"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM users WHERE username = %s AND email = %s',
                (username, email)
                )
            row = cursor.fetchone()
            if row:
                return row[0]  # Retorna el ID del usuario
            return None  # No se encontró coincidencia
        except Exception as e:
            print(f"Error al buscar usuario por username y email: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
                if conn:
                    conn.close()

    @staticmethod
    def get_by_id(user_id):
        """Busca a un usuario usando su número interno de identificación"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, email, password, isAdmin, name, lastname, created_at, last_login, last_ip, activo FROM users WHERE id = %s', (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0], username=row[1], email=row[2], password=row[3], 
                    is_admin=row[4], name=row[5], lastname=row[6], created_at=row[7],
                    last_login=row[8], activo=row[10], original_row=row
                )
        except Exception as e:
            print(f"Error al buscar usuario por número ID: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        return None

    @staticmethod
    def verify_credentials(username, password):
        """Verifica si el usuario y la clave que escribieron en el login son los correctos"""
        user = User.get_by_username(username)
        # Usamos pbkdf2_sha256 para comparar la clave escrita con la que está guardada de forma segura (encriptada)
        if user and pbkdf2_sha256.verify(password, user.password):
            return user
        return None

    @staticmethod
    def get_user_roles(user_id):
        """Obtiene la lista de cargos (roles) que tiene asignados una persona"""
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
            
            # Si la persona no tiene roles asignados, por defecto le damos el de 'usuario' básico
            if not roles:
                roles = ['usuario'] 
        except Exception as e:
            print(f"Problema al leer los cargos del usuario: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        return roles, role_ids

    @staticmethod
    def get_user_permissions(role_ids, is_admin=False):
        """Buscamos exactamente qué botones y acciones tiene permitido ver el usuario según su cargo"""
        conn = None
        cursor = None
        permissions = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Traemos los permisos que están registrados formalmente en la base de datos
            if role_ids:
                placeholders = ','.join(['%s'] * len(role_ids))
                cursor.execute(f'''
                    SELECT DISTINCT p.code
                    FROM permissions p
                    JOIN role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id IN ({placeholders})
                ''', tuple(role_ids))
                permissions = [p[0] for p in cursor.fetchall()]

            # 2. SEGUERIDAD ADICIONAL: Definimos los permisos básicos por cargo (por si la base de datos falla)
            role_names = []
            if role_ids:
                 placeholders = ','.join(['%s'] * len(role_ids))
                 cursor.execute(f'SELECT name FROM roles WHERE id IN ({placeholders})', tuple(role_ids))
                 role_names = [r[0].lower() for r in cursor.fetchall()]

            for role in role_names:
                if role == 'administrador':
                    permissions.append('all') # El admin puede hacer TODO
                elif role == 'usuario':
                    # Permisos para el personal operativo estándar
                    permissions.extend(['create_provisions', 'view_approved_employees', 'view_history', 'create_users'])
                elif role == 'supervisor':
                    permissions.extend(['create_provisions', 'view_history', 'view_approved_employees', 'view_unapproved'])
                elif role == 'visualizador':
                    permissions.extend(['view_history', 'view_approved_employees'])

            # 3. Si tiene el interruptor de Administrador encendido, le damos paso libre a TODO
            if is_admin and 'all' not in permissions:
                permissions.append('all')
                
        except Exception as e:
            print(f"Error al calcular los permisos permitidos: {e}")
        finally:
             if cursor: cursor.close()
             if conn: conn.close()
        return list(set(permissions))

    @staticmethod
    def create(username, email, password, name, lastname, is_admin, role_id=3):
        """Registra a una nueva persona para que pueda usar el sistema administrativo"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Encriptamos la clave antes de guardarla para que nadie (ni nosotros) pueda verla
            hashed_pw = pbkdf2_sha256.hash(password)
            
            cursor.execute('''
                INSERT INTO users (username, password, email, name, lastname, isAdmin)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (username, hashed_pw, email, name, lastname, is_admin))
            
            new_id = cursor.lastrowid
            
            # Le asignamos de una vez su cargo de usuario (Default ID 3) u otro que elijamos
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
        """Cambia la clave de un usuario (usado normalmente cuando la olvidan)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Encriptamos la nueva clave elegida por el usuario
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
    def get_all_users_with_roles():
        """Obtiene la lista completa de usuarios del sistema junto con todos los cargos que tienen"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True) 
            # Usamos GROUP_CONCAT para juntar todos los roles de una persona en una sola frase con comas
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.name, u.lastname, u.created_at, u.isAdmin, u.activo,
                GROUP_CONCAT(DISTINCT r.name ORDER BY r.name SEPARATOR ', ') as roles
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.id
                GROUP BY u.id ORDER BY u.created_at DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def delete_user_fully(user_id):
        """Elimina por completo a un usuario y todo su rastro (permisos, actividades, etc.)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Limpiamos sus roles y su historial de actividades antes de borrarlo a él
            cursor.execute('DELETE FROM user_roles WHERE user_id = %s', (user_id,))
            try:
                cursor.execute('DELETE FROM user_activities WHERE user_id = %s', (user_id,))
            except: pass

            # Finalmente, borramos el registro principal del usuario
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
        """Habilita o deshabilita la entrada de un usuario al sistema"""
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

    @staticmethod
    def create_reset_token(user_id):
        """Crea una 'llave temporal' única para que el usuario pueda cambiar su clave si la olvidó"""
        conn = None
        cursor = None
        try:
            # Generamos un código secreto difícil de adivinar
            token = secrets.token_urlsafe(32)
            # La llave solo sirve durante la próxima hora por seguridad
            expires_at = datetime.now() + timedelta(hours=1)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            # Anulamos cualquier llave anterior que el usuario haya pedido
            cursor.execute('UPDATE password_resets SET used = TRUE WHERE user_id = %s', (user_id,))
            
            # Guardamos la nueva llave temporal
            cursor.execute('INSERT INTO password_resets (user_id, token, expires_at) VALUES (%s, %s, %s)', (user_id, token, expires_at))
            conn.commit()
            return token
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    @staticmethod
    def validate_reset_token(token):
        """Verifica si la llave temporal que nos trajo el usuario todavía sirve y no ha expirado"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Solo es válida si no se ha usado antes y si la hora actual es menor al vencimiento
            cursor.execute('''
                SELECT user_id FROM password_resets
                WHERE token = %s AND used = FALSE AND expires_at > NOW()
            ''', (token,))
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
    def mark_token_as_used(token):
        """Invalida la llave temporal para que nadie pueda volver a usarla una vez que se cambió la clave"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE password_resets SET used = TRUE WHERE token = %s', (token,))
            conn.commit()
            return True
        except Exception as e:
            if conn: conn.rollback()
            raise e
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
