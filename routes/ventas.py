from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import Venta, DetalleVenta, Producto, Cliente
import json
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


@ventas_bp.route('/nueva_venta', methods=['POST'])
@login_requerido
@rol_requerido('CAJERO')
def nueva_venta():
    try:
        idCliente = request.form['idCliente']
        canal = request.form['canal']
        detalle_json = request.form['detalle_json']
        detalle = json.loads(detalle_json)

        idEmpleado = session.get('idEmpleado')
        idSucursal = session.get('idSucursal')

        total = sum(Decimal(p['subtotal']) for p in detalle)

        # Crear venta
        venta = Venta(
            idCliente=idCliente,
            idEmpleado=idEmpleado,
            idSucursal=idSucursal,
            canal=canal,
            total=total
        )
        db.session.add(venta)
        db.session.flush()  # obtiene idVenta

        # Insertar los detalles
        for p in detalle:
            producto = Producto.query.get(p['id'])
            producto.stock -= p['cantidad']

            detalle_venta = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=p['id'],
                cantidad=p['cantidad'],
                subtotal=p['subtotal']
            )
            db.session.add(detalle_venta)

        db.session.commit()
        flash("Venta registrada correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar la venta: {str(e)}", "danger")

    return redirect(url_for('ventas.listar_ventas'))

