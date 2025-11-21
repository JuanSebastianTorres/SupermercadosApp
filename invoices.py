# invoices.py
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generar_factura_pdf(venta_id, cliente_nombre, fecha, items, total, empleado_nombre, sucursal):

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # ========================
    # ENCABEZADO
    # ========================
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, 750, "SUPERMERCADOSAPP")
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, 730, f"Factura N° {venta_id}")
    pdf.drawString(40, 715, f"Fecha: {fecha}")
    pdf.drawString(40, 700, f"Cliente: {cliente_nombre}")
    pdf.drawString(40, 685, f"Atendido por: {empleado_nombre}")
    pdf.drawString(40, 670, f"Sucursal: {sucursal}")

    # ========================
    # TABLA DE PRODUCTOS
    # ========================

    tabla_data = [["Producto", "Cantidad", "Precio", "Subtotal"]]

    for item in items:
        tabla_data.append([
            item["producto"],
            str(item["cantidad"]),
            f"${item['precio']:,}",
            f"${item['subtotal']:,}"
        ])

    tabla = Table(tabla_data, colWidths=[200, 80, 80, 100])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.gray),
    ]))

    tabla.wrapOn(pdf, 40, 400)
    tabla.drawOn(pdf, 40, 520 - (len(items) * 20))

    # ========================
    # TOTAL
    # ========================
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, 500 - (len(items) * 20), f"TOTAL: ${total:,.0f}")

    # ========================
    # PIE DE PÁGINA
    # ========================
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, 50, "Gracias por su compra. Puede descargar esta factura desde su panel de usuario.")

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()

