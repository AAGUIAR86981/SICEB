# controllers/auth.py - Módulo encargado de la seguridad y el acceso al sistema
from flask import Blueprint, request, render_template, session, flash, redirect, url_for, jsonify
from passlib.hash import pbkdf2_sha256
from config.database import get_db_connection
from utils.helpers import log_user_activity, send_reset_email
from utils.decorators import login_required, admin_required, permission_required 

# Creamos el módulo de autenticación para agrupar todo lo relacionado con login y usuarios
auth_bp = Blueprint('auth', __name__)

# Importamos el modelo de Usuario para interactuar con la base de datos
from models.user import User

@auth_bp.route('/')
def index():
    """Esta es la puerta de entrada: Muestra la pantalla de inicio de sesión"""
    # Por seguridad, limpiamos cualquier sesión que haya quedado abierta antes de mostrar el login
    for key in list(session.keys()):
        if not key.startswith('_'):
            session.pop(key)
    return render_template('index.html')


@auth_bp.route('/auth', methods=['POST'])
def access():
    """Proceso de validación: Revisa si el nombre y la clave son correctos"""
    if request.method == 'POST':
        # Leemos lo que el usuario escribió en los campos de texto
        username = request.form['username']
        password = request.form['password']

        try:
            # 1. Verificar credenciales usando el Modelo
            user = User.get_by_username(username)
            
            if user:

                # Capturamos el último acceso guardado antes de actualizarlo con la entrada actual
                fecha_anterior = user.last_login
                
                # Verificación de seguridad: Si la clave es la genérica, pedimos que la cambie
                if user.password == 'newuser':
                     flash('Por favor, actualiza tu contraseña haciendo clic en "¿Olvidaste tu contraseña?"')
                     return redirect(url_for('auth.index'))

                # Verificar password
                if pbkdf2_sha256.verify(password, user.password):
                    log_user_activity(user.id, user.username, 'Inicio de sesión', 'El usuario inició sesión correctamente')

                    # SESIÓN
                    from datetime import datetime
                    session['logged'] = True
                    session['id'] = user.id
                    session['user'] = user.username
                    session['userAlias'] = user.username
                    session['fecha'] = datetime.now().strftime('%d/%m/%Y')
                    session['last_access'] = fecha_anterior  # <--- GUARDAR EN SESIÓN AQUÍ
                    session['isAdmin'] = 1 if user.is_admin else 0
                    
                    # ACTUALIZAR DB PARA LA PRÓXIMA VEZ
                    from config.database import get_db_connection
                    from utils.helpers import get_client_ip
                    ip = get_client_ip()
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET last_login = NOW(), last_ip = %s WHERE id = %s", (ip, user.id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    if user.name: session['name'] = user.name
                    if user.lastname: session['lastname'] = user.lastname

                    # ========== CARGAR ROLES Y PERMISOS ==========
                    try:
                        # 1. Obtener roles
                        roles, role_ids = User.get_user_roles(user.id)
                        session['user_roles'] = roles
                        session['user_role_ids'] = role_ids

                        # 2. Obtener permisos
                        user_permissions = User.get_user_permissions(role_ids, user.is_admin)

                        # 3. Fallback manual de permisos si la BD estaba vacía (Logica de negocio legacy)
                        if not user_permissions:
                             for role in session['user_roles']:
                                if role == 'administrador':
                                    user_permissions.extend(['all', 'create_provisions', 'view_provisions_details', 
                                                             'manage_users', 'export_data', 'configure_system'])
                                elif role == 'supervisor':
                                    user_permissions.extend(['create_provisions', 'view_provisions_details', 'export_data', 'view_history'])
                                elif role == 'usuario':
                                    user_permissions.extend(['view_history', 'create_provisions', 'view_provisions_details'])

                        # Eliminar duplicados
                        session['user_permissions'] = list(set(user_permissions))

                        # Para debugging
                        print(f"✅ {user.username} - Roles: {session['user_roles']}")
                        print(f"✅ {user.username} - Permisos: {session['user_permissions']}")

                    except Exception as e:
                        print(f"⚠️ Error cargando roles/permisos: {e}")
                        # Fallbacks mínimos
                        if session.get('isAdmin') == 1:
                            session['user_roles'] = ['administrador']
                            session['user_permissions'] = ['all']
                        else:
                            session['user_roles'] = ['usuario']
                            session['user_permissions'] = ['view_history']
                    # ========== FIN CARGAR ROLES Y PERMISOS ==========

                    # Registrar login
                    # Nota: log_user_activity sigue usando BD directa, pero está encapsulado en helpers
                    log_user_activity(user.id, user.username, 'Inicio de sesión', 'El usuario inició sesión correctamente')
                    
                    flash(f'Bienvenido {session.get("name", user.username)}')
                    return redirect(url_for('main.main_page'))
                else:
                    log_user_activity(None, username, 'Intento de inicio de sesión fallido', 'Contraseña incorrecta')
                    flash('Usuario o contraseña incorrectos')
                    return redirect(url_for('auth.index'))
            else:
                log_user_activity(None, username, 'Intento de inicio de sesión fallido', 'Usuario no existe')
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('auth.index'))

        except Exception as e:
            log_user_activity(None, username, 'Error en autenticación', f'Error: {str(e)}')
            flash('Error en el sistema: ' + str(e))
            return redirect(url_for('auth.index'))

    return render_template('index.html')


