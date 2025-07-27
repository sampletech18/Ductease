from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure PostgreSQL DB
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://duct_db_user:SXQ9iAKpluAXibt4xcxhakJk4uoQCFko@dpg-d2075pp5pdvs73c6q740-a.singapore-postgres.render.com/duct_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File Uploads
UPLOAD_FOLDER = os.path.join("static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ======================= MODELS =======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.Text)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    gst_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    quotation = db.Column(db.Text)
    project_incharge = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    source_drawing = db.Column(db.String(100))

# ======================= HELPERS =======================

def generate_enquiry_id():
    latest_project = Project.query.order_by(Project.id.desc()).first()
    suffix = int(latest_project.enquiry_id.split("/")[-1][1:]) + 1 if latest_project else 1
    return f"VE/TN/2526/E{str(suffix).zfill(3)}"

# ======================= ROUTES =======================

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"]
        pwd = request.form["password"]
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session["user"] = uname
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    projects = Project.query.all()
    return render_template("dashboard.html", projects=projects)

@app.route("/new_project", methods=["GET", "POST"])
def new_project():
    if "user" not in session:
        return redirect(url_for("login"))

    vendors = Vendor.query.all()

    if request.method == "POST":
        enquiry_id = generate_enquiry_id()
        name = request.form["name"]
        location = request.form["location"]
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")
        vendor_id = request.form["vendor_id"]
        gst_number = request.form["gst_number"]
        address = request.form["address"]
        quotation = request.form["quotation"]
        project_incharge = request.form["project_incharge"]
        email = request.form["email"]
        phone = request.form["phone"]

        drawing_file = request.files["source_drawing"]
        drawing_filename = ""
        if drawing_file and drawing_file.filename:
            drawing_filename = f"{enquiry_id}_{drawing_file.filename}"
            drawing_file.save(os.path.join(app.config["UPLOAD_FOLDER"], drawing_filename))

        new_proj = Project(
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
            source_drawing=drawing_filename
        )
        db.session.add(new_proj)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("new_project.html", vendors=vendors)

@app.route("/delete_project/<int:id>")
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/register_vendor", methods=["GET", "POST"])
def register_vendor():
    if request.method == "POST":
        name = request.form["name"]
        gst = request.form["gst"]
        address = request.form["address"]
        vendor = Vendor(name=name, gst_number=gst, address=address)
        db.session.add(vendor)
        db.session.commit()
        return redirect(url_for("new_project"))
    return render_template("register_vendor.html")

@app.route("/measurement_sheet/<int:project_id>")
def measurement_sheet(project_id):
    project = Project.query.get_or_404(project_id)
    return f"Measurement Sheet for Project: {project.name} (Under Construction)"

# ======================= INIT DB =======================
@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.first():
        user = User(username="admin", password="admin123")
        db.session.add(user)
        db.session.commit()

# ======================= MAIN =======================
if __name__ == "__main__":
    app.run(debug=True)
