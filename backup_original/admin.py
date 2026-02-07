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
            isSupervisor = int(request.form.get('isSupervisor', 0))

            cursor.execute('INSERT INTO users(username, email, name, lastname, isAdmin, isSupervisor) VALUES (%s,%s,%s,%s,%s,%s)', 
                           (username, email, name, lastname, isAdmin, isSupervisor))
            conn.commit()

            log_user_activity(
                session['id'],
                session['userAlias'],
                'Creación de usuario',
                f'El administrador creó el usuario: {username} ({name} {lastname})'
            )

            flash('Registration successful')

        # Obtener historial de inicios de sesión
        cursor.execute('SELECT loggedAt, username, userID FROM user_logs ORDER BY loggedAt DESC')
        userlogs = cursor.fetchall()
        session['userLogs'] = userlogs if userlogs else []

        # Obtener actividades de usuarios
        cursor.execute('SELECT activity_date, username, user_id, activity_type, activity_details FROM user_activities ORDER BY activity_date DESC')
        user_activities = cursor.fetchall()
        session['userActivities'] = user_activities if user_activities else []

        # Obtener conteo de usuarios
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]

        # Obtener conteo de creaciones de usuarios
        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE activity_type LIKE '%Creación%'")
        creaciones_count = cursor.fetchone()[0]

        return render_template('admin.html', user_count=user_count, creaciones_count=creaciones_count)

    except Exception as e:
        flash('Error: ' + str(e))
        if conn:
            conn.rollback()
        return redirect(url_for('admin.admin'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
