from flask import Flask, render_template
from dotenv import load_dotenv
import os
import pymysql
from database import db  # 🔹 importamos db desde database.py

pymysql.install_as_MySQLdb()

# Cargar variables de entorno localmente (solo si existe .env)
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos usando variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔹 Inicializamos db con la app
db.init_app(app)

# Importar rutas y modelos después de inicializar db
from models import *
from routes.clientes import clientes_bp
from routes.productos import productos_bp
from routes.ventas import ventas_bp
from routes.reportes import reportes_bp

# Registrar blueprints
app.register_blueprint(clientes_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(reportes_bp)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ejecutar la app
if __name__ == '__main__':
    # Usar puerto dinámico asignado por Railway o fallback 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


