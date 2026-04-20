from flask import Blueprint, render_template, session, flash, redirect, url_for, request, Response
from utils.decorators import login_required, permission_required
from utils.helpers import dateformat, from_json, log_user_activity, exportar_csv, exportar_excel_generic
from config.database import get_db_connection
from datetime import datetime
import logging
import json
import requests
from models.provision import Provision
from models.employee import Employee
from models.combos_model import ComboModel

# Configuramos el sistema de registro (logs) específicamente para el proceso de entrega de beneficios
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
f_handler = logging.FileHandler('provision_debug.log', mode='w')
f_handler.setLevel(logging.INFO)
f_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_formatter)
logger.addHandler(f_handler)

# Creamos el módulo de 'provision' para organizar todas las rutas relacionadas con las entregas
provision_bp = Blueprint('provision', __name__)

def check_system_time_integrity():
    """Seguridad: Verifica que la hora de la computadora coincida con la hora real de Internet.
    Esto evita que alguien cambie la fecha del PC para intentar adelantar una entrega de combos.
    """
    try:
        # Consultamos el reloj mundial oficial para Caracas
        api_url = "http://worldtimeapi.org/api/timezone/America/Caracas"
        response = requests.get(api_url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            internet_timestamp = data['unixtime']
            system_timestamp = datetime.now().timestamp()
            
            # Calculamos la diferencia en segundos
            diff = abs(system_timestamp - internet_timestamp)
            
            # Si hay más de 5 minutos de diferencia, sospechamos que el reloj fue alterado
            if diff > 300: 
                logger.error(f"¡ALERTA DE SEGURIDAD! El reloj del servidor está desfasado por {diff} segundos.")
                return False, f"Se detectó un posible cambio manual en la fecha ({diff/60:.1f} min de diferencia)"
            
            return True, "Sincronizado"
            
    except requests.exceptions.SSLError:
        logger.error("Error de SSL detectado: Posible manipulación de fecha.")
        return False, "Error de Seguridad: Reloj del sistema inválido"
    except Exception as e:
        logger.warning(f"Error de red/API en validación: {e}")
        # Solo permitimos si es un error de conexión genérico
        return True, "Verificación omitida (Sin Internet)"

    return True, "Desconocido"

def validar_regla_pollo(productos_list):
    MAX_POLLO = 4
    for nombre, cantidad in productos_list:
        if "POLLO" in nombre.upper():
            if int(cantidad) > MAX_POLLO:
                raise ValueError(f"Alerta: No se permiten más de {MAX_POLLO} pollos por empleado.")


# =============================================================================
# RUTA 1: REALIZAR PROVISIÓN (SOLO ADMIN Y SUPERVISOR)
# =============================================================================
@provision_bp.route('/provision', methods=['GET', 'POST'])
@login_required
@permission_required('create_provisions') 
def make_provision():
    if request.method == 'POST':
        return procesar_provision_post()
    else:
        return mostrar_formulario_provision_get()
    if request.method == 'POST':
        return procesar_provision_post()
    else:
        return mostrar_formulario_provision_get()

def mostrar_formulario_provision_get():
    try:
        # Calcular ambos períodos: semanal (ISO week) y quincenal (1 o 2)
        semana_iso, quincena = Provision.get_type_and_week()

        # Guardar ambos períodos en sesión para mostrarlos en el formulario
        session['fecha'] = datetime.now().strftime('%A, %d / %m / %Y')
        session['semana_iso'] = semana_iso
        session['quincena'] = quincena

        # Verificar cuáles nóminas ya fueron generadas hoy
        semanal_ya_hecha = Provision.exists(semana_iso, '1')
        quincenal_ya_hecha = Provision.exists(quincena, '2')

        combos = Provision.get_active_combos()
        return render_template(
            'realizarP.html',
            combos=combos,
            semana_iso=semana_iso,
            quincena=quincena,
            semanal_ya_hecha=semanal_ya_hecha,
            quincenal_ya_hecha=quincenal_ya_hecha
        )
    except Exception as e:
        logger.error(f"Error en mostrar_formulario_provision_get: {e}")
        flash('Error al cargar el formulario de provisión', 'error')
        return redirect(url_for('auth.index'))

def procesar_provision_post():
    try:
        tipo_nomina = request.form.get('Nomina')
        if not tipo_nomina:
            flash('Debe seleccionar el tipo de nómina', 'error')
            return redirect(url_for('provision.make_provision'))

        # Calcular ambos períodos y usar el que corresponde al tipo seleccionado
        semana_iso, quincena = Provision.get_type_and_week()
        # '1' = Semanal (usa número de semana ISO), '2' = Quincenal (usa 1 o 2)
        periodo_actual = semana_iso if tipo_nomina == '1' else quincena
        
        # Verificar si YA se generó este tipo específico hoy (semanal y quincenal son independientes)
        if Provision.exists(periodo_actual, tipo_nomina):
            nomina_lbl = 'Semanal' if tipo_nomina == '1' else 'Quincenal'
            flash(f'Error: Ya se ha generado la provisión de nómina {nomina_lbl} para el día de hoy.', 'error')
            return redirect(url_for('provision.make_provision'))
        
        # --- ESTRATEGIA: No-Retorno (Verificar que no vamos atrás en el tiempo) ---
        last_date = Provision.get_last_provision_date()
        if last_date:
            ahora = datetime.now()
            # Si el servidor dice que hoy es ANTES que la última provisión guardada
            if ahora < last_date:
                flash(f"BLOQUEO DE SEGURIDAD: La fecha del servidor ({ahora.strftime('%d/%m/%Y')}) es anterior al último registro ({last_date.strftime('%d/%m/%Y')}). No puede viajar al pasado.", "error")
                return redirect(url_for('provision.make_provision'))

        # Validar integridad del reloj antes de cualquier operación CRÍTICA
        is_sync, time_msg = check_system_time_integrity()
        if not is_sync:
            flash(f"PROCESO BLOQUEADO: {time_msg}. El reloj del servidor ha sido alterado.", "error")
            return redirect(url_for('provision.make_provision'))

        tipo_prov_slug = 'semanal' if tipo_nomina == '1' else 'quincenal'
        
        semProv = periodo_actual
        tipo_provision = tipo_prov_slug

        combo_id = request.form.get('combo_id')
        productos = []
        if combo_id and combo_id != 'standard':
            selected_combo = ComboModel.get_combo_by_id(int(combo_id))
            if selected_combo:
                productos = [(item['nombre'], str(item['cantidad'])) for item in selected_combo['items']]

        if not productos:
            flash('Debe seleccionar un combo válido.', 'warning')
            return redirect(url_for('provision.make_provision'))

        asignados = Employee.get_all(tipo_nomina, 'activo', 1000)
        user_permissions = session.get('user_permissions', [])
        can_view_unapproved = 'all' in user_permissions or 'view_unapproved' in user_permissions or session.get('isAdmin') == 1
        
        invalidados = []
        if can_view_unapproved:
            invalidados = Employee.get_all(tipo_nomina, 'inactivo', 1000)
        
        Provision.save_log(semProv, tipo_nomina, session.get('userAlias', 'Usuario'), len(asignados), len(invalidados))

        try:
            provision_id = Provision.save_history(
                tipo_provision, semProv, tipo_nomina, productos,
                asignados, invalidados, session.get('id'),
                session.get('userAlias', 'Usuario')
            )
        except mariadb.Error as e:
            if e.errno == 1062:
                flash(f"ERROR CRÍTICO: La provisión para la Semana {semProv} ({tipo_prov_slug}) ya existe en la base de datos.", "error")
            else:
                flash(f"Error de base de datos al guardar: {str(e)}", "error")
            return redirect(url_for('provision.make_provision'))
        
        if provision_id:
            session.update({
                'asignados': asignados,
                'invalidados': invalidados,
                'nomina': tipo_nomina,
                'semana': semProv,
                'semProv': semProv,
                'tipo_provision': tipo_provision,
                'fecha': datetime.now().strftime('%A, %d / %m / %Y'),
                'combo': productos,
                'provExiste': False,
                'current_provision_id': provision_id
            })
            flash('Provisión creada exitosamente', 'success')
            return render_template('resultados_provision.html')
        else:
            flash('Error técnico al guardar en historial.', 'error')
            return redirect(url_for('provision.make_provision'))
    except Exception as e:
        logger.error(f"Error crítico en procesar_provision_post: {e}")
        flash('Error al procesar la provisión', 'error')
        return redirect(url_for('provision.make_provision'))
    

# =============================================================================
# RUTAS DE EXPORTACIÓN
# =============================================================================
@provision_bp.route('/exportar/<tipo_empleado>/<formato>')
@login_required
@permission_required('create_provisions')
def exportar_empleados(tipo_empleado, formato):
    try:
        provision_id = session.get('current_provision_id')
        raw_data = []
        
        if provision_id:
            status_filter = 1 if tipo_empleado == 'asignados' else 0
            raw_data = Provision.get_beneficiary_report({'provision_id': provision_id, 'recibio': status_filter})
        
        if not raw_data:
            raw_data = session.get('asignados', []) if tipo_empleado == 'asignados' else session.get('invalidados', [])

        if not raw_data:
            flash('No hay datos recientes para exportar. Realice una provisión primero.', 'warning')
            return redirect(url_for('provision.make_provision'))

        headers = ['Cédula', 'Nombre', 'Apellido', 'Departamento', 'ID Empleado', 'Estatus']
        datos_normalizados = []
        estatus_label = "ASIGNADO" if tipo_empleado == 'asignados' else "INVALIDADO"
        
        for emp in raw_data:
            # Manejar tanto diccionarios como objetos si fuera necesario
            nombre = emp.get('nombre', '')
            apellido = emp.get('apellido', '')
            
            # Si vienen del reporte de beneficiarios, el nombre está completo
            if not nombre and not apellido:
                nombre_completo = emp.get('nombre_completo', '')
                partes = nombre_completo.split(' ', 1) if ' ' in nombre_completo else [nombre_completo, '']
                nombre = partes[0]
                apellido = partes[1] if len(partes) > 1 else ''
            
            datos_normalizados.append([
                emp.get('cedula', ''),
                nombre,
                apellido,
                emp.get('departamento', ''),
                emp.get('id_empleado', 'N/A'),
                estatus_label
            ])

        filename = f"empleados_{tipo_empleado}_{datetime.now().strftime('%Y%m%d')}"
        titulo = f"REPORTE DE EMPLEADOS {estatus_label}S"

        if formato == 'csv':
            return exportar_csv(datos_normalizados, headers, filename, titulo)
        return exportar_excel_generic(datos_normalizados, headers, filename, titulo)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('provision.make_provision'))

