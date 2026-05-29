from flask import Blueprint, render_template, request, redirect, url_for, flash,session,Blueprint
from flask_mysqldb import MySQL
from Cconexion.conexion import mysql, Conexion

clientes_blueprint = Blueprint('clientes', __name__)

@clientes_blueprint.route('/clientes')
def Index():
   
    if not session.get('logeado'):
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM cliente')
    data = cur.fetchall() 
    cur.close()
    return render_template("clientes.html", clientes=data, edit_item=None)


@clientes_blueprint.route('/add_cliente', methods=['POST'])
def add_cliente():
    if request.method == 'POST':
      
        nombre = request.form['nombre']
        appaterno = request.form['appaterno']
        apmaterno = request.form['apmaterno']
        cedula = request.form['cedula']

        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO cliente (nombre, appaterno, apmaterno, cedula) VALUES (%s, %s, %s, %s)',
            (nombre, appaterno, apmaterno, cedula)
        )
        mysql.connection.commit()
        cur.close()
        
        flash('Cliente agregado exitosamente')
        
        return redirect(url_for('clientes.Index'))
    

@clientes_blueprint.route('/edit/<id>')
def get_cliente(id):
    cur = mysql.connection.cursor()
    # Filtramos por idcliente
    cur.execute('SELECT * FROM cliente WHERE idcliente = %s', [id])
    data = cur.fetchall()
    cur.execute('SELECT * FROM cliente')
    todos = cur.fetchall()
    cur.close()
    return render_template("clientes.html", clientes=todos, edit_item=data[0])


@clientes_blueprint.route('/update/<id>', methods=['POST'])
def update_cliente(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        appaterno = request.form['appaterno']
        apmaterno = request.form['apmaterno']
        cedula = request.form['cedula']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE cliente 
            SET nombre = %s, 
                appaterno = %s, 
                apmaterno = %s,
                cedula = %s
            WHERE idcliente = %s
        """, (nombre, appaterno, apmaterno, cedula, id))
        mysql.connection.commit()
        cur.close()
        
        flash('Cliente actualizado correctamente')
        
        return redirect(url_for('clientes.Index'))


@clientes_blueprint.route('/delete/<string:id>')
def delete_cliente(id):
    cur = mysql.connection.cursor()
    # Eliminamos buscando por idcliente
    cur.execute('DELETE FROM cliente WHERE idcliente = %s', [id])
    mysql.connection.commit()
    cur.close()
    
    flash('Cliente eliminado exitosamente')
    
    return redirect(url_for('clientes.Index'))

