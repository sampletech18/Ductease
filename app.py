from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key = 'secretkey'

# PostgreSQL on Render
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://duct_db_user:SXQ9iAKpluAXibt4xcxhakJk4uoQCFko@dpg-d2075pp5pdvs73c6q740-a.singapore-postgres.render.com/duct_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --------------------- MODELS ---------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.String(200))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    quotation = db.Column(db.String(100))
    project_incharge = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    source_drawing = db.Column(db.String(200))

class MeasurementSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    duct_no = db.Column(db.String(50))
    type = db.Column(db.String(50))
    st = db.Column(db.String(10))
    elb = db.Column(db.String(10))
    red = db.Column(db.String(10))
    vanes = db.Column(db.String(10))
    dm = db.Column(db.String(10))
    offset = db.Column(db.String(10))
    shoe = db.Column(db.String(10))
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
    bolts = db.Column(db.Float)
    corner = db.Column(db.Float)

# --------------------- ROUTES ---------------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session['user'] = uname
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register_vendor', methods=['GET', 'POST'])
def register_vendor():
    if request.method == 'POST':
        name = request.form['name']
        gst = request.form['gst_number']
        addr = request.form['address']
        vendor = Vendor(name=name, gst_number=gst, address=addr)
        db.session.add(vendor)
        db.session.commit()
        return redirect(url_for('register_vendor'))
    vendors = Vendor.query.all()
    return render_template('register_vendor.html', vendors=vendors)

@app.route('/get_vendor_details/<int:vendor_id>')
def get_vendor_details(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if vendor:
        return jsonify({'gst_number': vendor.gst_number, 'address': vendor.address})
    return jsonify({})

def generate_enquiry_id():
    last = Project.query.order_by(Project.id.desc()).first()
    if last and last.enquiry_id:
        last_num = int(last.enquiry_id.split("/")[-1][1:])
    else:
        last_num = 0
    new_num = str(last_num + 1).zfill(3)
    return f"VE/TN/2526/E{new_num}"

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        data = request.form
        file = request.files['source_drawing']
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        proj = Project(
            enquiry_id=data['enquiry_id'],
            name=data['name'],
            location=data['location'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            vendor_id=data['vendor_id'],
            gst_number=data['gst_number'],
            address=data['address'],
            quotation=data['quotation'],
            project_incharge=data['project_incharge'],
            email=data['email'],
            phone=data['phone'],
            source_drawing=filename
        )
        db.session.add(proj)
        db.session.commit()
        return redirect(url_for('dashboard'))
    vendors = Vendor.query.all()
    enquiry_id = generate_enquiry_id()
    return render_template('new_project.html', vendors=vendors, enquiry_id=enquiry_id)

@app.route('/measurement_sheet/<int:project_id>', methods=['GET', 'POST'])
def measurement_sheet(project_id):
    project = Project.query.get(project_id)
    if not project:
        return "Project not found"
    if request.method == 'POST':
        data = request.get_json()
        for row in data:
            entry = MeasurementSheet(
                project_id=project_id,
                duct_no=row['duct_no'],
                type=row['type'],
                st=row.get('st'),
                elb=row.get('elb'),
                red=row.get('red'),
                vanes=row.get('vanes'),
                dm=row.get('dm'),
                offset=row.get('offset'),
                shoe=row.get('shoe'),
                w1=row['w1'],
                h1=row['h1'],
                w2=row['w2'],
                h2=row['h2'],
                degree=row['degree'],
                length=row['length'],
                quantity=row['quantity'],
                factor=row['factor'],
                area=row['area'],
                gauge=row['gauge'],
                gasket=row['gasket'],
                cleat=row['cleat'],
                bolts=row['bolts'],
                corner=row['corner']
            )
            db.session.add(entry)
        db.session.commit()
        return jsonify({'status': 'success'})
    return render_template('measurement_sheet.html', project=project)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------- DB CREATE -------------------
with app.app_context():
    db.create_all()
