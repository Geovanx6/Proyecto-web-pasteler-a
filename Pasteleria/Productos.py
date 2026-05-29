from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from Cconexion.conexion import mysql, Conexion

productos_blueprint = Blueprint('productos', __name__)

@productos_blueprint.route('/productos')
def index():

    if not session.get('logeado'):
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM producto')

    data = cur.fetchall()

    cur.close()

    return render_template(
        'Producto.html',
        productos=data,
        edit_item=None
    )


@productos_blueprint.route('/add_nombre', methods=['POST'])
def add_nombre():

    nombre = request.form['nombre']
    precioProducto = request.form['precioProducto']
    stock = request.form['stock']

    cur = mysql.connection.cursor()

    cur.execute(
        '''
        INSERT INTO producto(nombre, precioProducto, stock)
        VALUES(%s, %s, %s)
        ''',
        (nombre, precioProducto, stock)
    )

    mysql.connection.commit()

    cur.close()

    flash('Producto agregado correctamente')

    return redirect(url_for('productos.index'))


# CAMBIO IMPORTANTE
@productos_blueprint.route('/edit_producto/<string:id>')
def get_producto(id):

    cur = mysql.connection.cursor()

    cur.execute(
        'SELECT * FROM producto WHERE idproducto = %s',
        [id]
    )

    data = cur.fetchone()

    cur.execute('SELECT * FROM producto')

    productos = cur.fetchall()

    cur.close()

    if data is None:

        flash('Producto no encontrado')

        return redirect(url_for('productos.index'))

    return render_template(
        'Producto.html',
        productos=productos,
        edit_item=data
    )