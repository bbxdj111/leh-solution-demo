import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_invoice_pdf(order_title: str, address: str, items: list, total_amount: float, currency: str = "EUR") -> bytes:
    """
    Генерирует PDF-инвойс (Rechnung) в формате Bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12
    )
    
    story.append(Paragraph("<b>RECHNUNG / INVOICE</b>", title_style))
    story.append(Paragraph(f"<b>Объект / Заказ:</b> {order_title}", styles['Normal']))
    story.append(Paragraph(f"<b>Адрес:</b> {address}", styles['Normal']))
    story.append(Spacer(1, 15))

    # Таблица выполненных работ и запчастей
    table_data = [["Наименование / Деталь", "Кол-во", "Цена", "Итого"]]
    
    for item in items:
        table_data.append([
            item.get("name", "Работа / Деталь"),
            str(item.get("quantity", 1)),
            f"{item.get('unit_price', 0.0):.2f} {currency}",
            f"{(item.get('quantity', 1) * item.get('unit_price', 0.0)):.2f} {currency}"
        ])
    
    table_data.append(["<b>ИТОГО К ОПЛАТЕ:</b>", "", "", f"<b>{total_amount:.2f} {currency}</b>"])

    t = Table(table_data, colWidths=[250, 60, 100, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    
    story.append(t)
    doc.build(story)
    
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value