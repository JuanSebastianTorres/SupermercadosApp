# routes/ventas.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import Venta, DetalleVenta, Producto, Cliente, Fidelizacion, Empleado, Sucursal
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime
from routes.auth import login_requerido, rol_requerido
from invoices import generar_factura_pdf 
from mongodb import get_db
import base64
from zoneinfo import ZoneInfo

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
        # Datos recibidos
        idCliente = request.form.get('idCliente') or None
        canal = request.form.get('canal') or 'POS'
        detalle_json = request.form.get('detalle_json')

        # Validaciones básicas
        if not detalle_json:
            flash("El carrito está vacío. Agrega al menos un producto.", "warning")
            return redirect(url_for('ventas.listar_ventas'))

        try:
            detalle = json.loads(detalle_json)
            if not isinstance(detalle, list) or len(detalle) == 0:
                flash("Detalle inválido.", "danger")
                return redirect(url_for('ventas.listar_ventas'))
        except Exception:
            flash("Error al leer el detalle del carrito.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        # Obtener empleado y sucursal desde session
        idEmpleado = session.get('usuario_id')        
        idSucursal = session.get('idSucursal')

        if not idEmpleado or not idSucursal:
            flash("Error: sesión del empleado o sucursal no encontrada.", "danger")
            return redirect(url_for('ventas.listar_ventas'))

        # Calcular total (Decimal seguro)
        total = Decimal('0')
        for p in detalle:
            try:
                subtotal = Decimal(str(p.get('subtotal', 0)))
            except (InvalidOperation, TypeError):
                flash("Subtotal inválido en algún producto.", "danger")
                return redirect(url_for('ventas.listar_ventas'))
            total += subtotal

        # Crear venta (usar tipos compatibles con tu modelo)
        venta = Venta(
            idCliente=(int(idCliente) if idCliente else None),
            idEmpleado=int(idEmpleado),
            idSucursal=int(idSucursal),
            canal=canal,
            total=int(total),  
            fechaVenta=datetime.now(ZoneInfo("America/Bogota"))

        )
        db.session.add(venta)
        db.session.flush()  # obtener venta.idVenta antes del commit

        # Insertar detalles y actualizar stock
        items_for_pdf = []
        for p in detalle:
            pid = int(p.get('id'))
            cantidad = int(p.get('cantidad', 0))
            subtotal = int(str(p.get('subtotal', 0)))

            producto = Producto.query.get(pid)
            if not producto:
                raise Exception(f"Producto con ID {pid} no encontrado.")

            # Actualizar stock (no negativo)
            producto.stock = max(0, (producto.stock or 0) - cantidad)

            detalle_venta = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=pid,
                cantidad=cantidad,
                subtotal=int(subtotal)
            )
            db.session.add(detalle_venta)

            # Datos para PDF y Mongo
            items_for_pdf.append({
                "id": pid,
                "producto": producto.nombre,
                "cantidad": cantidad,
                "precio": int(producto.precio),
                "subtotal": int(subtotal)
            })

        # Actualizar puntos de fidelizacion si existe cliente
        cliente = None
        if idCliente:
            cliente = Cliente.query.get(int(idCliente))
            if cliente:
                puntos_ganados = int(total // Decimal(1000))
                cliente.puntosAcumulados = (cliente.puntosAcumulados or 0) + puntos_ganados

                movimiento = Fidelizacion(
                    idCliente=cliente.idCliente,
                    fecha=datetime.now(),
                    puntosGanados=puntos_ganados,
                    puntosRedimidos=0,
                    saldo=cliente.puntosAcumulados
                )
                db.session.add(movimiento)

        # Commit de todo lo anterior
        db.session.commit()

        # -------------------------------
        # Generar PDF y guardar en Mongo
        # -------------------------------
        empleado = Empleado.query.get(int(idEmpleado)) if idEmpleado else None
        sucursal = Sucursal.query.get(int(idSucursal)) if idSucursal else None

        cliente_nombre = f"{cliente.nombre} {cliente.apellido}" if cliente else "Cliente Ocasional"
        empleado_nombre = f"{empleado.nombre} {empleado.apellido}" if empleado else None
        sucursal_nombre = sucursal.nombre if sucursal else None

        # Llamada a tu función que crea el PDF. Debe devolver bytes o base64 string.
        # Ajusta la firma de generar_factura_pdf si la tienes diferente.
        pdf_result = generar_factura_pdf(
            venta_id=venta.idVenta,
            cliente_nombre=cliente_nombre,
            fecha=datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S"),
            items=items_for_pdf,
            total=int(total),
            empleado_nombre=empleado_nombre,
            sucursal=sucursal_nombre
        )

        # Normalizar el resultado a bytes
        if isinstance(pdf_result, str):
            # asumo que es base64 string
            try:
                pdf_bytes = base64.b64decode(pdf_result)
            except Exception:
                # si es string con bytes repr, intentar encode
                pdf_bytes = pdf_result.encode('utf-8')
        elif isinstance(pdf_result, (bytes, bytearray)):
            pdf_bytes = bytes(pdf_result)
        else:
            # si la función devuelve None o algo inesperado, evitar fallo
            pdf_bytes = None

        # Guardar documento en MongoDB
        db_mongo = get_db()
        documento = {
            "idVenta": int(venta.idVenta),
            "cliente": cliente_nombre,
            "fecha": venta.fechaVenta,
            "total": int(total),
            "items": items_for_pdf,
            "creado_por": empleado_nombre,
            "sucursal": sucursal_nombre
        }

        if pdf_bytes:
            documento["pdfBase64"] = base64.b64encode(pdf_bytes).decode('utf-8')

        db_mongo.facturas.insert_one(documento)

        flash("✅ Venta registrada y factura guardada.", "success")
        return redirect(url_for('ventas.listar_ventas'))

    except Exception as e:
        db.session.rollback()
        # registrar en consola para debugging en Railway
        print("ERROR al registrar venta:", e)
        flash(f"❌ Error al registrar la venta: {str(e)}", "danger")
        return redirect(url_for('ventas.listar_ventas'))
