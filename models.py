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
    precio = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    referencia = db.Column(db.String(50), unique=True)
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
    total = db.Column(db.Integer, nullable=False)

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
    subtotal = db.Column(db.Integer, nullable=False)

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

class Fidelizacion(db.Model):
    __tablename__ = 'Fidelizacion'
    idMovimiento = db.Column(db.Integer, primary_key=True)
    idCliente = db.Column(db.Integer, db.ForeignKey('Cliente.idCliente'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    puntosGanados = db.Column(db.Integer, default=0)
    puntosRedimidos = db.Column(db.Integer, default=0)
    saldo = db.Column(db.Integer, nullable=False)

    cliente = db.relationship('Cliente', backref='movimientos_fidelizacion')


class PedidoProveedor(db.Model):
    __tablename__ = 'PedidoProveedor'
    idPedido = db.Column(db.Integer, primary_key=True)
    idProveedor = db.Column(db.Integer, db.ForeignKey('Proveedor.idProveedor'), nullable=False)
    fechaPedido = db.Column(db.Date, default=datetime.utcnow)
    estado = db.Column(db.Enum('PENDIENTE', 'ENVIADO', 'RECIBIDO', 'CANCELADO'), default='PENDIENTE')

    proveedor = db.relationship('Proveedor', backref='pedidos')


class DetallePedido(db.Model):
    __tablename__ = 'DetallePedido'
    idDetallePedido = db.Column(db.Integer, primary_key=True)
    idPedido = db.Column(db.Integer, db.ForeignKey('PedidoProveedor.idPedido'), nullable=False)
    idProducto = db.Column(db.Integer, db.ForeignKey('Producto.idProducto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    pedido = db.relationship('PedidoProveedor', backref='detalles')
    producto = db.relationship('Producto')


class InventarioSucursal(db.Model):
    __tablename__ = 'InventarioSucursal'
    idInventario = db.Column(db.Integer, primary_key=True)
    idSucursal = db.Column(db.Integer, db.ForeignKey('Sucursal.idSucursal'), nullable=False)
    idProducto = db.Column(db.Integer, db.ForeignKey('Producto.idProducto'), nullable=False)
    stockActual = db.Column(db.Integer, default=0)
    stockMinimo = db.Column(db.Integer, default=0)

    sucursal = db.relationship('Sucursal', backref='inventarios')
    producto = db.relationship('Producto')


class Promocion(db.Model):
    __tablename__ = 'Promocion'
    idPromocion = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    fechaInicio = db.Column(db.Date, nullable=False)
    fechaFin = db.Column(db.Date, nullable=False)
    descuento = db.Column(db.Integer, nullable=False)


class PromocionProducto(db.Model):
    __tablename__ = 'PromocionProducto'
    idPromocion = db.Column(db.Integer, db.ForeignKey('Promocion.idPromocion'), primary_key=True)
    idProducto = db.Column(db.Integer, db.ForeignKey('Producto.idProducto'), primary_key=True)

    promocion = db.relationship('Promocion', backref='productos')
    producto = db.relationship('Producto', backref='promociones')



