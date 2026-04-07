# controllers/roles.py - Módulo para gestionar quién puede hacer qué en el sistema
from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from config.database import get_db_connection
from utils.decorators import login_required, admin_required

# Módulo de Roles: Aquí el administrador decide los permisos de cada usuario
roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/admin/roles')
@login_required
@admin_required # Solo los administradores jefes pueden entrar aquí
def gestion_roles():
    conn = None
    cursor = None
    try:
        # Obtener todos los roles
        from models.roles import get_all_roles
        roles = get_all_roles()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener usuarios con sus roles y estado activo
        cursor.execute('''
            SELECT u.id, u.username, u.name, u.lastname, u.email, u.isAdmin, u.activo
            FROM users u
            ORDER BY u.name
        ''')
        usuarios = cursor.fetchall()
        
        # Procesar usuarios para incluir roles
        usuarios_con_info = []
        for usuario in usuarios:
            user_id = usuario[0]
            
            # Obtener roles de este usuario
            cursor.execute('''
                SELECT r.name FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = %s
            ''', (user_id,))
            
            roles_usuario = [r[0] for r in cursor.fetchall()]
            
            usuarios_con_info.append({
                'id': usuario[0],
                'username': usuario[1],
                'name': usuario[2],
                'lastname': usuario[3],
                'email': usuario[4],
                'isAdmin': usuario[5],
                'activo': usuario[6],
                'roles': roles_usuario
            })
        
        return render_template('gestion_roles.html', roles=roles, usuarios=usuarios_con_info)

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin.admin'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@roles_bp.route('/admin/roles/asignar/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def asignar_roles(user_id):
    """Asignar roles a un usuario"""
    if request.method == 'POST':
        try:
            from models.roles import update_user_roles
            
            # Obtener roles seleccionados
            roles_seleccionados = request.form.getlist('roles[]')
            
            # Actualizar roles
            if update_user_roles(user_id, roles_seleccionados):
                flash(' Roles actualizados correctamente', 'success')
            else:
                flash(' Error al actualizar roles', 'danger')
                
        except Exception as e:
            flash(f' Error: {str(e)}', 'danger')
    
    return redirect(url_for('roles.gestion_roles'))

@roles_bp.route('/admin/usuarios/toggle/<int:user_id>')
@login_required
@admin_required
def toggle_user(user_id):
    """Activar/Desactivar usuario"""
    if user_id == session.get('id'):
        flash('No puedes desactivar tu propia cuenta', 'warning')
        return redirect(url_for('roles.gestion_roles'))
        
    conn = None
    cursor = None
    try:
        from models.user import User
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT activo FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('roles.gestion_roles'))
            
        current_status = row[0]
        new_status = 0 if current_status == 1 else 1
        
        # Usar la función del modelo que ya maneja su propia conexión (pero cerrar la nuestra primero o usar una sola)
        # Para evitar problemas de bloqueo, cerramos esta conexión antes de llamar al modelo o pasamos el cursor
        cursor.close()
        conn.close()
        conn = None # Evitar doble cierre en finally
        cursor = None
        
        if User.toggle_active_status(user_id, new_status):
            msg = 'Usuario activado' if new_status == 1 else 'Usuario desactivado'
            flash(f' {msg} correctamente', 'success')
        else:
            flash(' Error al cambiar estado', 'danger')
    except Exception as e:
        flash(f' Error: {str(e)}', 'danger')
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        
    return redirect(url_for('roles.gestion_roles'))

@roles_bp.route('/admin/usuarios/update_config/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user_config(user_id):
    """Actualizar configuración de usuario (isAdmin y Roles)"""
    conn = None
    cursor = None
    try:
        is_admin = 1 if request.form.get('isAdmin') else 0
        roles_seleccionados = request.form.getlist('roles[]')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Actualizar isAdmin en la tabla users
        cursor.execute("UPDATE users SET isAdmin = %s WHERE id = %s", (is_admin, user_id))
        
        # 2. Actualizar Roles en la misma transacción (evitar deadlocks de conexiones paralelas)
        # Eliminamos roles actuales
        cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
        # Insertamos nuevos roles
        for rid in roles_seleccionados:
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, rid))
        
        conn.commit()
        flash(' Configuración de usuario actualizada correctamente', 'success')
    except Exception as e:
        if conn: conn.rollback()
        flash(f' Error: {str(e)}', 'danger')
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        
    return redirect(url_for('roles.gestion_roles'))