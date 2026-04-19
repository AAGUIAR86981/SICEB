# controllers/reports.py
from flask import Blueprint, session, redirect, url_for
from services.empleado_excel import generar_reporte_empleados_excel
from services.report_pdf import generar_reporte_empleados_pdf
from config.database import get_db_connection

reports_bp = Blueprint('reports', __name__)

def obtener_empleados():
    """Obtiene la lista de empleados desde la base de datos"""
    conn = get_db_connection()
    if not conn:
        print("Error: No se pudo conectar a la base de datos")
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, cedula, nombre, apellido, 
                   COALESCE(departamento, 'Sin asignar') as departamento,
                   boolValidacion
            FROM empleados 
            ORDER BY nombre
        """)
        empleados = cursor.fetchall()
        cursor.close()
        conn.close()
        return empleados
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return []

#@reports_bp.route('/exportar/empleados/excel')
#def exportar_empleados_excel():
 #   if not session.get('logged'):
  #      return redirect(url_for('auth.login'))
    
   # empleados = obtener_empleados()
    #if not empleados:
     #   return "No hay empleados para exportar", 404
    
    #return generar_reporte_empleados_excel(empleados)

@reports_bp.route('/exportar/empleados/pdf')
def exportar_empleados_pdf():
    if not session.get('logged'):
        return redirect(url_for('auth.login'))
    
    empleados = obtener_empleados()
    if not empleados:
        return "No hay empleados para exportar", 404
    
    return generar_reporte_empleados_pdf(empleados)