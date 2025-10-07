from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import pymysql
from database import db  # 🔹 importamos db desde database.py

# Instalar PyMySQL como reemplazo de MySQLdb
pymysql.install_as_MySQLdb()

# Cargar variables de entorno localmente (solo si existe .env)
load_dotenv()

app = Flask(__name__)


# 🔹 Si existe la variable DATABASE_URL (Railway), la usa.
# 🔹 Si no, usa SQLite local (modo desarrollo)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv("DATABASE_URL")
    or "mysql+pymysql://root:zdyoqLmJyBEyedVCapsVRlWxABYLekfj@shuttle.proxy.rlwy.net:18990/railway"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "Supermercados2025")

# Inicializar base de datos
db = SQLAlchemy(app)

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


