from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Vendor, Project, MeasurementEntry
import os
from datetime import datetime

# Set upload folder
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ========== LOGIN ==========
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["user_id"] = user.id
            return redirect("/dashboard")
        flash("Invalid credentials")
    return render_template("login.html")

# ========== DASHBOARD ==========
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template("dashboard.html", projects=projects)

# ========== NEW PROJECT ==========
@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        enquiry_id = generate_enquiry_id()
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
        
        drawing_file = request.files['source_drawing']
        drawing_filename = None
        if drawing_file and drawing_file.filename:
            drawing_filename = f"{datetime.utcnow().timestamp()}_{drawing_file.filename}"
            drawing_file.save(os.path.join(app.config['UPLOAD_FOLDER'], drawing_filename))

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
            source_drawing=drawing_filename
        )
        db.session.add(new_project)
        db.session.commit()
        flash('New project created successfully!', 'success')
        return redirect(url_for('dashboard'))

    vendors = Vendor.query.all()
    return render_template('new_project.html', vendors=vendors)


@app.route('/get_vendor_details/<int:vendor_id>')
def get_vendor_details(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if vendor:
        return jsonify({
            'gst_number': vendor.gst_number,
            'address': vendor.address
        })
    return jsonify({'gst_number': '', 'address': ''})


# ========== MEASUREMENT SHEET ==========
@app.route("/measurement_sheet/<int:project_id>", methods=["GET", "POST"])
def measurement_sheet(project_id):
    if "user_id" not in session:
        return redirect("/")

    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        entry = MeasurementEntry(
            project_id=project.id,
            duct_no=request.form["duct_no"],
            type=request.form["type"],
            st=request.form.get("st") or 0,
            elb=request.form.get("elb") or 0,
            red=request.form.get("red") or 0,
            vanes=request.form.get("vanes") or 0,
            dm=request.form.get("dm") or 0,
            offset=request.form.get("offset") or 0,
            shoe=request.form.get("shoe") or 0,
            w1=request.form.get("w1") or 0,
            h1=request.form.get("h1") or 0,
            w2=request.form.get("w2") or 0,
            h2=request.form.get("h2") or 0,
            degree=request.form.get("degree") or 0,
            length=request.form.get("length") or 0,
            quantity=request.form.get("quantity") or 1,
            factor=request.form.get("factor") or 1,
            area=request.form.get("area") or 0,
            gauge=request.form.get("gauge"),
            gasket=request.form.get("gasket") or 0,
            cleat=request.form.get("cleat") or 0,
            bolts=request.form.get("bolts") or 0,
            corners=request.form.get("corners") or 0,
        )
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for("measurement_sheet", project_id=project.id))

    entries = MeasurementEntry.query.filter_by(project_id=project.id).all()
    return render_template("measurement_sheet.html", project=project, entries=entries)

# ========== REGISTER VENDOR ==========
@app.route("/register_vendor", methods=["GET", "POST"])
def register_vendor():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["vendor_name"]
        gst_number = request.form["gst_number"]
        address = request.form["address"]

        vendor = Vendor(name=name, gst_number=gst_number, address=address)
        db.session.add(vendor)
        db.session.commit()
        flash("Vendor registered successfully.")
        return redirect("/register_vendor")

    return render_template("register_vendor.html")

# ========== LOGOUT ==========
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ========== ENQUIRY ID GENERATOR ==========
def generate_enquiry_id():
    last_project = Project.query.order_by(Project.id.desc()).first()
    next_number = (last_project.id + 1) if last_project else 1
    return f"VE/TN/2526/E{str(next_number).zfill(3)}"

# ========== CREATE DUMMY USER (Optional) ==========
@app.before_first_request
def create_dummy_admin():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="admin123")
        db.session.add(admin)
        db.session.commit()
