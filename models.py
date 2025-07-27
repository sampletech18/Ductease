from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

# ===== USER LOGIN =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# ===== VENDOR MASTER =====
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    gst_number = db.Column(db.String(20))
    pan_number = db.Column(db.String(20))
    address = db.Column(db.String(255))

    contacts = db.relationship("VendorContact", backref="vendor", cascade="all, delete-orphan")
    bank = db.relationship("VendorBank", uselist=False, backref="vendor", cascade="all, delete-orphan")
    projects = db.relationship("Project", backref="vendor", cascade="all, delete-orphan")

class VendorContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

class VendorBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"))
    account_holder = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    ifsc = db.Column(db.String(20))
    account_number = db.Column(db.String(30))

# ===== PROJECT MASTER =====
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(150))
    location = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.String(255))
    quotation = db.Column(db.String(255))
    project_incharge = db.Column(db.String(150))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    source_drawing = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship('Vendor', backref='projects')
# ===== MEASUREMENT ENTRY =====
class MeasurementEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    duct_no = db.Column(db.String(50))
    type = db.Column(db.String(20))
    st = db.Column(db.Float)
    elb = db.Column(db.Float)
    red = db.Column(db.Float)
    vanes = db.Column(db.Float)
    dm = db.Column(db.Float)
    offset = db.Column(db.Float)
    shoe = db.Column(db.Float)
    w1 = db.Column(db.Float)
    h1 = db.Column(db.Float)
    w2 = db.Column(db.Float)
    h2 = db.Column(db.Float)
    degree = db.Column(db.Float)
    length = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    factor = db.Column(db.Float)
    area = db.Column(db.Float)
    gauge = db.Column(db.String(10))
    gasket = db.Column(db.Float)
    cleat = db.Column(db.Float)
    bolts = db.Column(db.Integer)
    corners = db.Column(db.Integer)
