from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for,Blueprint,session
from flask_mysqldb import MySQL
from Cconexion.conexion import mysql, Conexion
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

reporte_blueprint = Blueprint('reporte', __name__)


@reporte_blueprint.route('/comprobante')
def vista_comprobante():
  
    if not session.get('logeado'):
        return redirect(url_for('login'))
        
    return render_template('comprobante.html')

@reporte_blueprint.route('/obtener_comprobante/<int:id_factura>', methods=['GET'])
def obtener_comprobante(id_factura):
    try:
        cur = mysql.connection.cursor()
        
      
        cur.execute('''
            SELECT f.idfactura, DATE_FORMAT(f.fechaFactura, '%%Y-%%m-%%d') as fecha, 
                   c.nombre, c.appaterno, c.apmaterno
            FROM factura f
            INNER JOIN cliente c ON f.fkcliente = c.idcliente
            WHERE f.idfactura = %s
        ''', (id_factura,))
        cabecera_data = cur.fetchone()
        
        if not cabecera_data:
            cur.close()
            return jsonify({'status': 'error', 'message': 'El número de factura no existe en el sistema.'})
            
        cabecera = {
            'idfactura': cabecera_data[0],
            'fechaFactura': cabecera_data[1],
            'nombre': cabecera_data[2],
            'appaterno': cabecera_data[3],
            'apmaterno': cabecera_data[4]
        }
        
        #Obtener lista completa de productos agregados a dicha factura
        cur.execute('''
            SELECT d.fkproducto, p.nombre, d.precioventa, d.cantidad, (d.precioventa * d.cantidad) as subtotal
            FROM detalle d
            INNER JOIN producto p ON d.fkproducto = p.idproducto
            WHERE d.fkfactura = %s
        ''', (id_factura,))
        productos_rows = cur.fetchall()
        cur.close()
        
        productos = []
        subtotal_acumulado = 0.0
        
        for p in productos_rows:
            subtotal_acumulado += float(p[4])
            productos.append({
                'idproducto': p[0],
                'nombre_producto': p[1],
                'precioventa': float(p[2]),
                'cantidad': p[3],
                'subtotal': float(p[4])
            })
            
        # Cálculos económicos basados en la tasa impositiva del 15%
        iva = subtotal_acumulado * 0.15
        total_general = subtotal_acumulado + iva
        
        return jsonify({
            'status': 'success',
            'cabecera': cabecera,
            'productos': productos,
            'totales': {
                'subtotal': subtotal_acumulado,
                'iva': iva,
                'total': total_general
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==========================================
# IMPRIMIR PDF  
# ==========================================
@reporte_blueprint.route('/generar_pdf_factura/<int:id_factura>', methods=['GET'])
def generar_pdf_factura(id_factura):
    cur = mysql.connection.cursor()
    
   
    cur.execute('''
        SELECT f.idfactura, DATE_FORMAT(f.fechaFactura, '%%d/%%m/%%Y') as fecha, 
               c.nombre, c.appaterno, c.apmaterno
        FROM factura f
        INNER JOIN cliente c ON f.fkcliente = c.idcliente
        WHERE f.idfactura = %s
    ''', (id_factura,))
    cabecera = cur.fetchone()
    
    if not cabecera:
        cur.close()
        return "Factura no encontrada", 404
        
   
    cur.execute('''
        SELECT d.fkproducto, p.nombre, d.precioventa, d.cantidad, (d.precioventa * d.cantidad) as subtotal
        FROM detalle d
        INNER JOIN producto p ON d.fkproducto = p.idproducto
        WHERE d.fkfactura = %s
    ''', (id_factura,))
    productos = cur.fetchall()
    cur.close()
    
  
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#1e3a8a"), spaceAfter=15)
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, leading=16, textColor=colors.HexColor("#334155"))
    
    # Encabezado del PDF
    story.append(Paragraph(f"COMPROBANTE DE FACTURA ELECTRÓNICA", title_style))
    story.append(Spacer(1, 10))
    
    # Sección informativa estructurada del cliente
    info_datos = [
        [Paragraph(f"<b>Factura N°:</b> {cabecera[0]}", text_style), Paragraph(f"<b>Fecha de Emisión:</b> {cabecera[1]}", text_style)],
        [Paragraph(f"<b>Cliente:</b> {cabecera[2]} {cabecera[3]} {cabecera[4]}", text_style), ""]
    ]
    info_table = Table(info_datos, colWidths=[250, 250])
    info_table.setStyle(TableStyle([('SPAN', (0, 1), (1, 1)), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(info_table)
    story.append(Spacer(1, 25))
    
    # Tabla de Items comprados
    tabla_articulos = [["ID", "Producto / Descripción", "Precio Unit.", "Cant.", "Subtotal"]]
    subtotal_acumulado = 0.0
    
    for item in productos:
        subtotal_acumulado += float(item[4])
        tabla_articulos.append([
            str(item[0]),
            str(item[1]),
            f"${float(item[2]):.2f}",
            str(item[3]),
            f"${float(item[4]):.2f}"
        ])
        
    iva = subtotal_acumulado * 0.15
    total_general = subtotal_acumulado + iva
    
    # Agregar filas de cierre financiero
    tabla_articulos.append(["", "", "", "IVA (15%):", f"${iva:.2f}"])
    tabla_articulos.append(["", "", "", "Total a Pagar:", f"${total_general:.2f}"])
    
    prod_table = Table(tabla_articulos, colWidths=[50, 240, 80, 50, 100])
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -3), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -3), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (3, -2), (4, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (3, -2), (4, -2), 1, colors.HexColor("#1e3a8a")),
    ]))
    
    story.append(prod_table)
    
  
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=False, mimetype='application/pdf', download_name=f'Factura_{id_factura}.pdf')

