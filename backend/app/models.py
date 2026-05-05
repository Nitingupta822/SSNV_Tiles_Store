from datetime import datetime
from .extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150))
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Tile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=False)
    buy_price = db.Column(db.Float)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)

class SanitaryProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150))
    customer_mobile = db.Column(db.String(15))
    total = db.Column(db.Float, nullable=False)
    gst = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('BillItem', backref='bill_ref', lazy=True, cascade="all, delete-orphan")

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))
    tile_name = db.Column(db.String(150))
    size = db.Column(db.String(50))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)

class OnlineOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_mobile = db.Column(db.String(15), nullable=False)
    customer_email = db.Column(db.String(150))
    customer_address = db.Column(db.String(300))
    tile_id = db.Column(db.Integer, db.ForeignKey('tile.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tile = db.relationship('Tile', backref='online_orders')

class SanitaryOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_mobile = db.Column(db.String(15), nullable=False)
    customer_email = db.Column(db.String(150))
    customer_address = db.Column(db.String(300))
    sanitary_id = db.Column(db.Integer, db.ForeignKey('sanitary_product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sanitary = db.relationship('SanitaryProduct', backref='online_orders')

class OtherProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    specifications = db.Column(db.String(200), nullable=True)
    buy_price = db.Column(db.Float)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=True)

class OtherOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_mobile = db.Column(db.String(15), nullable=False)
    customer_email = db.Column(db.String(150))
    customer_address = db.Column(db.String(300))
    other_id = db.Column(db.Integer, db.ForeignKey('other_product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('OtherProduct', backref='online_orders')
