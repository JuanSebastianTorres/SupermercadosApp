# routes/facturas.py
from flask import Blueprint, render_template, request, send_file, abort
from mongodb import get_db
import base64
import io
from routes.auth import login_requerido, rol_requerido

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@facturas_bp.route('/', methods=['GET'])
@login_requerido
@rol_requerido('GERENTE', 'CAJERO')
def listar_facturas():
    db = get_db()
    docs = list(db.facturas.find().sort("fecha", -1).limit(200))
    # convert ObjectId to string if needed in template
    for d in docs:
        d["_id_str"] = str(d.get("_id"))
    return render_template('facturas.html', facturas=docs)

@facturas_bp.route('/descargar/<int:idVenta>', methods=['GET'])
@login_requerido
@rol_requerido('GERENTE', 'CAJERO')
def descargar_factura(idVenta):
    db = get_db()
    doc = db.facturas.find_one({"idVenta": int(idVenta)})
    if not doc:
        abort(404)
    pdf_b64 = doc.get("pdfBase64")
    if not pdf_b64:
        abort(404)
    pdf_bytes = base64.b64decode(pdf_b64)
    return send_file(io.BytesIO(pdf_bytes), download_name=f"factura_{idVenta}.pdf", as_attachment=True)
