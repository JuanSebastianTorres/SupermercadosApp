from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import Venta, DetalleVenta, Producto, Cliente, Fidelizacion, Empleado, Sucursal
import json
from decimal import Decimal
from datetime import datetime
from routes.auth import login_requerido, rol_requerido
from invoices import generar_factura_pdf
from mongodb import get_db
import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from mongodb import get_db

ventas_bp = Blueprint('ventas', __name__)

# =========================================
# LISTAR / FORMULARIO DE VENTAS
# =========================================
@ventas_bp.route('/ventas', methods=['GET'])
@login_requerido
@rol_requerido('CAJERO')
def listar_ventas():
    ventas = Venta.query.order_by(Venta.fechaVenta.desc()).all()
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template('ventas.html', ventas=ventas, clientes=clientes, productos=productos)

# =========================================
# REGISTRAR UNA NUEVA VENTA + FACTURA PDF + MONGODB
# =========================================
@ventas_bp.route('/nueva_venta', methods=['POST'])
@login_requerido
@rol_requerido('CAJERO')
def nueva_venta():
    try:
        print("=== DEBUG: Datos recibidos ===")
        idCliente = request.form.get('idCliente')
        canal = request.form.get('canal')
        detalle_json = request.form.get('detalle_json')

        print("Cliente:", idCliente)
        print("Canal:", canal)
        print("Detalle JSON:", detalle_json)

        # Convertir JSON a lista
        detalle = json.loads(detalle_json)
        print("Detalle cargado:", detalle)

        # Obtener datos del cajero logueado
        idEmpleado = session.get('idEmpleado')   # Mantengo tu nombre
        idSucursal = session.get('idSucursal')
        print("Empleado activo:", idEmpleado)
        print("Sucursal activa:", idSucursal)

        if not idEmpleado or not idSucursal:
            flash("Error: sesión del empleado o sucursal no encontrada.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        # Calcular total
        total = sum(Decimal(p['subtotal']) for p in detalle)
        print("Total venta:", total)

        # Crear la venta
        venta = Venta(
            idCliente=idCliente,
            idEmpleado=idEmpleado,
            idSucursal=idSucursal,
            canal=canal,
            total=total,
            fechaVenta=datetime.now()
        )
        db.session.add(venta)
        db.session.flush()  # obtiene idVenta antes del commit

        # Registrar los detalles
        items_for_pdf = []  # para la factura PDF
        for p in detalle:
            producto = Producto.query.get(p['id'])
            if not producto:
                raise Exception(f"Producto con ID {p['id']} no encontrado.")

            # Actualizar stock
            producto.stock = max(0, producto.stock - p['cantidad'])

            detalle_venta = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=p['id'],
                cantidad=p['cantidad'],
                subtotal=p['subtotal']
            )
            db.session.add(detalle_venta)

            # Datos para PDF
            items_for_pdf.append({
                "producto": producto.nombre,
                "cantidad": p['cantidad'],
                "precio": int(producto.precio),
                "subtotal": float(p['subtotal'])
            })

        # -------------------------------
        # Actualizar puntos de fidelización
        # -------------------------------
        cliente = Cliente.query.get(idCliente)
        if cliente:
            puntos_ganados = int(total // 1000)  # 1 punto por cada 1000 pesos
            cliente.puntosAcumulados += puntos_ganados

            movimiento = Fidelizacion(
                idCliente=cliente.idCliente,
                fecha=datetime.now(),
                puntosGanados=puntos_ganados,
                puntosRedimidos=0,
                saldo=cliente.puntosAcumulados
            )
            db.session.add(movimiento)

            print(f"Puntos agregados a {cliente.nombre}: +{puntos_ganados}")

        db.session.commit()
        print("Venta creada correctamente con ID:", venta.idVenta)

        # ===============================================================
        #        🧾 GENERAR FACTURA PDF Y GUARDARLA EN MONGODB
        # ===============================================================

        cliente_nombre = (
            f"{cliente.nombre} {cliente.apellido}"
            if cliente else "Cliente Ocasional"
        )

        empleado = Empleado.query.get(idEmpleado)
        sucursal = Sucursal.query.get(idSucursal)

        empleado_nombre = f"{empleado.nombre} {empleado.apellido}" if empleado else None
        sucursal_nombre = sucursal.nombre if sucursal else None

        pdf_bytes = generar_factura_pdf(
            venta_id=venta.idVenta,
            cliente_nombre=cliente_nombre,
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            items=items_for_pdf,
            total=float(total),
            empleado_nombre=empleado_nombre,
            sucursal=sucursal_nombre
        )

        # Guardar en MongoDB
        db_mongo = get_db()
        documento = {
            "idVenta": int(venta.idVenta),
            "cliente": cliente_nombre,
            "fecha": datetime.now(),
            "total": float(total),
            "items": items_for_pdf,
            "pdfBase64": base64.b64encode(pdf_bytes).decode("utf-8"),
            "creado_por": empleado_nombre,
            "sucursal": sucursal_nombre
        }
        db_mongo.facturas.insert_one(documento)

        flash("✅ Venta registrada y factura generada correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al registrar la venta: {str(e)}", "danger")
        print("ERROR:", e)

    return redirect(url_for('ventas.listar_ventas'))





