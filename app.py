from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import pymysql
from database import db  # Importa la instancia de SQLAlchemy desde database.py
from datetime import timedelta

# ---------------------------------------------
# CONFIGURACION BaSICA Y CONEXION CON RAILWAY
# ---------------------------------------------

# Instalar PyMySQL como reemplazo de MySQLdb
pymysql.install_as_MySQLdb()

# Cargar variables de entorno (.env)
load_dotenv()

app = Flask(__name__)

# Configuracion de la base de datos
# Si no hay DATABASE_URL, usa conexion por defecto (Railway)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv("DATABASE_URL")
    or "mysql+pymysql://root:zdyoqLmJyBEyedVCapsVRlWxABYLekfj@shuttle.proxy.rlwy.net:18990/SupermercadosApp"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "Supermercados2025")

# --- Configuración de la sesión ---
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)  # expira en 10 minutos
app.config['SESSION_PERMANENT'] = False  # se elimina al cerrar el navegador
app.config['SESSION_COOKIE_SECURE'] = True  # solo enviar cookie por HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # no accesible desde JavaScript


# Inicializar la base de datos
db.init_app(app)

# ---------------------------------------------
# IMPORTAR MODELOS Y RUTAS
# ---------------------------------------------
with app.app_context():
    from models import *
    db.create_all()

# Importar Blueprints (modulos)
from routes.auth import auth_bp
from routes.clientes import clientes_bp
from routes.productos import productos_bp
from routes.ventas import ventas_bp
from routes.reportes import reportes_bp
from routes.empleados import empleados_bp
from routes.pedidos import pedidos_bp
from routes.facturas import facturas_bp

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(empleados_bp)
app.register_blueprint(pedidos_bp)
app.register_blueprint(facturas_bp)



# ---------------------------------------------
# RUTA PRINCIPAL (Redireccion segun el rol)
# ---------------------------------------------
@app.route('/')
def index():
    session.clear()
    # Si no hay usuario logueado, ir al login
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Verificar rol actual
    rol = session.get('rol')

    # Redirigir segun el rol del empleado
    if rol == 'GERENTE':
        return redirect(url_for('reportes.reportes'))  # Vista principal del gerente
    elif rol == 'CAJERO':
        return redirect(url_for('ventas.listar_ventas'))  # Vista principal del cajero
    elif rol == 'ADMIN_INVENTARIO':
        return redirect(url_for('productos.listar_productos'))  # Vista principal del admin de inventario
    else:
        return redirect(url_for('auth.login'))

# ---------------------------------------------
# EJECUCION LOCAL O EN RAILWAY
# ---------------------------------------------
if __name__ == '__main__':
    # Usar puerto asignado por Railway o 5000 local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



