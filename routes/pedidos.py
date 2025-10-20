from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import PedidoProveedor, DetallePedido, Producto, Proveedor
from routes.auth import login_requerido, rol_requerido
from datetime import datetime

pedidos_bp = Blueprint('pedidos', __name__)

# =========================
# PANEL DEL ADMIN INVENTARIO
# =========================
@pedidos_bp.route('/pedidos', methods=['GET'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO')
def listar_pedidos():
    pedidos = PedidoProveedor.query.all()
    proveedores = Proveedor.query.all()
    productos = Producto.query.all()
    return render_template('pedidos_admin.html', pedidos=pedidos, proveedores=proveedores, productos=productos)


@pedidos_bp.route('/pedidos/nuevo', methods=['POST'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO')
def nuevo_pedido():
    idProveedor = request.form['idProveedor']
    productos = request.form.getlist('producto[]')
    cantidades = request.form.getlist('cantidad[]')

    pedido = PedidoProveedor(idProveedor=idProveedor, fechaPedido=datetime.utcnow(), estado='PENDIENTE')
    db.session.add(pedido)
    db.session.flush()

    for i in range(len(productos)):
        detalle = DetallePedido(
            idPedido=pedido.idPedido,
            idProducto=productos[i],
            cantidad=cantidades[i]
        )
        db.session.add(detalle)

    db.session.commit()
    flash("Pedido registrado correctamente", "success")
    return redirect(url_for('pedidos.listar_pedidos'))


@pedidos_bp.route('/pedidos/cambiar_estado/<int:idPedido>', methods=['POST'])
@login_requerido
@rol_requerido('ADMIN_INVENTARIO')
def cambiar_estado_admin(idPedido):
    nuevo_estado = request.form['estado']
    pedido = PedidoProveedor.query.get(idPedido)
    pedido.estado = nuevo_estado
    db.session.commit()
    flash("Estado actualizado correctamente", "success")
    return redirect(url_for('pedidos.listar_pedidos'))

# =========================
# PANEL DEL PROVEEDOR
# =========================
@pedidos_bp.route('/pedidos_proveedor', methods=['GET'])
@login_requerido
@rol_requerido('PROVEEDOR')
def pedidos_proveedor():
    idProveedor = session.get('idProveedor')
    pedidos = PedidoProveedor.query.filter_by(idProveedor=idProveedor).all()
    return render_template('pedidos_proveedor.html', pedidos=pedidos)


@pedidos_bp.route('/pedidos_proveedor/actualizar/<int:idPedido>', methods=['POST'])
@login_requerido
@rol_requerido('PROVEEDOR')
def actualizar_estado_proveedor(idPedido):
    nuevo_estado = request.form['estado']
    pedido = PedidoProveedor.query.get(idPedido)
    pedido.estado = nuevo_estado
    db.session.commit()
    flash("Pedido actualizado por el proveedor", "info")
    return redirect(url_for('pedidos.pedidos_proveedor'))
