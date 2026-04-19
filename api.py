# api.py - API para la app móvil
from flask import Flask, jsonify, request, session, send_file
from functools import wraps
from config.database import get_db_connection
from models.user import User
from models.employee import Employee
from models.provision import Provision
from models.combos_model import ComboModel
import os
from dotenv import load_dotenv

load_dotenv()


api_app = Flask(__name__)
api_app.secret_key = os.environ.get('SECRET_KEY', 'clave-api-segura')

# Decorador para autenticación con token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        # Aquí validas el token (por ahora simple)
        return f(*args, **kwargs)
    return decorated

@api_app.route('/')
def home():
    return jsonify({
        'mensaje': 'API de SICEB funcionando',
        'endpoints': {
            'login': 'POST /api/login',
            'dashboard': 'GET /api/dashboard',
            'empleados': 'GET /api/empleados',
            'historial': 'GET /api/historial'
        }
    })


# ============== ENDPOINTS PARA APP MÓVIL ==============

# 1. Login
@api_app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.get_by_username(username)
    if user and User.verify_credentials(username, password):
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name or '',
                'isAdmin': user.is_admin or 0
            }
        })
    return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

# 2. Dashboard / Estadísticas
@api_app.route('/api/dashboard', methods=['GET'])
@token_required
def api_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total empleados
    cursor.execute("SELECT COUNT(*) as total FROM empleados")
    total_empleados = cursor.fetchone()
    
    # Empleados activos
    cursor.execute("SELECT COUNT(*) as activos FROM empleados WHERE boolValidacion = 1")
    activos = cursor.fetchone()
    
    # Departamentos
    cursor.execute("SELECT COUNT(DISTINCT departamento_id) as deptos FROM empleados WHERE departamento_id IS NOT NULL")
    deptos = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_empleados': total_empleados['total'] if total_empleados else 0,
        'empleados_activos': activos['activos'] if activos else 0,
        'total_departamentos': deptos['deptos'] if deptos else 0
    })

# 3. Listar empleados
@api_app.route('/api/empleados', methods=['GET'])
@token_required
def api_empleados():
    tipo_nomina = request.args.get('tipo', None)
    empleados = Employee.get_all(tipo_nomina, None)
    
    return jsonify([{
        'id': e.get('id'),
        'cedula': e.get('cedula'),
        'nombre': e.get('nombre', ''),
        'apellido': e.get('apellido', ''),
        'departamento': e.get('departamento', 'Sin Depto'),
        'estado': 'Activo' if e.get('boolValidacion') else 'Inactivo'
    } for e in empleados])

# 4. Historial de provisiones
@api_app.route('/api/historial', methods=['GET'])
@token_required
def api_historial():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, tipo_provision, semana, fecha_creacion, cant_aprobados
        FROM provisiones_historial
        ORDER BY fecha_creacion DESC
        LIMIT 20
    """)
    historial = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(historial)

# 5. Procesar provisión
@api_app.route('/api/provision', methods=['POST'])
@token_required
def api_provision():
    data = request.get_json()
    tipo_nomina = data.get('tipo_nomina') # '1' o '2'
    combo_id = data.get('combo_id')
    user_id = data.get('user_id', 1) # Usamos ID del payload
    user_name = data.get('user_name', 'Móvil User')
    
    semana_iso, quincena = Provision.get_type_and_week()
    periodo_actual = semana_iso if tipo_nomina == '1' else quincena
    tipo_prov_slug = 'semanal' if tipo_nomina == '1' else 'quincenal'
    
    if Provision.exists(periodo_actual, tipo_nomina):
        return jsonify({'success': False, 'error': f'Ya se ha generado la provisión para la jornada actual.'}), 400
        
    combo = ComboModel.get_combo_by_id(int(combo_id))
    productos = [(item['nombre'], str(item['cantidad'])) for item in combo['items']] if combo else []
    
    asignados = Employee.get_all(tipo_nomina, 'activo', 1000)
    invalidados = Employee.get_all(tipo_nomina, 'inactivo', 1000)
    
    try:
        Provision.save_history(tipo_prov_slug, periodo_actual, tipo_nomina, productos, asignados, invalidados, user_id, user_name)
        return jsonify({'success': True, 'message': f'Provisión {tipo_prov_slug} guardada exitosamente.', 'aprobados': len(asignados)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 6. Cumpleaños próximos
@api_app.route('/api/cumpleanos', methods=['GET'])
@token_required
def api_cumpleanos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, nombre, apellido, fecha_nacimiento
            FROM empleados
            WHERE fecha_nacimiento IS NOT NULL
            AND DATE_FORMAT(fecha_nacimiento, '%m-%d') BETWEEN DATE_FORMAT(CURDATE(), '%m-%d')
            AND DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 7 DAY), '%m-%d')
            ORDER BY DATE_FORMAT(fecha_nacimiento, '%m-%d')
        """)
        cumpleanos = cursor.fetchall()
    except Exception as e:
        # Prevent 500 error if column fecha_nacimiento does not exist yet
        print("Warning: /api/cumpleanos failed, possibly missing column. Error:", e)
        cumpleanos = []
    finally:
        cursor.close()
        conn.close()
    
    return jsonify(cumpleanos)

# 7. Recuperacion de Clave
@api_app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    data = request.get_json()
    user_id = User.get_id_by_username_email(data.get('username'), data.get('email'))
    if user_id:
        token = User.create_reset_token(user_id)
        return jsonify({'success': True, 'message': 'Token listo.', 'token': token})
    return jsonify({'success': False, 'error': 'Credenciales no encontradas'}), 404

# 8. Catálogo de Combos
@api_app.route('/api/combos', methods=['GET'])
def api_combos():
    return jsonify(Provision.get_active_combos())

    # Agrega esta ruta al final de tus endpoints, antes del if __name__
@api_app.route('/mobile')
def mobile_app():
    return send_file('templates/mobile_app.html')

if __name__ == '__main__':
    # host='0.0.0.0' permite que dispositivos externos (como tu teléfono en el mismo WiFi) puedan conectarse.
    api_app.run(host='0.0.0.0', debug=True, port=5002)