@auth_bp.route('/olvido', methods=['GET', 'POST'])
def olvido():
    """Recuperación de contraseña con envío de token"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        try:
            user_id = User.get_id_by_username_email(username, email)

            if user_id:
                # 1. Generar Token
                token = User.create_reset_token(user_id)
                # 2. Enviar Correo
                if send_reset_email(email, token):
                    log_user_activity(user_id, username, 'Solicitud de restablecimiento', 'Token de recuperación enviado por correo')
                    flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña. Revisa tu bandeja de entrada.')
                else:
                    flash('Error al generar el envío. Contacte a soporte.')
                
                return redirect(url_for('auth.index'))
            else:
                flash('Usuario o email incorrectos')
                return redirect(url_for('auth.olvido'))
        except Exception as e:
            flash('Error: '+str(e))
            return redirect(url_for('auth.olvido'))
            
    return render_template('olvido.html')


@auth_bp.route('/restablecer-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    """Restablecimiento de contraseña mediante token seguro"""
    try:
        # Validar Token
        user_id = User.validate_reset_token(token)
        
        if not user_id:
            flash('El enlace es inválido, ya fue usado o ha expirado.')
            return redirect(url_for('auth.olvido'))
            
        if request.method == 'POST':
            newPassword = request.form['password']
            confirmPassword = request.form.get('confirm_password')
            
            if confirmPassword and newPassword != confirmPassword:
                 flash('Las contraseñas no coinciden')
                 return render_template('nuevaclave.html', token=token)

            # Actualizar Password
            User.update_password_by_reset_id(user_id, newPassword)
            # Marcar token como usado
            User.mark_token_as_used(token)
            
            log_user_activity(user_id, None, 'Restablecimiento de contraseña', 'Contraseña actualizada mediante token')
            
            flash('Tu contraseña ha sido actualizada exitosamente.')
            return redirect(url_for('auth.index'))
            
        return render_template('nuevaclave.html', token=token)
        
    except Exception as e:
        flash('Error: '+str(e))
        return redirect(url_for('auth.index'))


@auth_bp.route('/nuevaclave', methods=['GET', 'POST'])
def nuevaclave():
    """Actualización de contraseña - CORREGIDO NOMBRE DE FUNCIÓN"""
    if 'resetid' not in session:
        flash('Solicitud inválida')
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        try:
            newPassword = request.form['password']
            User.update_password_by_reset_id(session['resetid'], newPassword)

            log_user_activity(session['resetid'], None, 'Restablecimiento de contraseña', 'Usuario restableció su contraseña')

            flash('Contraseña actualizada exitosamente')
            session.pop('resetid', None)
            return redirect(url_for('auth.index'))
        except Exception as e:
            flash('Error: '+str(e))
            return redirect(url_for('auth.index'))
            
    return render_template('nuevaclave.html')


# =============================================================================
# NUEVAS FUNCIONALIDADES PARA ADMINISTRADOR
# =============================================================================

@auth_bp.route('/admin/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """Redirigir a la nueva gestión unificada de roles y usuarios"""
    return redirect(url_for('roles.gestion_roles'))


@auth_bp.route('/admin/usuarios/eliminar/<int:user_id>', methods=['POST'])
@login_required
@admin_required  # Solo administradores
def eliminar_usuario(user_id):
    """Eliminar usuario (solo admin)"""
    # Evitar auto-eliminación
    if user_id == session.get('id'):
        return jsonify({
            'success': False,
            'message': 'No puede eliminarse a sí mismo'
        }), 400

    try:
        # 1. Verificar que el usuario existe
        usuario = User.get_by_id(user_id)

        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404

        username = usuario.username

        # 2. Obtener información para logging
        admin_id = session.get('id')
        admin_username = session.get('user')

        # 3. Eliminar usuario y sus datos relacionados
        User.delete_user_fully(user_id)

        # 4. Registrar la actividad
        log_user_activity(
            admin_id,
            admin_username,
            'Eliminación de usuario',
            f'Administrador {admin_username} eliminó al usuario {username} (ID: {user_id})'
        )

        print(f"✅ Usuario {username} eliminado exitosamente por {admin_username}")

        return jsonify({
            'success': True,
            'message': f'Usuario {username} eliminado exitosamente',
            'username': username
        })

    except Exception as e:
        print(f" Error eliminando usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al eliminar usuario: {str(e)}'
        }), 500


@auth_bp.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@login_required
@permission_required('create_users') # Cambiado de admin_required a permission_required
def crear_usuario_admin():
    """Crear nuevo usuario (solo admin)"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            email = request.form.get('email', '').strip()
            name = request.form.get('name', '').strip()
            lastname = request.form.get('lastname', '').strip()
            role_id = request.form.get('role_id', 3)  # 3 = usuario por defecto
            is_admin = 1 if request.form.get('is_admin') == 'on' else 0

            # Validaciones básicas
            if not username or not password or not email:
                flash('Username, password y email son obligatorios', 'error')
                return redirect(url_for('auth.crear_usuario_admin'))

            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return redirect(url_for('auth.crear_usuario_admin'))

            # Verificar si el usuario o email ya existen (usando helper existente o try/catch en create)
            # En este caso, User.create fallará si hay unique constraints, pero mejor verificar antes si es posible
            # o manejar la excepción. El código original verificaba explícitamente.
            if User.get_id_by_username_email(username, email, password):
                 flash('El username o email ya están registrados', 'error')
                 return redirect(url_for('auth.crear_usuario_admin'))

            # Crear usuario usando el modelo
            User.create(username, email, name, lastname, password, is_admin, role_id)

            # Registrar actividad
            log_user_activity(
                session.get('id'),
                session.get('user'),
                'Creación de usuario',
                f'Administrador {session.get("user")} creó al usuario {username}'
            )

            flash(f'Usuario {username} creado exitosamente', 'success')
            return redirect(url_for('auth.listar_usuarios'))

        except Exception as e:
            print(f" Error creando usuario: {e}")
            flash(f'Error al crear usuario: {str(e)}', 'error')
            return redirect(url_for('auth.crear_usuario_admin'))

    # GET: Mostrar formulario
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener roles disponibles (esto podría moverse a un RoleModel también, pero lo dejamos aquí por ahora o usamos SQL directo rapidito ya que no tenemos RoleModel aun)
        cursor.execute('SELECT id, name, descripcion FROM roles ORDER BY name')
        roles = cursor.fetchall()

        return render_template('admin/crear_usuario.html', roles=roles)

    except Exception as e:
        print(f" Error cargando roles: {e}")
        flash('Error al cargar formulario', 'error')
        return redirect(url_for('auth.listar_usuarios'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route('/admin/usuarios/cambiar_estado/<int:user_id>', methods=['POST'])
@login_required
@permission_required('create_users') 
def cambiar_estado_usuario(user_id):
    """Activar/desactivar usuario"""
    if user_id == session.get('id'):
        return jsonify({
            'success': False,
            'message': 'No puede cambiar su propio estado'
        }), 400

    data = request.json
    if not data or 'activo' not in data:
        return jsonify({
            'success': False,
            'message': 'Estado no especificado'
        }), 400

    nuevo_estado = data['activo']  # True/False

    try:
        # Verificar usuario
        user = User.get_by_id(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404

        username = user.username

        # Actualizar estado
        User.toggle_active_status(user_id, nuevo_estado)

        estado_texto = 'activado' if nuevo_estado else 'desactivado'

        # Log
        log_user_activity(
            session.get('id'),
            session.get('user'),
            f'Usuario {estado_texto}',
            f'Usuario {username} fue {estado_texto} (ID: {user_id})'
        )

        return jsonify({
            'success': True,
            'message': f'Usuario {username} {estado_texto} exitosamente',
            'activo': nuevo_estado
        })

    except Exception as e:
        print(f" Error cambiando estado: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@auth_bp.route('/exit')
def salir():
    """Cierre de sesión"""
    if 'id' in session and 'userAlias' in session:
        log_user_activity(session['id'], session['userAlias'], 'Cierre de sesión', 'Usuario cerró sesión')

    # Mantener solo las cookies de sesión de Flask
    session_keys = list(session.keys())
    for key in session_keys:
        if not key.startswith('_'):
            session.pop(key)

    return redirect(url_for('auth.index'))
