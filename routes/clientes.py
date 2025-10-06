from flask import Blueprint, render_template, request, redirect, url_for
from database import db
from models import Cliente

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@clientes_bp.route('/nuevo', methods=['POST'])

def nuevo_cliente():
    tipo_doc = request.form['tipoDocumento']
    num_doc = request.form['numeroDocumento']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form.get('correo')
    celular = request.form.get('celular')
    
    
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
    return redirect(url_for('clientes.listar_clientes'))

