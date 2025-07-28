from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from sqlalchemy import text
from flask import redirect, url_for


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# PostgreSQL DB URL (from Render)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://duct_db_user:SXQ9iAKpluAXibt4xcxhakJk4uoQCFko@dpg-d2075pp5pdvs73c6q740-a.singapore-postgres.render.com/duct_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- Models --------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # plain text for demo only

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gst_number = db.Column(db.String(50))
    pan_number = db.Column(db.String(50))
    address = db.Column(db.String(200))

    contacts = db.relationship('VendorContact', backref='vendor', cascade='all, delete-orphan')
    bank_detail = db.relationship('BankDetail', backref='vendor', uselist=False, cascade='all, delete-orphan')

class VendorContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

class BankDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    account_holder = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    ifsc = db.Column(db.String(20))
    account_number = db.Column(db.String(30))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    gst_number = db.Column(db.String(50))
    address = db.Column(db.String(200))
    quotation = db.Column(db.String(200))
    project_incharge = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    source_drawing = db.Column(db.String(200))

class MeasurementSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    duct_no = db.Column(db.String(50))
    duct_type = db.Column(db.String(50))
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
    gasket = db.Column(db.Float)
    cleat = db.Column(db.Float)
    bolts = db.Column(db.Float)
    corner = db.Column(db.Float)
    gauge = db.Column(db.String(10))

# -------------------- Routes --------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        enquiry_id = request.form['enquiry_id']
        name = request.form['name']
        location = request.form['location']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        vendor_id = request.form['vendor_id']
        gst_number = request.form['gst_number']
        address = request.form['address']
        quotation = request.form['quotation']
        project_incharge = request.form['project_incharge']
        email = request.form['email']
        phone = request.form['phone']
        source_drawing = request.files['source_drawing']

        drawing_filename = source_drawing.filename
        drawing_path = os.path.join('static/uploads', drawing_filename)
        os.makedirs(os.path.dirname(drawing_path), exist_ok=True)
        source_drawing.save(drawing_path)

        new_proj = Project(
            enquiry_id=enquiry_id, name=name, location=location,
            start_date=start_date, end_date=end_date,
            vendor_id=vendor_id, gst_number=gst_number, address=address,
            quotation=quotation, project_incharge=project_incharge,
            email=email, phone=phone, source_drawing=drawing_path
        )
        db.session.add(new_proj)
        db.session.commit()
        return redirect(url_for('dashboard'))

    vendors = Vendor.query.all()
    return render_template('new_project.html', vendors=vendors)

@app.route('/generate_enquiry_id')
def generate_enquiry_id():
    latest_project = Project.query.order_by(Project.id.desc()).first()
    count = latest_project.id + 1 if latest_project else 1
    year = datetime.now().year
    enquiry_id = f"VE/TN/{year}/E{str(count).zfill(3)}"
    return jsonify({'enquiry_id': enquiry_id})

@app.route('/vendor/<int:vendor_id>')
def get_vendor_details(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if vendor:
        return jsonify({'gst_number': vendor.gst_number, 'address': vendor.address})
    return jsonify({'error': 'Vendor not found'}), 404


@app.route('/register_vendor', methods=['GET', 'POST'])
def register_vendor():
    if request.method == 'POST':
        # Vendor main details
        name = request.form.get('name')
        gst_number = request.form.get('gst_number')
        pan_number = request.form.get('pan_number')
        address = request.form.get('address')

        # Create vendor object
        vendor = Vendor(name=name, gst_number=gst_number, pan_number=pan_number, address=address)
        db.session.add(vendor)
        db.session.commit()

        # Communication details
        contact_names = request.form.getlist('contact_name[]')
        contact_designations = request.form.getlist('contact_designation[]')
        contact_emails = request.form.getlist('contact_email[]')
        contact_phones = request.form.getlist('contact_phone[]')

        for name, desig, email, phone in zip(contact_names, contact_designations, contact_emails, contact_phones):
            if name or desig or email or phone:  # Avoid saving empty rows
                contact = VendorContact(
                    vendor_id=vendor.id,
                    name=name,
                    designation=desig,
                    email=email,
                    phone=phone
                )
                db.session.add(contact)

        # Bank details
        account_holder = request.form.get('account_holder')
        bank_name = request.form.get('bank_name')
        branch = request.form.get('branch')
        ifsc = request.form.get('ifsc')
        account_number = request.form.get('account_number')

        bank_detail = VendorBankDetail(
            vendor_id=vendor.id,
            account_holder=account_holder,
            bank_name=bank_name,
            branch=branch,
            ifsc=ifsc,
            account_number=account_number
        )
        db.session.add(bank_detail)

        db.session.commit()
        return redirect(url_for('dashboard'))  # or another success page

    return render_template('register_vendor.html')


 




@app.route('/reset_db')
def reset_db():
    try:
        db.session.execute(text('DROP TABLE IF EXISTS measurement_entry CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS project CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS vendor_contact CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS bank_detail CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS vendor CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))  # <- FIXED HERE
        db.session.commit()
        return "✅ All specified tables dropped."
    except Exception as e:
        db.session.rollback()
        return f"❌ Error: {e}"




# -------------------- Init DB & Admin User --------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Add dummy admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
            print("Dummy admin user created.")

    app.run(debug=True)
