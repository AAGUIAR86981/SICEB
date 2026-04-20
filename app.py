import pymysql
pymysql.install_as_MySQLdb()
import os
from dotenv import load_dotenv

# Puerta de Entrada (app.py): Este archivo es el corazón que pone a marchar todo el sistema administrativo

# Paso 1: Cargamos nuestras configuraciones secretas (base de datos, contraseñas, etc.)
load_dotenv()

from flask import Flask, send_from_directory
from config.database import init_db_tables
from utils.helpers import dateformat, from_json

# Paso 2: Importamos cada uno de los módulos (Blueprints) que controlan diferentes partes del sistema
from controllers.auth import auth_bp
from controllers.main import main_bp
from controllers.provision import provision_bp
from controllers.history import history_bp
from controllers.admin import admin_bp
from controllers.roles import roles_bp
from controllers.combos import combos_bp
from controllers.employees import employees_bp
from controllers.products import products_bp
from controllers.reports import reports_bp

# Paso 3: Creamos el motor de la página web (Flask) y le decimos dónde están las pantallas (templates)
app = Flask(__name__, template_folder='templates')

# Seguridad Vital: Usamos una 'llave maestra' única para que nadie pueda hackear las sesiones de los usuarios
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise ValueError("¡ERROR CRÍTICO! No encontramos la SECRET_KEY. Sin ella, el sistema no puede funcionar seguro.")

# Paso 4: Registramos todas las secciones en el motor para que el sistema las reconozca
app.register_blueprint(auth_bp)        # Módulo de Entrada y Salida
app.register_blueprint(main_bp)        # Página Principal (Dashboard)
app.register_blueprint(provision_bp)   # Gestión de Provisiones
app.register_blueprint(history_bp)     # Reportes e Historial
app.register_blueprint(admin_bp)       # Panel de Administrador
app.register_blueprint(roles_bp)       # Control de Cargos
app.register_blueprint(combos_bp)      # Gestión de Combos de Productos
app.register_blueprint(employees_bp)   # Base de datos de Trabajadores
app.register_blueprint(products_bp)    # Catálogo de Productos

app.register_blueprint(reports_bp)     # Generación de reportes en excel y pdf

# Paso 5: Agregamos herramientas visuales para las pantallas (como formatear fechas correctamente)
app.jinja_env.filters['dateformat'] = dateformat
app.jinja_env.filters['from_json'] = from_json


# Ruta para el icono de la pestaña del navegador (Favicon)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'OIP.png', mimetype='image/png')

# Paso 6: Configuramos los 'Ayudantes de Pantalla' que estarán disponibles en todo el sistema
@app.context_processor
def utility_processor():
    """Estas funciones las usamos dentro de los archivos HTML para revisar si el usuario puede ver un botón o no"""
    from utils.template_helpers import (
        check_permission,
        check_role,
        get_user_roles,
        get_user_permissions
    )
    from datetime import datetime
    return {
        'check_permission': check_permission,
        'check_role': check_role,
        'get_user_roles': get_user_roles,
        'get_user_permissions': get_user_permissions,
        'now': datetime.now()
    }

# Arrancamos el sistema: Primero preparamos la base de datos y luego encendemos el servidor web
if __name__ == '__main__':
    print("Iniciando SICEB - Sistema de Control y Entregas de Beneficios...")
    init_db_tables() # Asegura que las tablas existan antes de empezar
    app.run(debug=True) # Enciende el motor con modo de detección de errores activado
