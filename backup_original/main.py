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

        return render_template('main.html')

    except Exception as e:
        flash('Error: '+str(e))
        return redirect(url_for('auth.index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
