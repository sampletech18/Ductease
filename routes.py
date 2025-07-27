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
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
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
@app.route("/new_project", methods=["GET", "POST"])
def new_project():
    if "user_id" not in session:
        return redirect("/")

    vendors = Vendor.query.all()

    if request.method == "POST":
        enquiry_id = generate_enquiry_id()
        client_name = request.form["client_name"]
        site_location = request.form["site_location"]
        vendor_id = request.form["vendor_id"]
        drawing_file = request.files["drawing"]

        filename = secure_filename(drawing_file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        drawing_file.save(path)

        new_project = Project(
            enquiry_id=enquiry_id,
            client_name=client_name,
            site_location=site_location,
            vendor_id=vendor_id,
            drawing_filename=filename
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect("/dashboard")

    return render_template("new_project.html", vendors=vendors)

# ========== MEASUREMENT SHEET ==========
@app.route("/measurement_sheet/<int:project_id>", methods=["GET", "POST"])
def measurement_sheet(project_id):
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


@app.route("/register_vendor", methods=["GET", "POST"])
def register_vendor():
    if request.method == "POST":
        # Vendor main info
        name = request.form["vendor_name"]
        gst = request.form["gst_number"]
        pan = request.form["pan_number"]
        address = request.form["address"]

        vendor = Vendor(name=name, gst_number=gst, pan_number=pan, address=address)
        db.session.add(vendor)
        db.session.flush()  # Get vendor.id before committing

        # Contacts (multiple)
        names = request.form.getlist("contact_name[]")
        designations = request.form.getlist("contact_designation[]")
        emails = request.form.getlist("contact_email[]")
        phones = request.form.getlist("contact_phone[]")

        for i in range(len(names)):
            contact = VendorContact(
                vendor_id=vendor.id,
                name=names[i],
                designation=designations[i],
                email=emails[i],
                phone=phones[i]
            )
            db.session.add(contact)

        # Bank details
        bank = VendorBank(
            vendor_id=vendor.id,
            account_holder=request.form["account_holder"],
            bank_name=request.form["bank_name"],
            branch=request.form["branch"],
            ifsc=request.form["ifsc"],
            account_number=request.form["account_number"]
        )
        db.session.add(bank)

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
