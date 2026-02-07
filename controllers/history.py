from flask import Blueprint, render_template, session, flash, redirect, url_for, request, send_file
from config.database import get_db_connection
from utils.decorators import login_required
from math import ceil
import pandas as pd
from io import BytesIO
from datetime import datetime

history_bp = Blueprint('history', __name__)


@history_bp.route('/historico')
@login_required
def history():
    """Histórico de provisiones (igual que en tu código original)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT semana, cant_aprobados, cant_rechazados, tipo_nomina, usuario_nombre, fecha_creacion FROM provisiones_historial ORDER BY fecha_creacion DESC')
        logs = cursor.fetchall()

        cursor.execute('SELECT SUM(cant_aprobados) as total_aprob, SUM(cant_rechazados) as total_rechazado FROM provisiones_historial')
        totales = cursor.fetchone()
        
        # Manejar caso de tabla vacía o valores NULL
        if totales and totales[0] is not None:
            totalAprob = float(totales[0])
        else:
            totalAprob = 0.0
            
        if totales and totales[1] is not None:
            totalRecha = float(totales[1])
        else:
            totalRecha = 0.0
        
        total = totalAprob + totalRecha

        if total > 0:
            totalAprob_angle = ceil((totalAprob/total)*360)
            totalRecha_angle = ceil((totalRecha/total)*360)
        else:
            totalAprob_angle = 0
            totalRecha_angle = 0

        session['total'] = total
        session['aprobados'] = totalAprob_angle
        session['rechazados'] = totalRecha_angle
        session['provLogs'] = logs if logs else []  # Lista vacía si no hay logs
        session['totalAprob'] = totalAprob
        session['totalRecha'] = totalRecha

        return render_template('historico.html')

    except Exception as e:
        print(f"❌ Error en historial: {e}")
        flash(f'Error al cargar el historial: {str(e)}', 'error')
        # En lugar de redirigir, mostrar página con datos vacíos
        session['total'] = 0
        session['aprobados'] = 0
        session['rechazados'] = 0
        session['provLogs'] = []
        session['totalAprob'] = 0
        session['totalRecha'] = 0
        return render_template('historico.html')
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

            # Ajustar anchos de columnas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Máximo 50 caracteres
                    worksheet.column_dimensions[column_letter].width = adjusted_width

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
