from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    gst_number = db.Column(db.String(20))
    address = db.Column(db.String(255))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True)
    client_name = db.Column(db.String(150))
    site_location = db.Column(db.String(200))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    drawing_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship('Vendor', backref='projects')

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

    project = db.relationship('Project', backref='measurements')
