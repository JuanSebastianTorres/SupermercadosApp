from flask import Blueprint, render_template, jsonify
from models import Venta, Producto, DetalleVenta, Cliente, Sucursal
from database import db
from sqlalchemy import func, and_, or_
from routes.auth import login_requerido, rol_requerido

reportes_bp = Blueprint('reportes', __name__)

# =========================================
# VISTA PRINCIPAL DE REPORTES
# =========================================
@reportes_bp.route('/reportes', methods=['GET'])
@login_requerido
@rol_requerido('GERENTE')
def reportes():
    # Consulta 1: Ventas por producto
    ventas_por_producto = (
        db.session.query(
            Producto.nombre,
            func.sum(DetalleVenta.cantidad).label('total_vendido')
        )
        .join(DetalleVenta)
        .group_by(Producto.nombre)
        .all()
    )

    # Consulta 2: Ventas totales por día (funciones agregadas)
    ventas_por_dia = (
        db.session.query(
            func.date(Venta.fechaVenta).label('fecha'),
            func.sum(Venta.total).label('total_dia'),
            func.count(Venta.idVenta).label('num_ventas')
        )
        .group_by(func.date(Venta.fechaVenta))
        .order_by(func.date(Venta.fechaVenta).desc())
        .all()
    )

    # Consulta 3: Clientes con más compras (JOIN y ORDER)
    top_clientes = (
        db.session.query(
            Cliente.nombre,
            Cliente.apellido,
            func.count(Venta.idVenta).label('num_compras'),
            func.sum(Venta.total).label('total_gastado')
        )
        .join(Venta)
        .group_by(Cliente.idCliente)
        .order_by(func.sum(Venta.total).desc())
        .limit(5)
        .all()
    )

    # Consulta 4: Productos con bajo stock (operador lógico)
    productos_bajo_stock = (
        db.session.query(Producto)
        .filter(or_(Producto.stock < 10, Producto.stock == None))
        .order_by(Producto.stock.asc())
        .all()
    )

    # Consulta 5: Ventas por sucursal (si existe relación)
    try:
        ventas_sucursal = (
            db.session.query(
                Sucursal.nombre,
                func.sum(Venta.total).label('total_ventas')
            )
            .join(Venta)
            .group_by(Sucursal.nombre)
            .all()
        )
    except Exception:
        ventas_sucursal = []

    return render_template(
        'reportes.html',
        ventas_por_producto=ventas_por_producto,
        ventas_por_dia=ventas_por_dia,
        top_clientes=top_clientes,
        productos_bajo_stock=productos_bajo_stock,
        ventas_sucursal=ventas_sucursal
    )


# =========================================
# API para Chart.js (se mantiene igual)
# =========================================
@reportes_bp.route('/reportes/ventas_por_producto')
def ventas_por_producto():
    data = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad)
    ).join(DetalleVenta).group_by(Producto.nombre).all()

    labels = [r[0] for r in data]
    valores = [int(r[1]) for r in data]

    return jsonify({'labels': labels, 'valores': valores})


