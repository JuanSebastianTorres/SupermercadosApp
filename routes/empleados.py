from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Empleado
from database import db
from routes.auth import login_requerido, rol_requerido

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/empleados/nuevo', methods=['GET', 'POST'])
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
        # 🔹 Aquí se aplica el hash automáticamente
        nuevo.set_password(password)

        db.session.add(nuevo)
        db.session.commit()
        flash("Empleado creado correctamente", "success")
        return redirect(url_for('auth.dashboard'))

    return render_template('nuevo_empleado.html')
