from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from database import db
from models import Producto
from routes.auth import login_requerido, rol_requerido

productos_bp = Blueprint('productos', __name__)

# -----------------------------------
# VISTA PRINCIPAL
# -----------------------------------
@productos_bp.route('/productos', methods=['GET'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO', 'GERENTE')
def listar_productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)


# -----------------------------------
# API PARA AUTOCOMPLETADO
# -----------------------------------
@productos_bp.route('/api/productos', methods=['GET'])
@login_requerido
def obtener_productos():
    productos = Producto.query.all()
    data = [
        {
            "id": p.idProducto,
            "referencia": p.referencia,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": p.precio,
            "stock": p.stock
        }
        for p in productos
    ]
    return jsonify(data)


# -----------------------------------
# AUMENTAR STOCK O AGREGAR PRODUCTO
# -----------------------------------
@productos_bp.route('/productos/agregar', methods=['POST'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO', 'GERENTE')
def agregar_producto():
    referencia = request.form.get('referencia')
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    cantidad = int(request.form.get('cantidad', 0))

    producto = Producto.query.filter_by(nombre=referencia).first()

    # Si el producto ya existe, sumar al stock
    if producto:
        producto.stock += cantidad
        flash(f"Stock actualizado para {producto.nombre}. Nuevo stock: {producto.stock}", "success")

    # Si no existe, crear nuevo
    else:
        nuevo = Producto(
            referencia=referencia,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=cantidad
        )
        db.session.add(nuevo)
        flash(f"Nuevo producto '{nombre}' agregado correctamente", "success")

    db.session.commit()
    return redirect(url_for('productos.listar_productos'))