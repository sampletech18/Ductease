import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # From Render env var
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gst_number = db.Column(db.String(15))
    address = db.Column(db.String(200))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    gst_number = db.Column(db.String(15))
    address = db.Column(db.String(200))
    quotation = db.Column(db.String(200))
    project_incharge = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    source_drawing = db.Column(db.String(100))

# ------------------ UTILS ------------------

def generate_enquiry_id():
    prefix = "VE/TN/2526"
    latest = Project.query.order_by(Project.id.desc()).first()
    if latest and latest.enquiry_id:
        last_num = int(latest.enquiry_id.split("/")[-1][1:])  # E001 → 1
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}/E{new_num:03d}"

# ------------------ ROUTES ------------------

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    vendors = Vendor.query.all()
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

        file = request.files['source_drawing']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_project = Project(
            enquiry_id=enquiry_id,
            name=name,
            location=location,
            start_date=start_date,
            end_date=end_date,
            vendor_id=vendor_id,
            gst_number=gst_number,
            address=address,
            quotation=quotation,
            project_incharge=project_incharge,
            email=email,
            phone=phone,
            source_drawing=filename
        )
        db.session.add(new_project)
        db.session.commit()
        flash("Project created successfully!")
        return redirect(url_for('dashboard'))

    enquiry_id = generate_enquiry_id()
    return render_template('new_project.html', enquiry_id=enquiry_id, vendors=vendors)

# ------------------ INIT ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