@provision_bp.route('/historial_provisiones')
@login_required
def historial_provisiones():
    try:
        raw_history = Provision.get_history(100)
        historial = []
        for row in raw_history:
            productos = from_json(row[4]) if isinstance(row[4], str) else (row[4] if row[4] else [])
            datos_completos = from_json(row[5]) if isinstance(row[5], str) else (row[5] if row[5] else {})
            
            historial.append({
                'id': row[0], 'tipo_provision': row[1] or 'N/A', 'semana': row[2] or 'N/A',
                'tipo_nomina': row[3] or 'N/A', 'productos': productos,
                'datos_completos': datos_completos, 'fecha_creacion': row[6],
                'usuario_nombre': row[7] or 'Usuario desconocido'
            })
        return render_template('historial_provisiones.html', historial=historial, 
                             es_admin=(session.get('isAdmin') == 1))
    except Exception as e:
        logger.error(f"Error historial: {e}")
        flash('Error al cargar historial', 'error')
        return render_template('historial_provisiones.html', historial=[])

@provision_bp.route('/consultar_beneficios')
@login_required
def consultar_beneficios():
    try:
        filters = {
            'cedula': request.args.get('cedula'), 'nombre': request.args.get('nombre'),
            'semana': request.args.get('semana'), 'fecha': request.args.get('fecha'),
            'recibio': request.args.get('recibio'), 'tipo_nomina': request.args.get('tipo_nomina')
        }
        recibio_int = int(filters['recibio']) if filters['recibio'] in ['0', '1'] else None
        report_filters = filters.copy()
        report_filters['recibio'] = recibio_int
        
        # Mapear tipo_nomina de ID a texto para la consulta en provisiones_historial
        tipo_nomina_map = {'1': 'Semanal', '2': 'Quincenal'}
        if filters['tipo_nomina'] in tipo_nomina_map:
            report_filters['tipo_nomina'] = tipo_nomina_map[filters['tipo_nomina']]
        
        reporte_completo = Provision.get_beneficiary_report(report_filters)
        for row in reporte_completo:
            row['productos_list'] = from_json(row['productos']) if isinstance(row['productos'], str) else (row['productos'] if row['productos'] else [])

        # ── Paginación ──
        per_page    = 10
        page        = max(1, int(request.args.get('page', 1)))
        total       = len(reporte_completo)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page        = min(page, total_pages)
        start       = (page - 1) * per_page
        reporte     = reporte_completo[start:start + per_page]

        return render_template(
            'consultar_beneficios.html',
            reporte=reporte,
            filters=filters,
            page=page,
            total_pages=total_pages,
            total=total,
        )
    except Exception as e:
        logger.error(f"Error beneficios: {e}")
        flash('Error al cargar beneficios', 'error')
        return redirect(url_for('provision.historial_provisiones'))


