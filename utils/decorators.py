# utils/decorators.py - VERSIÓN CORRECTA
from functools import wraps
from flask import session, flash, redirect, url_for


def login_required(f):
    """Decorador para verificar autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged' not in session or not session['logged']:
            flash('Por favor inicie sesión')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorador para verificar permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'isAdmin' not in session or session['isAdmin'] != 1:
            flash('Acceso restringido a administradores')
            return redirect(url_for('main.main_page'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*required_roles):
    """Decorador para verificar que el usuario tenga AL MENOS UNO de los roles requeridos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged' not in session or not session['logged']:
                flash('Por favor inicie sesión')
                return redirect(url_for('auth.index'))

            # Si es admin, tiene acceso a todo
            if session.get('isAdmin') == 1:
                return f(*args, **kwargs)

            # Verificar roles en sesión
            user_roles = session.get('user_roles', [])

            # Verificar si tiene alguno de los roles requeridos
            for required_role in required_roles:
                if required_role in user_roles:
                    return f(*args, **kwargs)

            user_permissions = session.get('user_permissions', [])

            if 'create_provisions' in user_permissions or 'all' in user_permissions:
                return f(*args, **kwargs)

            flash('No tiene el rol necesario para acceder')
            return redirect(url_for('main.main_page'))
        return decorated_function
    return decorator


# Decorador alternativo si prefieres usar permisos
def permission_required(permission_code):
    """Decorador para verificar permisos específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged' not in session or not session['logged']:
                flash('Por favor inicie sesión')
                return redirect(url_for('auth.index'))

            # Verificar si es admin (acceso completo)
            if session.get('isAdmin') == 1:
                return f(*args, **kwargs)

            # Verificar permiso en sesión
            if 'user_permissions' in session:
                if permission_code in session['user_permissions'] or 'all' in session['user_permissions']:
                    return f(*args, **kwargs)

            flash('No tiene permisos para acceder a esta funcionalidad')
            return redirect(url_for('main.main_page'))
        return decorated_function
    return decorator
