from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shops = db.relationship('Shop', backref='owner_user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Shop(db.Model):
    __tablename__ = 'shops'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shop_name = db.Column(db.String(150), nullable=False)
    logo_path = db.Column(db.String(255), nullable=True)
    owner_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    gstin = db.Column(db.String(20), nullable=True)
    invoice_prefix = db.Column(db.String(10), default='INV-')
    footer_note = db.Column(db.String(255), default='Thank you for shopping with us!')
    tax_type = db.Column(db.String(20), default='GST') # GST or NON_GST
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    categories = db.relationship('Category', backref='shop', lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='shop', lazy=True, cascade="all, delete-orphan")
    customers = db.relationship('Customer', backref='shop', lazy=True, cascade="all, delete-orphan")
    invoices = db.relationship('Invoice', backref='shop', lazy=True, cascade="all, delete-orphan")


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    products = db.relationship('Product', backref='category_rel', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), nullable=True)
    purchase_price = db.Column(db.Float, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    gst_rate = db.Column(db.Float, default=0.0) # 0, 5, 12, 18, 28
    stock_qty = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20), default='Piece') # Piece, Kg, Gram, Liter, Meter, Box, Packet
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    whatsapp = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    total_spent = db.Column(db.Float, default=0.0)
    total_invoices = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoices = db.relationship('Invoice', backref='customer_rel', lazy=True)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    
    invoice_number = db.Column(db.String(30), nullable=False, index=True)
    secure_token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Financial breakdown
    subtotal = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    taxable_amount = db.Column(db.Float, default=0.0)
    total_tax = db.Column(db.Float, default=0.0)
    cgst_amount = db.Column(db.Float, default=0.0)
    sgst_amount = db.Column(db.Float, default=0.0)
    igst_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    
    payment_method = db.Column(db.String(30), default='Cash') # Cash, UPI, Card, Bank Transfer, Other
    payment_status = db.Column(db.String(20), default='Paid') # Paid, Pending, Partial
    amount_paid = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('InvoiceItem', backref='invoice_rel', lazy=True, cascade="all, delete-orphan")


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), default='Piece')
    rate = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, default=0.0) # Percentage or flat
    gst_rate = db.Column(db.Float, default=0.0)
    line_tax = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, nullable=False, default=0.0)
