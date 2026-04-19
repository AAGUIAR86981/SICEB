from flask import Blueprint, render_template, session, flash, redirect, url_for, request, send_file
from config.database import get_db_connection
from utils.decorators import login_required
from math import ceil
import pandas as pd
from io import BytesIO
from datetime import datetime
from openpyxl.utils import get_column_letter
from services.historico_excel import generar_reporte_historico_excel


# Módulo de Historial: Aquí se guardan y consultan todos los registros de entregas pasadas
history_bp = Blueprint('history', __name__)


@history_bp.route('/historico')
@login_required # Solo usuarios que iniciaron sesión
def history():
    print("=" * 60)
    print("services/historico_excel.py")
    print("=" * 60)

    """Muestra la bitácora de todas las entregas realizadas con resúmenes visuales (gráficos)"""
    conn = None
    cursor = None
    try:
        # --- CONFIGURACIÓN DE PÁGINAS ---
        # Si hay muchos registros, los mostramos de 10 en 10
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener total para paginación
        cursor.execute('SELECT COUNT(*) as total FROM provisiones_historial')
        total_records = cursor.fetchone()['total']
        total_pages = ceil(total_records / per_page) if total_records > 0 else 1

        # Obtener logs paginados
        cursor.execute('''
            SELECT semana, cant_aprobados, cant_rechazados, tipo_nomina, usuario_nombre, fecha_creacion, ip_address 
            FROM provisiones_historial 
            ORDER BY fecha_creacion DESC 
            LIMIT %s OFFSET %s
        ''', (per_page, offset))
        logs = cursor.fetchall()

        # Obtener totales generales para el dashboard
        cursor.execute('SELECT SUM(cant_aprobados) as total_aprob, SUM(cant_rechazados) as total_rechazado FROM provisiones_historial')
        totales = cursor.fetchone()
        
        # Manejar caso de tabla vacía o valores NULL
        totalAprob = float(totales['total_aprob']) if totales and totales['total_aprob'] is not None else 0.0
        totalRecha = float(totales['total_rechazado']) if totales and totales['total_rechazado'] is not None else 0.0
        total = totalAprob + totalRecha

        if total > 0:
            totalAprob_angle = ceil((totalAprob/total)*360)
            totalRecha_angle = ceil((totalRecha/total)*360)
        else:
            totalAprob_angle = 0
            totalRecha_angle = 0

        # Pasar datos al contexto del template
        return render_template('historico.html', 
                             logs=logs, 
                             total=total, 
                             aprobados_angle=totalAprob_angle, 
                             rechazados_angle=totalRecha_angle,
                             totalAprob=totalAprob,
                             totalRecha=totalRecha,
                             page=page,
                             total_pages=total_pages)

    except Exception as e:
        print(f" Error en historial: {e}")
        flash(f'Error al cargar el historial: {str(e)}', 'error')
        return render_template('historico.html', 
                             logs=[], 
                             total=0, 
                             aprobados_angle=0, 
                             rechazados_angle=0,
                             totalAprob=0,
                             totalRecha=0,
                             page=1,
                             total_pages=1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@history_bp.route('/descargar-historico-excel')
@login_required
def descargar_historico_excel():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener TODOS los datos del historial
        cursor.execute('''
            SELECT semana, tipo_nomina, cant_aprobados, cant_rechazados, 
                   usuario_nombre, fecha_creacion, ip_address
            FROM provisiones_historial
            ORDER BY fecha_creacion DESC
        ''')
        logs = cursor.fetchall()
        
        # Calcular estadísticas totales
        totalAprob = sum(log.get('cant_aprobados', 0) for log in logs)
        totalRecha = sum(log.get('cant_rechazados', 0) for log in logs)
        total = totalAprob + totalRecha
        total_records = len(logs)
        
        # Usar el nuevo servicio personalizado
        return generar_reporte_historico_excel(logs, total_records, totalAprob, totalRecha, total)
        
    except Exception as e:
        print(f"Error al generar Excel: {e}")
        flash(f'Error al generar el archivo Excel: {str(e)}', 'error')
        return redirect(url_for('history.history'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()