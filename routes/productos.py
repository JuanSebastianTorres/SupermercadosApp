from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Producto, Categoria, Proveedor
from routes.auth import login_requerido, rol_requerido

productos_bp = Blueprint('productos', __name__)

# Listar productos y agregar stock
@productos_bp.route('/productos', methods=['GET', 'POST'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO', 'GERENTE')
def listar_productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)


# Agregar stock a un producto existente
@productos_bp.route('/productos/agregar', methods=['POST'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO', 'GERENTE')
def agregar_producto():
    referencia = request.form.get('referencia')
    cantidad = int(request.form.get('cantidad', 0))

    producto = Producto.query.filter_by(referencia=referencia).first()

    if producto:
        producto.stock += cantidad
        db.session.commit()
        flash(f"Se agregaron {cantidad} unidades al stock de '{producto.nombre}'.", "success")
    else:
        flash("La referencia no existe. Registra primero el producto.", "warning")
        return redirect(url_for('productos.nuevo_producto', referencia=referencia))

    return redirect(url_for('productos.listar_productos'))


# Mostrar formulario para crear un nuevo producto
@productos_bp.route('/productos/nuevo', methods=['GET'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO', 'GERENTE')
def nuevo_producto():
    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    referencia = request.args.get('referencia', '')
    return render_template('nuevo_producto.html', categorias=categorias, proveedores=proveedores, referencia=referencia)


# Guardar producto nuevo
@productos_bp.route('/productos/guardar', methods=['POST'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO', 'GERENTE')
def guardar_producto():
    referencia = request.form['referencia']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    stock = request.form['stock']
    idCategoria = request.form['idCategoria']
    idProveedor = request.form['idProveedor']

    nuevo = Producto(
        referencia=referencia,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        idCategoria=idCategoria,
        idProveedor=idProveedor
    )
    db.session.add(nuevo)
    db.session.commit()

    flash(f"Producto '{nombre}' agregado correctamente.", "success")
    return redirect(url_for('productos.listar_productos'))
