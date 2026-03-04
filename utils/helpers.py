from datetime import datetime
import io
import csv
from flask import Response
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from config.database import get_db_connection

def dateformat(value, format="%d/%m/%Y"):
    """Filtro personalizado para formato de fecha (igual que en tu código original)"""
    if value is None:
        return ""

    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return value

    if isinstance(value, datetime):
        return value.strftime(format)

    return value

import json
def from_json(value):
    """Convierte una cadena JSON a un objeto Python"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

def log_user_activity(user_id, username, activity_type, activity_details):
    ip = get_client_ip()
    """Registra actividades de usuario (igual que en tu código original)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Si user_id es None, intentar obtenerlo de la base de datos
        if user_id is None and username:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_id = user_data[0]

        # Insertar la actividad
        cursor.execute(
            'INSERT INTO user_activities (user_id, username, activity_type, activity_details, ip_address) VALUES (%s, %s, %s, %s, %s)',
            (user_id, username, activity_type, activity_details, ip)
        )
        conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def exportar_csv(datos_filas, headers, filename, titulo):
    """Exporta datos a formato CSV - Genérico"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Escribir título y encabezados
    writer.writerow([titulo])
    writer.writerow([f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
    writer.writerow([])
    writer.writerow(headers)

    # Escribir todas las filas recibidas
    for fila in datos_filas:
        writer.writerow(fila)

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}.csv"}
    )

    return response

def exportar_excel_generic(datos_filas, headers, filename, titulo):
    """Función auxiliar para exportar cualquier matriz de datos a Excel"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"

        # Título
        ws.merge_cells(f'A1:{chr(64+len(headers))}1')
        ws['A1'] = titulo
        ws['A1'].font = Font(size=14, bold=True)
        ws['A1'].alignment = Alignment(horizontal='center')

        # Headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

        # Datos
        for r_idx, row in enumerate(datos_filas, 4):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)

        # Ajustar columnas (máximo 50 caracteres para evitar columnas demasiado anchas)
        from openpyxl.utils import get_column_letter
        for col_idx, column_cells in enumerate(ws.columns, 1):
            max_length = 0
            column_letter = get_column_letter(col_idx)
            for cell in column_cells:
                try:
                    if cell.value:
                        length = len(str(cell.value))
                        if length > max_length:
                            max_length = length
                except: pass
            ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return Response(
            buffer.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment;filename={filename}.xlsx"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error en exportar_excel_generic: {e}")
        return f"Error al generar Excel: {str(e)}", 500

def get_client_ip():
    from flask import request
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr