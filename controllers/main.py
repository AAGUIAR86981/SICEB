from flask import Blueprint, render_template, session, flash, redirect, url_for
from config.database import get_db_connection
from utils.decorators import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/main')
@login_required
def main_page():
    """Página principal después del login (igual que en tu código original)"""
    conn = None
    cursor = None
    try:
        currentUserID = session['id']
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT CONCAT(name, " ", lastname) AS full_name FROM users WHERE id=%s', (currentUserID,))
        currentUser = cursor.fetchone()
        session['user'] = currentUser[0] if currentUser else session['userAlias']

        # Obtener estadísticas para el dashboard
        from models.employee import Employee
        from models.provision import Provision
        
        # Resumen general (usando tipoNomina=1 para estadísticas generales si aplica)
        resumen_semanal = Employee.get_payroll_summary(1)
        resumen_quincenal = Employee.get_payroll_summary(2)
        
        stats = {
            'total_empleados': (resumen_semanal[0] or 0) + (resumen_quincenal[0] or 0),
            'empleados_activos': (resumen_semanal[1] or 0) + (resumen_quincenal[1] or 0),
            'total_departamentos': len(Employee.get_unique_departments())
        }
        
        # Últimas 5 provisiones
        ultimas_provisiones = Provision.get_history(5)

        return render_template('main.html', stats=stats, ultimas_provisiones=ultimas_provisiones)

    except Exception as e:
        flash('Error: '+str(e))
        return redirect(url_for('auth.index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@main_bp.route('/test-roles')
@login_required
def test_roles():
    """Ruta para probar sistema de roles"""
    return render_template('test_roles.html')