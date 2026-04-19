# services/report_pdf.py
from flask import send_file
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
import os
import base64

# ============ FUNCIÓN PARA REPORTE DE EMPLEADOS ============
def generar_reporte_empleados_pdf(empleados):
    """Genera PDF con lista de empleados"""
    
    # Cargar logo en base64
    logo_path = os.path.join('static', 'images', 'Imagen1.jpg')
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    html_string = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte de Empleados SICEB</title>
        <meta charset="UTF-8">
        <style>
            @page {{ size: letter; margin: 2cm; }}
            body {{ font-family: 'Helvetica', sans-serif; font-size: 10pt; }}
            .membrete {{
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #cccccc;
            }}
            .logo {{
                display: inline-block;
                vertical-align: middle;
                margin-right: 15px;
            }}
            .logo img {{
                max-height: 10px;
            }}
            .info-empresa {{
                display: inline-block;
                vertical-align: middle;
                text-align: left;
            }}
            .empresa {{
                font-size: 11pt;
                font-weight: bold;
                color: #1a3a5f;
            }}
            .direccion, .contacto {{
                font-size: 8pt;
                color: #555555;
            }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .header h1 {{ color: #0d6efd; }}
            table {{ width: 100%;  border-radius:10px; margin-top: 20px; }}
            th {{ background-color: #0d6efd; color: white; padding: 8px; text-align: left; }}
            td {{ border: 1px solid #dee2e6; padding: 6px; }}
            .footer {{ text-align: center; font-size: 8pt; color: #6c757d; margin-top: 30px; border-top: 1px solid #dee2e6; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="membrete">
            <div class="logo">
                <img src="data:image/jpg;base64,{logo_base64}" alt="Logo">
            </div>
            <div class="info-empresa">
                <div class="empresa">L.P. LIDER POLLO, C.A. RIF J-30713528-0</div>
                <div class="direccion">Zona Industrial El Recreo Parcela Nro. 51 Vía Flor Amarillo, Valencia Edo. Carabobo</div>
                
                <div class="contacto">Telf: (0412) 801.7687 / 801.7887 - liderpolloca@gmail.com</div>
            </div>
        </div>
        <div class="header">
            <p>Reporte General de Empleados</p>
            <p>Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        <h3>Listado de Empleados</h3>
        <table>
            <thead><tr><th>ID</th><th>Cédula</th><th>Nombre Completo</th><th>Departamento</th><th>Estado</th></tr></thead>
            <tbody>
    """
    for emp in empleados:
        estado = "Activo" if emp.get('boolValidacion') == 1 else "Inactivo"
        html_string += f"<tr><td>{emp.get('id', '')}</td><td>{emp.get('cedula', '')}</td><td>{emp.get('nombre', '')} {emp.get('apellido', '')}</td><td>{emp.get('departamento', '')}</td><td>{estado}</td></tr>"
    
    html_string += """
            </tbody>
        </table>
        <div class="footer"><p>Reporte generado automáticamente por SICEB</p></div>
    </body>
    </html>
    """
    
    pdf_buffer = BytesIO()
    pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='reporte_empleados.pdf')


# ============ FUNCIÓN PARA REPORTE DE BENEFICIOS ============
def generar_reporte_beneficios_pdf(reporte, filtros=None):
    """Genera PDF con los resultados de beneficios filtrados"""
    
    # Cargar logo en base64
    logo_path = os.path.join('static', 'images', 'imagen1.jpg')
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    html_string = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte de Beneficios SICEB</title>
        <meta charset="UTF-8">
        <style>
            @page {{ size: landscape; margin: 1.5cm; }}
            body {{ font-family: 'Helvetica', sans-serif; font-size: 9pt; }}
            .membrete {{
                text-align: center;
                width:100px;
                height:100px;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #cccccc;             
            }}

            .logo {{
                display: inline-block;
                /*vertical-align: middle;*/
                margin-right: 15px;
            }}
            .logo img {{
                max-height: 3px;
            }}
            .info-empresa {{
                display: inline-block;
                vertical-align: middle;
                text-align: left;
            }}
            .empresa {{
                font-size: 12pt;
                font-weight: bold;
                color: #1a3a5f;
            }}
            .direccion, .contacto {{
                font-size: 8pt;
                color: #555555;
            }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .header h1 {{ color: #0d6efd; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background-color: #0d6efd; color: white; padding: 5px; text-align: center; border-radius:10px;}}
            td {{ border: 1px solid #dee2e6; padding: 6px; font-size:10px;  }}
            .footer {{ text-align: center; font-size: 8pt; color: #6c757d; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="membrete">
            <div class="logo">
                <img src="data:image/jpg;base64,{logo_base64}" alt="Logo">
            </div>
            <div class="info-empresa">
                <div class="empresa">L.P. LIDER POLLO, C.A. RIF J-30713528-0</div>
                <div class="direccion">Zona Industrial El Recreo Parcela Nro. 51 Vía Flor Amarillo, Valencia Edo. Carabobo</div>
                <div class="contacto">Telf: (0412) 801.7687 / 801.7887 - liderpolloca@gmail.com</div>
            </div>
        </div>
        <div class="header">
           
            <p>Reporte de Beneficios Individuales</p>
            <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Empleado</th>
                    <th>Cédula</th>
                    <th>Depto</th>
                    <th>Estatus</th>
                    <th>Productos</th>
                    <th>Fecha/Hora</th>
                    <th>Semana/Tipo</th>
                </tr>
            </thead>
            <tbody>
    """
    for item in reporte:
        estado = "Recibió" if item.get('recibio') else "No recibió"
        productos_list = item.get('productos_list', [])
        productos = ', '.join([f"{p[1]} {p[0]}" for p in productos_list]) if productos_list else ''
        fecha = item.get('fecha_entrega')
        fecha_str = fecha.strftime('%d/%m/%Y %H:%M') if fecha and hasattr(fecha, 'strftime') else str(fecha) if fecha else ''
        semana_tipo = f"S{item.get('semana')} - {item.get('tipo_nomina')}"
        
        html_string += f"""
            <tr>
                <td>{item.get('nombre_completo', '')}</td>
                <td>{item.get('cedula', '')}</td>
                <td>{item.get('departamento', '')}</td>
                <td>{estado}</td>
                <td>{productos}</td>
                <td>{fecha_str}</td>
                <td>{semana_tipo}</td>
            </tr>
        """
    
    html_string += """
            </tbody>
        </table>
        <div class="footer">
            <p>Reporte generado por SICEB - Sistema de Control de Beneficios</p>
        </div>
    </body>
    </html>
    """
    
    pdf_buffer = BytesIO()
    pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='reporte_beneficios.pdf')