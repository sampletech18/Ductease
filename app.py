from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://duct_db_user:SXQ9iAKpluAXibt4xcxhakJk4uoQCFko@dpg-d2075pp5pdvs73c6q740-a.singapore-postgres.render.com/duct_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.String(200))

class VendorContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

class VendorBankDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    bank_name = db.Column(db.String(100))
    acc_no = db.Column(db.String(50))
    ifsc = db.Column(db.String(20))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True)
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
    type = db.Column(db.String(20))
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

@app.before_first_request
def seed_admin():
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password='admin123'))
        db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register_vendor', methods=['GET', 'POST'])
def register_vendor():
    if request.method == 'POST':
        vendor = Vendor(name=request.form['name'], gst_number=request.form['gst'], address=request.form['address'])
        db.session.add(vendor)
        db.session.commit()

        for name, phone, email in zip(request.form.getlist('contact_name'), request.form.getlist('contact_phone'), request.form.getlist('contact_email')):
            db.session.add(VendorContact(vendor_id=vendor.id, name=name, phone=phone, email=email))

        for bank, acc, ifsc in zip(request.form.getlist('bank_name'), request.form.getlist('acc_no'), request.form.getlist('ifsc_code')):
            db.session.add(VendorBankDetail(vendor_id=vendor.id, bank_name=bank, acc_no=acc, ifsc=ifsc))

        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('register_vendor.html')

def generate_enquiry_id():
    year = datetime.now().year
    count = Project.query.count() + 1
    return f"VE/TN/{year}/E{str(count).zfill(3)}"

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    vendors = Vendor.query.all()
    if request.method == 'POST':
        file = request.files['source_drawing']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        project = Project(
            enquiry_id=generate_enquiry_id(),
            name=request.form['name'],
            location=request.form['location'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
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
    return render_template('new_project.html', vendors=vendors, enquiry_id=generate_enquiry_id())

@app.route('/get_vendor_details/<int:vendor_id>')
def get_vendor_details(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    return jsonify({'gst': vendor.gst_number, 'address': vendor.address})

@app.route('/measurement_sheet/<int:project_id>', methods=['GET', 'POST'])
def measurement_sheet(project_id):
    if request.method == 'POST':
        data = request.json
        for entry in data['entries']:
            ms = MeasurementSheet(project_id=project_id, **entry)
            db.session.add(ms)
        db.session.commit()
        return jsonify({'status': 'success'})
    return render_template('measurement_sheet.html', project_id=project_id)

if __name__ == '__main__':
    app.run()
