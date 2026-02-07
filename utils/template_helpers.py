# utils/template_helpers.py
from flask import session

def check_permission(permission_code):
    """Verifica permiso para usar en plantillas - VERSIÓN SEGURA"""
    # Solo verificar en sesión, SIN llamar a base de datos
    if 'logged' not in session or not session['logged']:
        return False
    
    # Si es admin, tiene todos los permisos
    if session.get('isAdmin') == 1:
        return True
    
    # Verificar en sesión
    if 'user_permissions' in session:
        if permission_code in session['user_permissions']:
            return True
        # Si admin tiene 'all', también tiene todos
        if 'all' in session['user_permissions']:
            return True
    
    return False

def check_role(role_name):
    """Verifica rol para usar en plantillas - VERSIÓN SEGURA"""
    if 'logged' not in session or not session['logged']:
        return False
    
    # Si es admin y busca rol administrator
    if session.get('isAdmin') == 1 and role_name == 'administrator':
        return True
    
    # Verificar en sesión
    if 'user_roles' in session:
        return role_name in session['user_roles']
    
    return False

def get_user_roles():
    """Obtiene roles del usuario para plantillas"""
    if 'logged' in session and session['logged'] and 'user_roles' in session:
        return session['user_roles']
    return []

def get_user_permissions():
    """Obtiene permisos del usuario para plantillas"""
    if 'logged' in session and session['logged'] and 'user_permissions' in session:
        return session['user_permissions']
    return []