# Agrega estas funciones al final de controllers/provision.py

@provision_bp.route('/exportar/beneficios/excel')
def exportar_beneficios_excel():
    """Exporta a Excel los resultados filtrados de beneficios"""
    if not session.get('logged'):
        return redirect(url_for('auth.login'))
    
    # Obtener filtros
    cedula = request.args.get('cedula', '')
    nombre = request.args.get('nombre', '')
    semana = request.args.get('semana', '')
    tipo_nomina = request.args.get('tipo_nomina', '')
    recibio = request.args.get('recibio', '')
    fecha = request.args.get('fecha', '')
    
    from services.report_excel import generar_reporte_beneficios_excel
    from models.provision import obtener_reporte_beneficios_completo
    
    reporte = obtener_reporte_beneficios_completo(
        cedula=cedula,
        nombre=nombre,
        semana=semana,
        tipo_nomina=tipo_nomina,
        recibio=recibio,
        fecha=fecha
    )
    
    return generar_reporte_beneficios_excel(reporte, request.args)

@provision_bp.route('/exportar/beneficios/pdf')
def exportar_beneficios_pdf():
    """Exporta a PDF los resultados filtrados de beneficios"""
    if not session.get('logged'):
        return redirect(url_for('auth.login'))
    
    cedula = request.args.get('cedula', '')
    nombre = request.args.get('nombre', '')
    semana = request.args.get('semana', '')
    tipo_nomina = request.args.get('tipo_nomina', '')
    recibio = request.args.get('recibio', '')
    fecha = request.args.get('fecha', '')
    
    from services.report_pdf import generar_reporte_beneficios_pdf
    from models.provision import obtener_reporte_beneficios_completo
    
    reporte = obtener_reporte_beneficios_completo(
        cedula=cedula,
        nombre=nombre,
        semana=semana,
        tipo_nomina=tipo_nomina,
        recibio=recibio,
        fecha=fecha
    )
    
    return generar_reporte_beneficios_pdf(reporte, request.args)

