import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# PostgreSQL connection (Replace with your actual URL or use os.environ)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://duct_db_user:SXQ9iAKpluAXibt4xcxhakJk4uoQCFko@dpg-d2075pp5pdvs73c6q740-a.singapore-postgres.render.com/duct_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    gst_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    communications = db.relationship('VendorContact', backref='vendor', cascade="all, delete")

class VendorContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(120))
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    quotation = db.Column(db.String(200))
    project_incharge = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    source_drawing = db.Column(db.String(200))

# -------------- AUTH ----------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -------------- VENDOR REGISTRATION ----------------

@app.route('/register_vendor', methods=['GET', 'POST'])
def register_vendor():
    if request.method == 'POST':
        vendor = Vendor(
            name=request.form['name'],
            gst_number=request.form['gst_number'],
            address=request.form['address']
        )
        db.session.add(vendor)
        db.session.flush()

        contacts = zip(request.form.getlist('contact_name'),
                       request.form.getlist('contact_email'),
                       request.form.getlist('contact_phone'))
        for name, email, phone in contacts:
            db.session.add(VendorContact(vendor_id=vendor.id, name=name, email=email, phone=phone))

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('register_vendor.html')

# -------------- PROJECT CREATION ----------------

def generate_enquiry_id():
    prefix = "VE/TN/2526/"
    last_project = Project.query.order_by(Project.id.desc()).first()
    number = int(last_project.enquiry_id.split('/')[-1][1:]) + 1 if last_project else 1
    return prefix + f"E{number:03d}"

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    vendors = Vendor.query.all()
    if request.method == 'POST':
        filename = None
        if 'source_drawing' in request.files:
            drawing = request.files['source_drawing']
            if drawing.filename:
                filename = secure_filename(str(uuid.uuid4()) + "_" + drawing.filename)
                drawing.save(os.path.join("uploads", filename))

        project = Project(
            enquiry_id=generate_enquiry_id(),
            name=request.form['name'],
            location=request.form['location'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
            vendor_id=request.form['vendor_id'],
            gst_number=request.form['gst_number'],
            address=request.form['address'],
            quotation=request.form['quotation'],
            project_incharge=request.form['project_incharge'],
            email=request.form['email'],
            phone=request.form['phone'],
            source_drawing=filename
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('new_project.html', vendors=vendors)

# ---------------- INIT ----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="admin123"))
            db.session.commit()
    app.run(debug=True)
