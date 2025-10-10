from flask import Blueprint, render_template, request, redirect, url_for
from database import db
from models import Venta, DetalleVenta, Producto, Cliente
from decimal import Decimal
from routes.auth import login_requerido, rol_requerido

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/ventas', methods=['GET'])
@login_requerido
@rol_requerido('CAJERO')

def listar_ventas():
    ventas = Venta.query.all()
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template('ventas.html', ventas=ventas, clientes=clientes, productos=productos)

@ventas_bp.route('/nueva', methods=['POST'])
def nueva_venta():
    idCliente = request.form['idCliente']
    idProducto = request.form['idProducto']
    cantidad = int(request.form['cantidad'])

    producto = Producto.query.get(idProducto)
    subtotal = Decimal(cantidad) * producto.precio

    # Crear venta y detalle
    venta = Venta(idCliente=idCliente, total=subtotal)
    db.session.add(venta)
    db.session.commit()

    detalle = DetalleVenta(
        idVenta=venta.idVenta,
        idProducto=idProducto,
        cantidad=cantidad,
        subtotal=subtotal
    )
    producto.stock -= cantidad
    db.session.add(detalle)
    db.session.commit()

    return redirect(url_for('ventas.listar_ventas'))
