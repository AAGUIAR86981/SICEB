from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.product import Product
from utils.decorators import login_required, admin_required
from utils.helpers import log_user_activity

# Módulo de Productos: Aquí administramos el catálogo de todos los artículos que se pueden entregar
products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required # Solo usuarios registrados
def list_products():
    """Muestra la lista de todos los productos disponibles, permitiendo buscar y filtrar"""
    try:
        # Obtenemos lo que el usuario quiere filtrar (Activos, Inactivos o Todos)
        filter_status = request.args.get('status', 'active')  # active, inactive, all
        search_query = request.args.get('search', '').strip()
        
        # Avisamos al sistema si debe incluir los productos que ya no se usan
        include_inactive = filter_status in ['inactive', 'all']
        
        # Buscamos los productos en el catálogo según los filtros aplicados
        if search_query:
            products = Product.search(search_query, include_inactive)
        else:
            products = Product.get_all(include_inactive)
        
        # Filtrar solo inactivos si se solicita
        if filter_status == 'inactive':
            products = [p for p in products if not p['activo']]
        
        # Contar productos
        total_activos = Product.count_all(include_inactive=False)
        total_inactivos = Product.count_all(include_inactive=True) - total_activos
        
        return render_template('products/list.html',
                             products=products,
                             filter_status=filter_status,
                             search_query=search_query,
                             total_activos=total_activos,
                             total_inactivos=total_inactivos,
                             total_productos=len(products))
    
    except Exception as e:
        flash(f'Error al cargar productos: {str(e)}', 'error')
        return redirect(url_for('main.main_page'))


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            categoria = request.form.get('categoria', '').strip() or None
            
            # Validaciones
            if not nombre:
                flash('El nombre del producto es obligatorio', 'error')
                return redirect(url_for('products.create_product'))
            
            # Verificar nombre único
            if Product.exists_by_name(nombre):
                flash(f'Ya existe un producto con el nombre "{nombre}"', 'error')
                return redirect(url_for('products.create_product'))
            
            # Crear producto
            product_id = Product.create(nombre, categoria)
            
            if product_id:
                # Registrar actividad
                log_user_activity(
                    session.get('id'),
                    session.get('user'),
                    'Creación de producto',
                    f'Producto "{nombre}" creado (ID: {product_id})'
                )
                
                flash(f'Producto "{nombre}" creado exitosamente', 'success')
                return redirect(url_for('products.list_products'))
            else:
                flash('Error al crear el producto', 'error')
                return redirect(url_for('products.create_product'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('products.create_product'))
    
    # GET: Mostrar formulario
    return render_template('products/form.html', product=None, action='create')


@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """Editar producto existente"""
    product = Product.get_by_id(product_id)
    
    if not product:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('products.list_products'))
    
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            categoria = request.form.get('categoria', '').strip() or None
            activo = request.form.get('activo') == 'on'
            
            # Validaciones
            if not nombre:
                flash('El nombre del producto es obligatorio', 'error')
                return redirect(url_for('products.edit_product', product_id=product_id))
            
            # Verificar nombre único (excluyendo el producto actual)
            if Product.exists_by_name(nombre, exclude_id=product_id):
                flash(f'Ya existe otro producto con el nombre "{nombre}"', 'error')
                return redirect(url_for('products.edit_product', product_id=product_id))
            
            # Actualizar producto
            if Product.update(product_id, nombre, categoria, activo):
                # Registrar actividad
                log_user_activity(
                    session.get('id'),
                    session.get('user'),
                    'Actualización de producto',
                    f'Producto "{nombre}" actualizado (ID: {product_id})'
                )
                
                flash(f'Producto "{nombre}" actualizado exitosamente', 'success')
                return redirect(url_for('products.list_products'))
            else:
                flash('Error al actualizar el producto', 'error')
                return redirect(url_for('products.edit_product', product_id=product_id))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('products.edit_product', product_id=product_id))
    
    # GET: Mostrar formulario
    return render_template('products/form.html', product=product, action='edit')


@products_bp.route('/toggle/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def toggle_product(product_id):
    """Activar/desactivar producto (AJAX)"""
    try:
        product = Product.get_by_id(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            }), 404
        
        # Cambiar estado
        if Product.toggle_status(product_id):
            nuevo_estado = not product['activo']
            estado_texto = 'activado' if nuevo_estado else 'desactivado'
            
            # Registrar actividad
            log_user_activity(
                session.get('id'),
                session.get('user'),
                f'Producto {estado_texto}',
                f'Producto "{product["nombre"]}" fue {estado_texto} (ID: {product_id})'
            )
            
            return jsonify({
                'success': True,
                'message': f'Producto {estado_texto} exitosamente',
                'activo': nuevo_estado
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al cambiar estado del producto'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@products_bp.route('/reporte-entregas')
def reporte_entregas():
    # Llamamos al método del query JSON_TABLE para consulta de productos entregados
    datos = Product.get_delivery_summary()
    return render_template('products/reporte_entregas.html', reporte=datos)
