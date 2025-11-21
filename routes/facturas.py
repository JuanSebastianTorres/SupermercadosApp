# routes/facturas.py
from flask import Blueprint, render_template, request, send_file, abort, flash, redirect, url_for, session
from mongodb import get_db
import base64
import io
from routes.auth import login_requerido, rol_requerido
from bson.objectid import ObjectId

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')


# ============================================================
# LISTAR FACTURAS (CAJERO y GERENTE)
# ============================================================
@facturas_bp.route('/')
@login_requerido
@rol_requerido('CAJERO', 'GERENTE')
def listar_facturas():

    db = get_db()
    query = {}

    # -----------------------------
    # FILTROS BÁSICOS (todos los roles)
    # -----------------------------
    idVenta = request.args.get("idVenta")
    cliente = request.args.get("cliente")
    fecha = request.args.get("fecha")

    if idVenta:
        try:
            query["idVenta"] = int(idVenta)
        except:
            flash("El ID de venta debe ser numérico.", "warning")

    if cliente:
        query["cliente"] = {"$regex": cliente, "$options": "i"}

    if fecha:
        query["fecha"] = {"$regex": fecha}

    # -----------------------------
    # FILTROS AVANZADOS (solo gerente)
    # -----------------------------
    if session.get("rol") == "GERENTE":

        empleado = request.args.get("empleado")
        sucursal = request.args.get("sucursal")

        if empleado:
            query["creado_por"] = {"$regex": empleado, "$options": "i"}

        if sucursal:
            query["sucursal"] = {"$regex": sucursal, "$options": "i"}

    # -----------------------------
    # CONSULTA A MONGO
    # -----------------------------
    facturas = list(db.facturas.find(query).sort("fecha", -1))

    # Convertir ObjectId a string para HTML
    for f in facturas:
        f["_id"] = str(f["_id"])

    return render_template("facturas.html", facturas=facturas)



# ============================================================
# DESCARGAR FACTURA
# ============================================================
@facturas_bp.route('/descargar/<int:idVenta>')
@login_requerido
@rol_requerido('CAJERO', 'GERENTE')
def descargar_factura(idVenta):

    db = get_db()
    doc = db.facturas.find_one({"idVenta": idVenta})

    if not doc:
        abort(404)

    pdf_b64 = doc.get("pdfBase64")
    if not pdf_b64:
        abort(404)

    pdf_bytes = base64.b64decode(pdf_b64)

    return send_file(
        io.BytesIO(pdf_bytes),
        download_name=f"factura_{idVenta}.pdf",
        as_attachment=True
    )



# ============================================================
# VER DETALLE DE FACTURA
# ============================================================
@facturas_bp.route('/ver/<idFactura>')
@login_requerido
@rol_requerido('CAJERO', 'GERENTE')
def ver_factura(idFactura):

    db = get_db()

    try:
        factura = db.facturas.find_one({"_id": ObjectId(idFactura)})

        if not factura:
            flash("Factura no encontrada.", "danger")
            return redirect(url_for("facturas.listar_facturas"))

        return render_template("factura_detalle.html", factura=factura)

    except Exception as e:
        print("ERROR ver_factura:", e)
        flash("Error al cargar factura.", "danger")
        return redirect(url_for("facturas.listar_facturas"))
