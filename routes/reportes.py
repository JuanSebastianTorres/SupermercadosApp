from flask import Blueprint, render_template, jsonify
from models import Venta, Producto, DetalleVenta, Cliente
from database import db
from sqlalchemy import func
from routes.auth import login_requerido, rol_requerido

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes', methods=['GET'])
@login_requerido
@rol_requerido('GERENTE')

def reportes():
    return render_template('reportes.html')

@reportes_bp.route('/ventas_por_producto')
def ventas_por_producto():
    data = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad)
    ).join(DetalleVenta).group_by(Producto.nombre).all()

    labels = [r[0] for r in data]
    valores = [int(r[1]) for r in data]

    return jsonify({'labels': labels, 'valores': valores})