@provision_bp.route('/exportar_mis_empleados_asignados_excel')
@login_required
def exportar_mis_empleados_asignados_excel():
    """Exporta los empleados ASIGNADOS a Excel con formato personalizado"""
    print("=" * 60)
    print("🎯 FUNCIÓN NUEVA Y ÚNICA - ASIGNADOS")
    print("=" * 60)
    
    try:
        asignados = session.get('asignados', [])
        print(f"Total asignados: {len(asignados)}")
        
        if not asignados:
            flash('No hay empleados asignados para exportar', 'warning')
            return redirect(url_for('provision.make_provision'))
        
        from services.resultado_provision_excel import generar_reporte_asignados_excel
        return generar_reporte_asignados_excel(asignados, "ASIGNADOS")
        
    except Exception as e:
        print(f"Error: {e}")
        flash('Error al generar Excel', 'error')
        return redirect(url_for('provision.make_provision'))


@provision_bp.route('/exportar_mis_empleados_invalidados_excel')
@login_required
def exportar_mis_empleados_invalidados_excel():
    """Exporta los empleados INVALIDADOS a Excel con formato personalizado"""
    print("=" * 60)
    print("🎯 FUNCIÓN NUEVA Y ÚNICA - INVALIDADOS")
    print("=" * 60)
    
    try:
        invalidados = session.get('invalidados', [])
        print(f"Total invalidados: {len(invalidados)}")
        
        if not invalidados:
            flash('No hay empleados invalidados para exportar', 'warning')
            return redirect(url_for('provision.make_provision'))
        
        from services.resultado_provision_excel import generar_reporte_asignados_excel
        return generar_reporte_asignados_excel(invalidados, "INVALIDADOS")
        
    except Exception as e:
        print(f"Error: {e}")
        flash('Error al generar Excel', 'error')
        return redirect(url_for('provision.make_provision'))
