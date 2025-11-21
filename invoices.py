# invoices.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import io
from datetime import datetime

def generar_factura_pdf(venta_id, cliente_nombre, fecha, items, total, empleado_nombre=None, sucursal=None):
    """
    items: lista de dicts {producto, cantidad, precio, subtotal}
    devuelve bytes (PDF)
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, (height - 20*mm), "SupermercadosApp - Factura")
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, (height - 28*mm), f"ID Venta: {venta_id}")
    c.drawString(20*mm, (height - 34*mm), f"Cliente: {cliente_nombre}")
    c.drawString(20*mm, (height - 40*mm), f"Fecha: {fecha}")
    if empleado_nombre:
        c.drawString(20*mm, (height - 46*mm), f"Empleado: {empleado_nombre}")
    if sucursal:
        c.drawString(20*mm, (height - 52*mm), f"Sucursal: {sucursal}")

    # Tabla simple
    y = height - 70*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "Producto")
    c.drawString(110*mm, y, "Precio")
    c.drawString(140*mm, y, "Cantidad")
    c.drawString(165*mm, y, "Subtotal")
    c.setFont("Helvetica", 10)
    y -= 6*mm

    for it in items:
        c.drawString(20*mm, y, str(it.get("producto")))
        c.drawRightString(125*mm, y, f"${int(it.get('precio'))}")
        c.drawRightString(155*mm, y, str(it.get("cantidad")))
        c.drawRightString(190*mm, y, f"${int(it.get('subtotal'))}")
        y -= 6*mm
        if y < 30*mm:  # nueva página si es necesario
            c.showPage()
            y = height - 30*mm

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(190*mm, y-6*mm, f"TOTAL: ${int(total)}")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(20*mm, 15*mm, "Gracias por su compra. Documento generado automáticamente.")

    c.save()
    buffer.seek(0)
    return buffer.read()
