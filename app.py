import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from config.database import init_db_tables
from utils.helpers import dateformat

# Importar blueprints
from controllers.auth import auth_bp
from controllers.main import main_bp
from controllers.provision import provision_bp
from controllers.history import history_bp
from controllers.admin import admin_bp
from controllers.roles import roles_bp
from controllers.combos import combos_bp
from controllers.employees import employees_bp
from controllers.products import products_bp

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(provision_bp)
app.register_blueprint(history_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(combos_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(products_bp)

# Registrar filtro de plantillas
from utils.helpers import from_json
app.jinja_env.filters['dateformat'] = dateformat
app.jinja_env.filters['from_json'] = from_json

# Ruta explícita para el favicon
from flask import send_from_directory
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'OIP.png', mimetype='image/png')


# app.py - AGREGAR ESTO AL FINAL (antes de if __name__)

# ========== CONTEXTO PARA PLANTILLAS ==========
@app.context_processor
def utility_processor():
    """Agrega funciones a todas las plantillas"""
    # Importar aquí para evitar problemas circulares
    from utils.template_helpers import (
        check_permission,
        check_role,
        get_user_roles,
        get_user_permissions
    )

    return {
        'check_permission': check_permission,
        'check_role': check_role,
        'get_user_roles': get_user_roles,
        'get_user_permissions': get_user_permissions
    }



if __name__ == '__main__':
    init_db_tables()
    app.run(debug=True)
