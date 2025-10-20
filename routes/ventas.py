from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import Venta, DetalleVenta, Producto, Cliente, Empleado, Sucursal
import json
from decimal import Decimal
from routes.auth import login_requerido, rol_requerido

ventas_bp = Blueprint('ventas', __name__)

# ======================================================
# MOSTRAR FORMULARIO DE VENTA
# ======================================================
@ventas_bp.route('/ventas', methods=['GET'])
@login_requerido
@rol_requerido('CAJERO')
def listar_ventas():
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template('ventas.html', clientes=clientes, productos=productos)


# ======================================================
# REGISTRAR NUEVA VENTA (CARRITO)
# ======================================================
@ventas_bp.route('/nueva_venta', methods=['POST'])
@login_requerido
@rol_requerido('CAJERO')
def nueva_venta():
    try:
        idCliente = int(request.form['idCliente'])
        canal = request.form['canal']
        detalle_json = request.form['detalle_json']
        detalle = json.loads(detalle_json)

        # Validación básica
        if not detalle:
            flash("El carrito está vacío.", "warning")
            return redirect(url_for('ventas.listar_ventas'))

        # Recuperar datos del cajero en sesión
        idEmpleado = session.get('usuario_id')  # Asegúrate que el login lo guarde así
        empleado = Empleado.query.get(idEmpleado)

        if not empleado:
            flash("Error: no se pudo identificar el empleado.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        idSucursal = empleado.idSucursal

        # Calcular total
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
        db.session.flush()  # obtiene idVenta antes del commit

        # Agregar detalle de productos
        for p in detalle:
            producto = Producto.query.get(int(p['id']))
            if not producto:
                continue

            # Actualizar stock
            if producto.stock < p['cantidad']:
                flash(f"Stock insuficiente para {producto.nombre}", "danger")
                db.session.rollback()
                return redirect(url_for('ventas.listar_ventas'))

            producto.stock -= p['cantidad']

            detalle_venta = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=producto.idProducto,
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


