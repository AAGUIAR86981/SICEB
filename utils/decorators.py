from functools import wraps
from flask import session, flash, redirect, url_for

# Protectores de rutas: Estos 'porteros' aseguran que solo las personas correctas entren a cada parte del sistema

def login_required(f):
    """Este protector asegura que la persona haya iniciado sesión antes de ver una pantalla"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si no hay registro de que inició sesión, lo mandamos de vuelta al login
        if 'logged' not in session or not session['logged']:
            flash('Por favor, ingresa con tu usuario y clave para continuar')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Este protector solo deja pasar a las personas con cargo de Administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si no es administrador (nivel 1), lo devolvemos a la página principal
        if 'isAdmin' not in session or session['isAdmin'] != 1:
            flash('Lo sentimos, esta sección solo es para administradores')
            return redirect(url_for('main.main_page'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*required_roles):
    """Este protector verifica que el usuario tenga al menos uno de los cargos permitidos para entrar"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Primero verificamos si está logueado
            if 'logged' not in session or not session['logged']:
                flash('Primero debes iniciar sesión')
                return redirect(url_for('auth.index'))

            # Si es un administrador total, no le ponemos trabas, puede pasar
            if session.get('isAdmin') == 1:
                return f(*args, **kwargs)

            # Revisamos qué cargos tiene la persona en su sesión actual
            user_roles = session.get('user_roles', [])

            # Si tiene alguno de los cargos que pedimos, lo dejamos pasar
            for required_role in required_roles:
                if required_role in user_roles:
                    return f(*args, **kwargs)

            # También revisamos si tiene permisos específicos de 'todopoderoso' o creación
            user_permissions = session.get('user_permissions', [])
            if 'create_provisions' in user_permissions or 'all' in user_permissions:
                return f(*args, **kwargs)

            flash('Tu cargo actual no tiene permiso para entrar a esta sección')
            return redirect(url_for('main.main_page'))
        return decorated_function
    return decorator


def permission_required(permission_code):
    """Este protector es muy detallista: revisa si el usuario tiene permiso para una ACCIÓN específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged' not in session or not session['logged']:
                flash('Inicia sesión para realizar esta acción')
                return redirect(url_for('auth.index'))

            # Los administradores siempre tienen permiso para todo
            if session.get('isAdmin') == 1:
                return f(*args, **kwargs)

            # Buscamos si en su lista de permisos está el código que necesitamos (ej: 'borrar_usuario')
            if 'user_permissions' in session:
                if permission_code in session['user_permissions'] or 'all' in session['user_permissions']:
                    return f(*args, **kwargs)

            flash('No tienes permiso para realizar esta operación específica')
            return redirect(url_for('main.main_page'))
        return decorated_function
    return decorator
