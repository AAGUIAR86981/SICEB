from flask import Blueprint, request, render_template, session, flash, redirect, url_for
from config.database import get_db_connection
from utils.decorators import admin_required
from utils.helpers import log_user_activity
# En controllers/main.py y controllers/admin.py:
from utils.decorators import login_required, admin_required
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    """Panel de administración (igual que en tu código original)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            name = request.form['name']
            lastname = request.form['lastname']
            isAdmin = int(request.form.get('isAdmin', 0))

            # Obtener roles seleccionados (nuevo)
            roles_seleccionados = request.form.getlist('roles[]')

            cursor.execute('INSERT INTO users(username, email, name, lastname, isAdmin) VALUES (%s,%s,%s,%s,%s)', 
                           (username, email, name, lastname, isAdmin))

            user_id = cursor.lastrowid # Obtener el ID del nuevo usuario

            # Asignación de roles al nuevo usuario (nuevo)
            for rol_id in roles_seleccionados:
                cursor.execute('''
                    INSERT INTO user_roles (user_id, role_id, assigned_at) VALUES (%s, %s, NOW())''', (user_id, rol_id)
                )

                # Si es Admin, asegurar rol administrador
                if isAdmin == 1:
                    cursor.execute("SELECT id FROM roles WHERE name = 'administrador'")
                    admin_role = cursor.fetchone()
                    if admin_role:
                        cursor.execute(
                            'INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, %s)',
                            (user_id, admin_role[0])
                        )

            conn.commit()

            log_user_activity(
                session['id'],
                session['userAlias'],
                'Creación de usuario',
                f'Creó el usuario: {username} ({name} {lastname}) con roles: {roles_seleccionados}'
            )

            flash('Ususario creado exitosamente')

        # Obtener historial de inicios de sesión
        cursor.execute("SELECT activity_date, username, user_id FROM user_activities WHERE activity_type = 'Inicio de sesión' ORDER BY activity_date DESC LIMIT 50")
        userlogs = cursor.fetchall()

        # Obtener actividades de usuarios
        cursor.execute('SELECT activity_date, username, user_id, activity_type, activity_details FROM user_activities ORDER BY activity_date DESC LIMIT 100')
        user_activities = cursor.fetchall()

        # Obtener conteo de usuarios
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]

        # Obtener conteo de creaciones de usuarios
        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE activity_type LIKE '%Creación%'")
        creaciones_count = cursor.fetchone()[0]

        return render_template('admin.html', 
                               user_count=user_count, 
                               creaciones_count=creaciones_count,
                               userlogs=userlogs,
                               user_activities=user_activities)

    except Exception as e:
        flash('Error: ' + str(e))
        if conn:
            conn.rollback()
        return redirect(url_for('admin.admin'))
    finally:
        if cursor:
            cursor.close()
        if conn: conn.close()

@admin_bp.route('/admin/auditoria')
@admin_required
def auditoria():
    """Muestra el resumen de auditoría de empleados"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consultar la vista v_resumen_auditoria
        cursor.execute("SELECT * FROM v_resumen_auditoria ORDER BY total_cambios DESC LIMIT 10")
        auditoria_data = cursor.fetchall()
        
        # Consultar logs detallados (empleadosaudit)
        cursor.execute("""
            SELECT a.*, e.nombre, e.apellido 
            FROM empleadosaudit a 
            JOIN empleados e ON a.employee_id = e.id 
            ORDER BY a.changed_at DESC 
            LIMIT 100
        """)
        detalles_audit = cursor.fetchall()
        
        return render_template('db_reports.html', auditoria=auditoria_data, detalles_audit=detalles_audit)
        
    except Exception as e:
        flash(f'Error al cargar auditoría: {e}', 'error')
        return redirect(url_for('admin.admin'))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
