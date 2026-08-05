from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    detalle = db.Column(db.String(300), nullable=False)
    categoria = db.Column(db.String(60), nullable=False)
    imagen = db.Column(db.String(120), nullable=False)
    stock = db.Column(db.Integer, default=10, nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="cliente")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    despachador_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(40), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Pendiente")

    user = db.relationship("User", foreign_keys=[user_id])
    despachador = db.relationship("User", foreign_keys=[despachador_id])
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=True)
    titulo = db.Column(db.String(120), nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product")
