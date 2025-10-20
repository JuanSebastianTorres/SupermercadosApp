from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Empleado
from database import db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# ---------------------------
# DECORADORES DE SEGURIDAD
# ---------------------------

def login_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para continuar", "warning")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper


def rol_requerido(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'rol' not in session:
                flash("Debes iniciar sesión", "warning")
                return redirect(url_for('auth.login'))
            if session['rol'] not in roles:
                flash("No tienes permiso para acceder a esta sección", "danger")
                return redirect(url_for('auth.dashboard'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ---------------------------
# LOGIN Y LOGOUT
# ---------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        empleado = Empleado.query.filter_by(correo=correo).first()

        if empleado and empleado.check_password(password):
            session['usuario_id'] = empleado.idEmpleado
            session['rol'] = empleado.rol
            session['nombre'] = empleado.nombre
            session['idSucursal'] = empleado.idSucursal
            session.permanent = False
            
            flash(f"Bienvenido, {empleado.nombre} ({empleado.rol})", "success")

            # Redirigir según el rol
            if empleado.rol == 'GERENTE':
                return render_template('inicio_gerente.html')
            elif empleado.rol == 'CAJERO':
                return redirect(url_for('ventas.listar_ventas'))
            elif empleado.rol == 'ADMIN_INVENTARIO':
                return redirect(url_for('productos.listar_productos'))
            else:
                return redirect(url_for('auth.login'))
        else:
            flash("Correo o contraseña incorrectos", "danger")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_requerido
def dashboard():
    """Redirige al panel correspondiente según el rol del usuario."""
    rol = session.get('rol')

    if rol == 'CAJERO':
        return redirect(url_for('ventas.listar_ventas'))
    elif rol == 'ADMIN_INVENTARIO':
        return redirect(url_for('productos.listar_productos'))
    elif rol == 'GERENTE':
        return redirect(url_for('reportes.reportes'))
    else:
        flash("Rol no autorizado")
        return redirect(url_for('auth.login'))


