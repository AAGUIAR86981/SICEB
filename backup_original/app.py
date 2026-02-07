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

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(provision_bp)
app.register_blueprint(history_bp)
app.register_blueprint(admin_bp)

# Registrar filtro de plantillas
app.jinja_env.filters['dateformat'] = dateformat

if __name__ == '__main__':
    init_db_tables()
    app.run(debug=True)
