from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from models import Venta, DetalleVenta, Producto, Cliente, Empleado
from decimal import Decimal
import json
from datetime import datetime
from routes.auth import login_requerido, rol_requerido

ventas_bp = Blueprint('ventas', __name__)

# ==============================
# VISTA PRINCIPAL
# ==============================
@ventas_bp.route('/ventas', methods=['GET'])
@login_requerido
@rol_requerido('CAJERO')
def listar_ventas():
    ventas = Venta.query.order_by(Venta.fechaVenta.desc()).all()
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template('ventas.html', ventas=ventas, clientes=clientes, productos=productos)


# ==============================
# NUEVA VENTA (desde carrito)
# ==============================
@ventas_bp.route('/nueva', methods=['POST'])
@login_requerido
@rol_requerido('CAJERO')
def nueva_venta():
    try:
        idCliente = request.form.get('idCliente')
        canal = request.form.get('canal')
        detalle_json = request.form.get('detalle_json')

        if not detalle_json:
            flash("Debe agregar al menos un producto al carrito.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        detalles = json.loads(detalle_json)
        if not detalles:
            flash("El carrito está vacío.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        # Obtener ID del empleado logueado y su sucursal
        idEmpleado = session.get('usuario_id')
        empleado = Empleado.query.get(idEmpleado)
        if not empleado or not empleado.idSucursal:
            flash("No se pudo determinar la sucursal del empleado.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        idSucursal = empleado.idSucursal

        # Calcular total
        total = sum(Decimal(p['subtotal']) for p in detalles)

        # Crear la venta
        venta = Venta(
            idCliente=idCliente,
            idEmpleado=idEmpleado,
            idSucursal=idSucursal,
            fechaVenta=datetime.now(),
            canal=canal,
            total=total
        )
        db.session.add(venta)
        db.session.flush()  # genera idVenta sin hacer commit aún

        # Crear detalle de venta
        for p in detalles:
            detalle = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=p['id'],
                cantidad=p['cantidad'],
                subtotal=p['subtotal']
            )
            db.session.add(detalle)

            # Actualizar stock del producto
            producto = Producto.query.get(p['id'])
            if producto:
                producto.stock = max(0, producto.stock - int(p['cantidad']))

        db.session.commit()
        flash("Venta registrada exitosamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar la venta: {str(e)}", "danger")

    return redirect(url_for('ventas.listar_ventas'))


