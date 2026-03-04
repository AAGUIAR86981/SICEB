from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.employee import Employee
from utils.decorators import login_required, permission_required
from utils.helpers import log_user_activity, exportar_excel_generic, exportar_csv
import math
from datetime import datetime

employees_bp = Blueprint('employees', __name__, url_prefix='/empleados')

@employees_bp.route('/')
@login_required
@permission_required('manage_employees')
def list_employees():
    search = request.args.get('search', '')
    tipo_nomina = request.args.get('tipo_nomina', '')
    estado = request.args.get('estado', '')
    page = int(request.args.get('page', 1))
    per_page = 15
    offset = (page - 1) * per_page

    employees = Employee.get_all_with_filters(
        search=search, 
        tipo_nomina=tipo_nomina, 
        estado=estado if estado else None,
        limit=per_page,
        offset=offset
    )
    
    total_count = Employee.count_with_filters(
        search=search, 
        tipo_nomina=tipo_nomina, 
        estado=estado if estado else None
    )
    
    total_pages = math.ceil(total_count / per_page)

    return render_template('employees/list.html', 
                          employees=employees, 
                          search=search, 
                          tipo_nomina=tipo_nomina, 
                          estado=estado,
                          page=page,
                          total_pages=total_pages)

@employees_bp.route('/exportar/<formato>')
@login_required
@permission_required('manage_employees')
def exportar_empleados(formato):
    """Exporta la lista de empleados actual según filtros"""
    try:
        search = request.args.get('search', '')
        tipo_nomina = request.args.get('tipo_nomina', '')
        estado = request.args.get('estado', '')

        # Obtener TODOS los empleados que coinciden con los filtros (sin paginación)
        employees = Employee.get_all_with_filters(
            search=search, 
            tipo_nomina=tipo_nomina, 
            estado=estado if estado else None,
            limit=2000, # Límite razonable
            offset=0
        )

        headers = ['ID Empleado', 'Cédula', 'Nombre', 'Apellido', 'Departamento', 'Nómina', 'Estado']
        datos = []
        for emp in employees:
            nomina_txt = "Semanal" if str(emp.get('tipoNomina')) == '1' else "Quincenal"
            estado_txt = "Activo" if emp.get('boolValidacion') else "Inactivo"
            datos.append([
                emp.get('id_empleado'),
                emp.get('cedula'),
                emp.get('nombre'),
                emp.get('apellido'),
                emp.get('departamento'),
                nomina_txt,
                estado_txt
            ])

        filename = f"lista_empleados_{datetime.now().strftime('%Y%m%d')}"
        titulo = "LISTADO DE EMPLEADOS"

        if formato == 'csv':
            return exportar_csv(datos, headers, filename, titulo)
        return exportar_excel_generic(datos, headers, filename, titulo)

    except Exception as e:
        print(f"Error exportando empleados: {e}")
        flash(f'Error al exportar el listado de empleados: {str(e)}', 'error')
        return redirect(url_for('employees.list_employees', **request.args))

@employees_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@permission_required('manage_employees')
def create_employee():
    if request.method == 'POST':
        data = {
            'id_empleado': request.form.get('id_empleado'),
            'cedula': request.form.get('cedula'),
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'departamento': request.form.get('departamento'),
            'tipoNomina': int(request.form.get('tipoNomina', 1)),
            'boolValidacion': 1 if request.form.get('activo') else 0
        }
        
        employee_id = Employee.create(data)
        if employee_id:
            log_user_activity(session['id'], session['userAlias'], 'Creación de empleado', f"Creó al empleado {data['nombre']} {data['apellido']} (CI: {data['cedula']})")
            flash('Empleado creado exitosamente', 'success')
            return redirect(url_for('employees.list_employees'))
        else:
            flash('Error al crear el empleado. Verifique si la Cédula o ID ya existen.', 'error')
            
    departments = Employee.get_unique_departments()
    return render_template('employees/form.html', employee=None, departments=departments)

@employees_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('manage_employees')
def edit_employee(id):
    employee = Employee.get_by_id(id)
    if not employee:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('employees.list_employees'))
        
    if request.method == 'POST':
        data = {
            'id_empleado': request.form.get('id_empleado'),
            'cedula': request.form.get('cedula'),
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'departamento': request.form.get('departamento'),
            'tipoNomina': int(request.form.get('tipoNomina')),
            'boolValidacion': 1 if request.form.get('activo') else 0
        }
        
        result = Employee.update(id, data)
        if result is True:
            log_user_activity(session['id'], session['userAlias'], 'Edición de empleado', f"Editó al empleado {data['nombre']} {data['apellido']} (ID: {id})")
            flash('Empleado actualizado exitosamente', 'success')
            return redirect(url_for('employees.list_employees'))
        elif result == 'DUPLICATE_CEDULA':
            flash('Error: La Cédula ya está registrada en otro empleado.', 'error')
        elif result == 'DUPLICATE_ID':
            flash('Error: La Ficha (ID Empleado) ya está registrada.', 'error')
        else:
            flash('Error crítico al actualizar el empleado. Verifique los datos.', 'error')
            
    departments = Employee.get_unique_departments()
    return render_template('employees/form.html', employee=employee, departments=departments)

@employees_bp.route('/toggle/<int:id>')
@login_required
@permission_required('manage_employees')
def toggle_status(id):
    if Employee.toggle_status(id):
        log_user_activity(session['id'], session['userAlias'], 'Cambio de estado empleado', f"Cambió el estado del empleado ID: {id}")
        flash('Estado del empleado actualizado', 'success')
    else:
        flash('Error al cambiar el estado del empleado', 'error')
    return redirect(url_for('employees.list_employees'))

@employees_bp.route('/ver/<int:id>')
@login_required
@permission_required('manage_employees')
def view_employee(id):
    employee = Employee.get_by_id(id)
    if not employee:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('employees.list_employees'))
    return render_template('employees/view.html', employee=employee)
