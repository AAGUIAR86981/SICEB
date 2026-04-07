from flask import Blueprint, render_template, session, flash, redirect, url_for, request, send_file
from config.database import get_db_connection
from utils.decorators import login_required
from math import ceil
import pandas as pd
from io import BytesIO
from datetime import datetime
from openpyxl.utils import get_column_letter

# Módulo de Historial: Aquí se guardan y consultan todos los registros de entregas pasadas
history_bp = Blueprint('history', __name__)


@history_bp.route('/historico')
@login_required # Solo usuarios que iniciaron sesión
def history():
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

@history_bp.route('/descargar_historico_excel')
@login_required
def descargar_historico_excel():
    """Descarga el historial de provisiones en formato Excel con datos para gráficos"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener todos los datos del historial
        cursor.execute('''
            SELECT
                semana,
                tipo_nomina,
                cant_aprobados,
                cant_rechazados,
                usuario_nombre,
                fecha_creacion
            FROM provisiones_historial
            ORDER BY fecha_creacion DESC
        ''')

        logs = cursor.fetchall()

        # Calcular estadísticas por tipo de nómina
        cursor.execute('''
            SELECT
                tipo_nomina,
                SUM(cant_aprobados) as total_aprobados,
                SUM(cant_rechazados) as total_rechazados,
                COUNT(*) as total_provisiones
            FROM provisiones_historial
            GROUP BY tipo_nomina
        ''')

        stats_nominas = cursor.fetchall()

        # Crear DataFrames
        df_logs = pd.DataFrame(logs, columns=[
            'Semana', 'Tipo_Nómina', 'Aprobados', 'Rechazados', 'Usuario', 'Fecha_Provisión'
        ])

        # Convertir tipos de nómina
        df_logs['Tipo_Nómina'] = df_logs['Tipo_Nómina'].apply(
            lambda x: 'Semanal' if x == '1' else 'Quincenal' if x == '2' else x
        )

        df_stats = pd.DataFrame(stats_nominas, columns=[
            'Tipo_Nómina', 'Total_Aprobados', 'Total_Rechazados', 'Total_Provisiones'
        ])

        df_stats['Tipo_Nómina'] = df_stats['Tipo_Nómina'].apply(
            lambda x: 'Semanal' if x == '1' else 'Quincenal' if x == '2' else x
        )

        # Estadísticas generales
        total_aprobados = df_logs['Aprobados'].sum()
        total_rechazados = df_logs['Rechazados'].sum()
        total_general = total_aprobados + total_rechazados

        stats_generales = {
            'Métrica': [
                'Total de Provisiones',
                'Total Empleados Aprobados',
                'Total Empleados Rechazados',
                'Total General de Empleados',
                'Porcentaje de Aprobación',
                'Porcentaje de Rechazo',
                'Fecha de Generación'
            ],
            'Valor': [
                len(df_logs),
                total_aprobados,
                total_rechazados,
                total_general,
                f"{(total_aprobados/total_general*100):.1f}%" if total_general > 0 else "0%",
                f"{(total_rechazados/total_general*100):.1f}%" if total_general > 0 else "0%",
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ]
        }

        df_generales = pd.DataFrame(stats_generales)

        # Crear archivo Excel en memoria
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja 1: Datos completos
            df_logs.to_excel(writer, sheet_name='Provisiones_Detalladas', index=False)

            # Hoja 2: Estadísticas generales
            df_generales.to_excel(writer, sheet_name='Estadísticas_Generales', index=False)

            # Hoja 3: Estadísticas por nómina
            df_stats.to_excel(writer, sheet_name='Estadísticas_por_Nómina', index=False)

            # Hoja 4: Datos para gráficos
            datos_graficos = {
                'Categoría': ['Aprobados', 'Rechazados'],
                'Total_General': [total_aprobados, total_rechazados],
                'Semanal_Aprobados': [df_stats[df_stats['Tipo_Nómina'] == 'Semanal']['Total_Aprobados'].iloc[0] if any(df_stats['Tipo_Nómina'] == 'Semanal') else 0, 0],
                'Semanal_Rechazados': [0, df_stats[df_stats['Tipo_Nómina'] == 'Semanal']['Total_Rechazados'].iloc[0] if any(df_stats['Tipo_Nómina'] == 'Semanal') else 0],
                'Quincenal_Aprobados': [df_stats[df_stats['Tipo_Nómina'] == 'Quincenal']['Total_Aprobados'].iloc[0] if any(df_stats['Tipo_Nómina'] == 'Quincenal') else 0, 0],
                'Quincenal_Rechazados': [0, df_stats[df_stats['Tipo_Nómina'] == 'Quincenal']['Total_Rechazados'].iloc[0] if any(df_stats['Tipo_Nómina'] == 'Quincenal') else 0]
            }

            df_graficos = pd.DataFrame(datos_graficos)
            df_graficos.to_excel(writer, sheet_name='Datos_para_Gráficos', index=False)

            # Ajustar anchos de columnas para todas las hojas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for col_idx, column_cells in enumerate(worksheet.columns, 1):
                    max_length = 0
                    column_letter = get_column_letter(col_idx)
                    for cell in column_cells:
                        try:
                            if cell.value:
                                length = len(str(cell.value))
                                if length > max_length:
                                    max_length = length
                        except:
                            pass
                    worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

        output.seek(0)

        # Nombre del archivo
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        filename = f"historial_provisiones_completo_{fecha_actual}.xlsx"

        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        flash(f'Error al generar el archivo Excel: {str(e)}', 'error')
        return redirect(url_for('history.history'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
