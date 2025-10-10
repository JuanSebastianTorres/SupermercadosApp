from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Cliente(db.Model):
    __tablename__ = 'Cliente'
    idCliente = db.Column(db.Integer, primary_key=True)
    tipoDocumento = db.Column(db.String(5), nullable=False)
    numeroDocumento = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True)
    celular = db.Column(db.String(20))
    fechaRegistro = db.Column(db.Date, default=datetime.utcnow)
    puntosAcumulados = db.Column(db.Integer, default=0)

class Sucursal(db.Model):
    __tablename__ = 'Sucursal'
    idSucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20))
    tipoSucursal = db.Column(db.Enum('FISICA', 'ONLINE'), nullable=False)

class Empleado(db.Model):
    __tablename__ = 'Empleado'

    idEmpleado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasenaHash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('CAJERO', 'ADMIN_INVENTARIO', 'GERENTE', 'CLIENTE'), default='CAJERO')
    idSucursal = db.Column(db.Integer, nullable=True)

    def set_password(self, password):
        self.contrasenaHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasenaHash, password)

class Proveedor(db.Model):
    __tablename__ = 'Proveedor'
    idProveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    NIT = db.Column(db.String(20), unique=True, nullable=False)
    contacto = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(120))
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')

class Categoria(db.Model):
    __tablename__ = 'Categoria'
    idCategoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))

class Producto(db.Model):
    __tablename__ = 'Producto'
    idProducto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(12,2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    codigoBarras = db.Column(db.String(50), unique=True)
    idCategoria = db.Column(db.Integer, db.ForeignKey('Categoria.idCategoria'), nullable=False)
    idProveedor = db.Column(db.Integer, db.ForeignKey('Proveedor.idProveedor'), nullable=False)

class Venta(db.Model):
    __tablename__ = 'Venta'
    idVenta = db.Column(db.Integer, primary_key=True)
    idCliente = db.Column(db.Integer, db.ForeignKey('Cliente.idCliente'), nullable=True)
    idEmpleado = db.Column(db.Integer, db.ForeignKey('Empleado.idEmpleado'), nullable=False)
    idSucursal = db.Column(db.Integer, db.ForeignKey('Sucursal.idSucursal'), nullable=False)
    fechaVenta = db.Column(db.DateTime, default=datetime.utcnow)
    canal = db.Column(db.Enum('POS', 'ONLINE'), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)

    cliente = db.relationship('Cliente', backref='ventas')
    empleado = db.relationship('Empleado', backref='ventas')
    sucursal = db.relationship('Sucursal', backref='ventas')
    detalles = db.relationship('DetalleVenta', backref='venta', cascade='all, delete-orphan')


class DetalleVenta(db.Model):
    __tablename__ = 'DetalleVenta'
    idDetalle = db.Column(db.Integer, primary_key=True)
    idVenta = db.Column(db.Integer, db.ForeignKey('Venta.idVenta'), nullable=False)
    idProducto = db.Column(db.Integer, db.ForeignKey('Producto.idProducto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    producto = db.relationship('Producto')

class Devolucion(db.Model):
    __tablename__ = 'Devolucion'
    idDevolucion = db.Column(db.Integer, primary_key=True)
    idVenta = db.Column(db.Integer, db.ForeignKey('Venta.idVenta'), nullable=False)
    idProducto = db.Column(db.Integer, db.ForeignKey('Producto.idProducto'), nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, default=datetime.utcnow)

    venta = db.relationship('Venta')
    producto = db.relationship('Producto')



