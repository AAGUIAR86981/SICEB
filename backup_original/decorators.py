from functools import wraps
from flask import session, flash, redirect, url_for


def login_required(f):
    """Decorador para verificar autenticación (igual que en tu código original)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged' not in session or not session['logged']:
            flash('Por favor inicie sesión')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorador para verificar permisos de administrador (igual que en tu código original)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'isAdmin' not in session or session['isAdmin'] != 1:
            flash('Acceso restringido a administradores')
            return redirect(url_for('main.main_page'))
        return f(*args, **kwargs)
    return decorated_function
