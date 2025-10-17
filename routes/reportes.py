from flask import Blueprint, render_template, jsonify
from database import db
from sqlalchemy import func, text
from routes.auth import login_requerido, rol_requerido

reportes_bp = Blueprint('reportes', __name__)

# ====================================================
# VISTA PRINCIPAL DE REPORTES (SOLO GERENTE)
# ====================================================
@reportes_bp.route('/reportes', methods=['GET'])
@login_requerido
@rol_requerido('GERENTE')
def reportes():
    return render_template('reportes.html')


# ====================================================
# ENDPOINTS DE CONSULTAS GERENCIALES
# ====================================================

@reportes_bp.route('/api/productos_mas_vendidos_ciudad')
def productos_mas_vendidos_ciudad():
    query = text("""
        SELECT s.ciudad, p.nombre, SUM(dv.cantidad) AS total_vendido
        FROM DetalleVenta dv
        JOIN Venta v ON dv.idVenta = v.idVenta
        JOIN Producto p ON dv.idProducto = p.idProducto
        JOIN Sucursal s ON v.idSucursal = s.idSucursal
        GROUP BY s.ciudad, p.nombre
        ORDER BY s.ciudad, total_vendido DESC;
    """)
    data = db.session.execute(query).fetchall()
    labels = [f"{r[0]} - {r[1]}" for r in data]
    valores = [int(r[2]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/ticket_promedio')
def ticket_promedio():
    query = text("""
        SELECT s.nombre, ROUND(AVG(v.total), 2) AS ticket_promedio
        FROM Venta v
        JOIN Sucursal s ON v.idSucursal = s.idSucursal
        GROUP BY s.nombre;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [float(r[1]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/clientes_fidelizados')
def clientes_fidelizados():
    query = text("""
        SELECT CONCAT(nombre, ' ', apellido) AS cliente, puntosAcumulados
        FROM Cliente
        ORDER BY puntosAcumulados DESC
        LIMIT 10;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [int(r[1]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/canal_ventas')
def canal_ventas():
    query = text("""
        SELECT canal, ROUND(SUM(total), 2) AS total_canal
        FROM Venta
        GROUP BY canal;
    """)
    data = db.session.execute(query).fetchall()
    total_general = sum([float(r[1]) for r in data]) or 1
    labels = [r[0] for r in data]
    valores = [round(float(r[1]) * 100 / total_general, 2) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/quiebre_stock')
def quiebre_stock():
    query = text("""
        SELECT c.nombre, 
               SUM(CASE WHEN p.stock <= 0 THEN 1 ELSE 0 END) AS sin_stock,
               COUNT(p.idProducto) AS total,
               ROUND(SUM(CASE WHEN p.stock <= 0 THEN 1 ELSE 0 END) * 100 / COUNT(p.idProducto), 2) AS porcentaje
        FROM Producto p
        JOIN Categoria c ON p.idCategoria = c.idCategoria
        GROUP BY c.nombre;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [float(r[3]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/proveedores_confiables')
def proveedores_confiables():
    query = text("""
        SELECT pr.nombre,
               ROUND(SUM(CASE WHEN pp.estado = 'RECIBIDO' THEN 1 ELSE 0 END) * 100 / COUNT(pp.idPedido), 2) AS confiabilidad
        FROM PedidoProveedor pp
        JOIN Proveedor pr ON pp.idProveedor = pr.idProveedor
        GROUP BY pr.nombre;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [float(r[1]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/promociones_ventas')
def promociones_ventas():
    query = text("""
        SELECT pr.descripcion, COUNT(dv.idDetalle) AS ventas_con_promocion
        FROM PromocionProducto pp
        JOIN Promocion pr ON pp.idPromocion = pr.idPromocion
        JOIN DetalleVenta dv ON pp.idProducto = dv.idProducto
        GROUP BY pr.descripcion;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [int(r[1]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/evolucion_mensual')
def evolucion_mensual():
    query = text("""
        SELECT DATE_FORMAT(fechaVenta, '%Y-%m') AS mes, SUM(total) AS total_mensual
        FROM Venta
        WHERE fechaVenta >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY mes
        ORDER BY mes;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [float(r[1]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/rentabilidad_sucursales')
def rentabilidad_sucursales():
    query = text("""
        SELECT s.nombre, SUM(v.total) AS ingresos
        FROM Venta v
        JOIN Sucursal s ON v.idSucursal = s.idSucursal
        GROUP BY s.nombre
        ORDER BY ingresos DESC;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [float(r[1]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})


@reportes_bp.route('/api/tasa_devoluciones')
def tasa_devoluciones():
    query = text("""
        SELECT c.nombre, 
               COUNT(d.idDevolucion) AS devoluciones,
               COUNT(dv.idDetalle) AS ventas,
               ROUND(COUNT(d.idDevolucion) * 100 / COUNT(dv.idDetalle), 2) AS tasa
        FROM Devolucion d
        JOIN Producto p ON d.idProducto = p.idProducto
        JOIN Categoria c ON p.idCategoria = c.idCategoria
        JOIN DetalleVenta dv ON p.idProducto = dv.idProducto
        GROUP BY c.nombre;
    """)
    data = db.session.execute(query).fetchall()
    labels = [r[0] for r in data]
    valores = [float(r[3]) for r in data]
    return jsonify({'labels': labels, 'valores': valores})
