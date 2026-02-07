from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.combos_model import ComboModel
from utils.decorators import login_required
from utils.template_helpers import check_permission

combos_bp = Blueprint('combos', __name__, url_prefix='/combos')

@combos_bp.route('/')
@login_required
def list_combos():
    if not check_permission('manage_combos'):
        flash('No tienes permiso para gestionar combos.')
        return redirect(url_for('main.main_page'))
        
    combos = ComboModel.get_all_combos()
    return render_template('combos/list.html', combos=combos)

@combos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def create_combo():
    if not check_permission('manage_combos'):
        flash('No tienes permiso para gestionar combos.')
        return redirect(url_for('main.main_page'))
        
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        # Procesar items dinámicos
        items = []
        # Esperamos campos como producto_1, cantidad_1, producto_2, cantidad_2...
        # Una forma más robusta es buscar todas las claves que empiecen con 'producto_'
        # Procesar items dinámicos agrupando por producto_id
        items_dict = {}
        for key in request.form:
            if key.startswith('producto_'):
                idx = key.split('_')[1]
                p_id = request.form.get(f'producto_{idx}')
                p_qty = request.form.get(f'cantidad_{idx}')
                
                if p_id and p_qty:
                    pid = int(p_id)
                    qty = int(p_qty)
                    if pid in items_dict:
                        items_dict[pid] += qty
                    else:
                        items_dict[pid] = qty
        
        items = [{'producto_id': k, 'cantidad': v} for k, v in items_dict.items()]
        
        if not items:
            flash('Debes agregar al menos un producto al combo.')
        else:
            success = ComboModel.create_combo(nombre, descripcion, items)
            if success:
                flash('Combo creado exitosamente.')
                return redirect(url_for('combos.list_combos'))
            else:
                flash('Error al crear el combo.')
                
    catalog = ComboModel.get_catalog()
    return render_template('combos/form.html', combo=None, catalog=catalog)

@combos_bp.route('/editar/<int:combo_id>', methods=['GET', 'POST'])
@login_required
def edit_combo(combo_id):
    if not check_permission('manage_combos'):
        flash('No tienes permiso para gestionar combos.')
        return redirect(url_for('main.main_page'))
        
    combo = ComboModel.get_combo_by_id(combo_id)
    if not combo:
        flash('Combo no encontrado.')
        return redirect(url_for('combos.list_combos'))
        
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        activo = 1 if request.form.get('activo') else 0
        
        # Procesar items dinámicos agrupando por producto_id
        items_dict = {}
        for key in request.form:
            if key.startswith('producto_'):
                idx = key.split('_')[1]
                p_id = request.form.get(f'producto_{idx}')
                p_qty = request.form.get(f'cantidad_{idx}')
                
                if p_id and p_qty:
                    pid = int(p_id)
                    qty = int(p_qty)
                    if pid in items_dict:
                        items_dict[pid] += qty
                    else:
                        items_dict[pid] = qty
        
        items = [{'producto_id': k, 'cantidad': v} for k, v in items_dict.items()]
        
        if not items:
            flash('Debes agregar al menos un producto al combo.')
        else:
            success = ComboModel.update_combo(combo_id, nombre, descripcion, activo, items)
            if success:
                flash('Combo actualizado exitosamente.')
                return redirect(url_for('combos.list_combos'))
            else:
                flash('Error al actualizar el combo.')
                
    catalog = ComboModel.get_catalog()
    return render_template('combos/form.html', combo=combo, catalog=catalog)

@combos_bp.route('/toggle/<int:combo_id>')
@login_required
def toggle_status(combo_id):
    if not check_permission('manage_combos'):
        flash('Permiso denegado.')
        return redirect(url_for('main.main_page'))
        
    combo = ComboModel.get_combo_by_id(combo_id)
    if combo:
        new_status = 0 if combo['activo'] else 1
        ComboModel.toggle_combo(combo_id, new_status)
        flash(f'Combo {"activado" if new_status else "desactivado"} exitosamente.')
        
    return redirect(url_for('combos.list_combos'))
