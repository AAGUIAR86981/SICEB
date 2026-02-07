# controllers/auth.py - VERSIÓN ORIGINAL COMPLETA
from flask import Blueprint, request, render_template, session, flash, redirect, url_for
from passlib.hash import pbkdf2_sha256
from config.database import get_db_connection
from utils.helpers import log_user_activity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Página principal de login"""
    [session.pop(key) for key in list(session.keys()) if not key.startswith('_')]
    return render_template('index.html')


@auth_bp.route('/auth', methods=['POST'])
def access():
    """Autenticación de usuario - VERSIÓN ORIGINAL (sin roles)"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT * FROM users WHERE username = %s',
                (username,)
            )
            fetch = cursor.fetchone()

            if fetch is not None:
                if fetch[3] == 'newuser':
                    flash('Please update your password by clicking "Forgot Password"')
                    return redirect(url_for('auth.index'))

                checkHash = pbkdf2_sha256.verify(password, fetch[3])

                if checkHash:
                    log_user_activity(fetch[0], fetch[1], 'Inicio de sesión', 'El usuario inició sesión correctamente')

                    # SOLO ESTO ORIGINAL - NO AGREGAR roles
                    session['logged'] = True
                    session['id'] = fetch[0]
                    session['userAlias'] = fetch[1]
                    session['isAdmin'] = fetch[4]

                    try:
                        cursor.execute(
                            'INSERT INTO user_logs (userID, username) VALUES (%s, %s)',
                            (fetch[0], fetch[1])
                        )
                        conn.commit()
                    except Exception as log_error:
                        print(f"Error al registrar en user_logs: {log_error}")
                        conn.rollback()

                    return redirect(url_for('main.main_page'))
                else:
                    log_user_activity(None, username, 'Intento de inicio de sesión fallido', 'Contraseña incorrecta')
                    flash('Usuario o contraseña incorrectos')
                    return redirect(url_for('auth.index'))

        except Exception as e:
            log_user_activity(None, username, 'Error en autenticación', f'Error: {str(e)}')
            flash('Error en el sistema: ' + str(e))
            return redirect(url_for('auth.index'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('index.html')


@auth_bp.route('/olvido', methods=['GET', 'POST'])
def olvido():
    """Recuperación de contraseña"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT id FROM users WHERE username = %s AND email = %s',
                (username, email)
            )
            userExists = cursor.fetchone()

            if userExists is not None:
                session['resetid'] = userExists[0]
                log_user_activity(userExists[0], username, 'Solicitud de restablecimiento', 'Usuario solicitó restablecer contraseña')
                return redirect(url_for('auth.update_password'))
            else:
                flash('Usuario o email incorrectos')
                return redirect(url_for('auth.olvido'))
        except Exception as e:
            flash('Error: '+str(e))
            return redirect(url_for('auth.olvido'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('olvido.html')


@auth_bp.route('/nuevaclave', methods=['GET', 'POST'])
def update_password():
    """Actualización de contraseña"""
    if 'resetid' not in session:
        flash('Solicitud inválida')
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            newPassword = request.form['password']
            newPassword = pbkdf2_sha256.hash(newPassword)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password=%s WHERE id=%s', (newPassword, session['resetid']))
            conn.commit()

            log_user_activity(session['resetid'], None, 'Restablecimiento de contraseña', 'Usuario restableció su contraseña')

            flash('Password updated successfully')
            session.pop('resetid', None)
            return redirect(url_for('auth.index'))
        except Exception as e:
            flash('Error: '+str(e))
            return redirect(url_for('auth.index'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('nuevaclave.html')


@auth_bp.route('/exit')
def salir():
    """Cierre de sesión"""
    if 'id' in session and 'userAlias' in session:
        log_user_activity(session['id'], session['userAlias'], 'Cierre de sesión', 'Usuario cerró sesión')
    session.clear()
    return redirect(url_for('auth.index'))