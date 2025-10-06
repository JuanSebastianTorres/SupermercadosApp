from flask import Blueprint, render_template, request, redirect, url_for
from database import db
from models import Producto

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

@productos_bp.route('/')
def listar_productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

@productos_bp.route('/nuevo', methods=['POST'])
def nuevo_producto():
    nuevo = Producto(
        nombre=request.form['nombre'],
        descripcion=request.form['descripcion'],
        precio=request.form['precio'],
        stock=request.form['stock']
    )
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('productos.listar_productos'))
