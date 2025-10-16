from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Empleado
from database import db
from routes.auth import login_requerido, rol_requerido

empleados_bp = Blueprint('empleados', __name__, url_prefix='/empleados')

#  Listar todos los empleados (solo para GERENTE)
@empleados_bp.route('/')
@login_requerido
@rol_requerido('GERENTE')
def listar_empleados():
    empleados = Empleado.query.all()
    return render_template('empleados.html', empleados=empleados)

#  Crear un nuevo empleado (solo para GERENTE)
@empleados_bp.route('/nuevo', methods=['GET', 'POST'])
@login_requerido
@rol_requerido('GERENTE')
def nuevo_empleado():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rol = request.form['rol']
        correo = request.form['correo']
        password = request.form['password']
        idSucursal = request.form['idSucursal']

        nuevo = Empleado(
            nombre=nombre,
            apellido=apellido,
            rol=rol,
            correo=correo,
            idSucursal=idSucursal
        )
        # 🔹 Se aplica el hash automáticamente
        nuevo.set_password(password)

        db.session.add(nuevo)
        db.session.commit()
        flash("Empleado creado correctamente", "success")
        return redirect(url_for('empleados.listar_empleados'))
