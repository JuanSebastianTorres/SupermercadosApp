from flask import Blueprint, render_template, request, redirect, url_for
from database import db
from models import Cliente
from routes.auth import login_requerido, rol_requerido

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET'])
@login_requerido
@rol_requerido('GERENTE', 'CAJERO')

def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@clientes_bp.route('/nuevo', methods=['POST'])

def nuevo_cliente():
    tipo_doc = request.form['tipoDocumento']
    num_doc = request.form['numeroDocumento']
    nombre = request.form['nombre'].strip().lower()
    apellido = request.form['apellido'].strip().lower()
    correo = request.form.get('correo')
    celular = request.form.get('celular')
    
    if Cliente.query.filter_by(numeroDocumento=numero_doc).first():
        flash("Ya existe un cliente con ese número de documento.")
        return redirect(url_for('clientes.listar_clientes'))
    
    nuevo = Cliente(
        tipoDocumento=tipo_doc,
        numeroDocumento=num_doc,
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        celular=celular
    )
    
    db.session.add(nuevo)
    db.session.commit()

    flash("Cliente agregado correctamente.")
    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/clientes/buscar', methods=['POST'])
def buscar_cliente():
    num_doc = request.form['numeroDocumentoBuscar'].strip()
    cliente = Cliente.query.filter_by(numeroDocumento=num_doc).first()

    if cliente:
        return render_template('clientes.html', cliente=cliente)
    else:
        flash("No se encontró ningún cliente con ese número de documento.")
        return redirect(url_for('clientes.listar_clientes'))