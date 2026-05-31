from flask import Flask, render_template, request, jsonify,Blueprint,session,redirect,url_for
from flask_mysqldb import MySQL
from Cconexion.conexion import mysql, Conexion

ventas_blueprint = Blueprint('ventas', __name__)

@ventas_blueprint.route('/ventas')
def Index():
    
    if not session.get('logeado'):
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor()
    cur.execute('SELECT MAX(idfactura) FROM factura')
    resultado = cur.fetchone()
    ultima_factura = resultado[0] if resultado and resultado[0] is not None else 0
    cur.close()
    return render_template("ventas.html", ultima_factura=ultima_factura)



@ventas_blueprint.route('/ventas/buscar_cliente', methods=['GET']) # <-- Agregar /ventas
def buscar_cliente():
    query = request.args.get('q', '')
    cur = mysql.connection.cursor()
    
    cur.execute('SELECT idcliente, nombre, appaterno, apmaterno FROM cliente WHERE nombre LIKE %s', (f"%{query}%",))
    clientes = cur.fetchall()
    cur.close()
    
    lista = [{'id': c[0], 'nombre': c[1], 'appaterno': c[2], 'apmaterno': c[3]} for c in clientes]
    return jsonify(lista)


@ventas_blueprint.route('/ventas/buscar_producto', methods=['GET']) # <-- Agregar /ventas
def buscar_producto():
    query = request.args.get('q', '')
    cur = mysql.connection.cursor()
    cur.execute('SELECT idproducto, nombre, precioProducto, stock FROM producto WHERE nombre LIKE %s', (f"%{query}%",))
    productos = cur.fetchall()
    cur.close()
    
    lista = [{'id': p[0], 'nombre': p[1], 'precio': float(p[2]), 'stock': p[3]} for p in productos]
    return jsonify(lista)