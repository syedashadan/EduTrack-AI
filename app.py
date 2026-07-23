from openpyxl import Workbook
from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Student
from forms import LoginForm, StudentForm

import os
from werkzeug.utils import secure_filename

from openpyxl import Workbook
import io

from reportlab.platypus import SimpleDocTemplate, Table

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = "Please login first."

login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():

    db.create_all()

    admin = User.query.filter_by(username="admin").first()

    if admin is None:

        admin = User(

            username="admin",

            email="admin@edutrack.com",

            password=generate_password_hash("admin123")

        )

        db.session.add(admin)

        db.session.commit()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and check_password_hash(
                user.password,
                form.password.data):

            login_user(user)

            flash("Login Successful", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid Username or Password", "danger")

    return render_template("login.html", form=form)


@app.route("/dashboard")
@login_required
def dashboard():

    total_students = Student.query.count()

    male_students = Student.query.filter_by(gender="Male").count()

    female_students = Student.query.filter_by(gender="Female").count()

    departments = db.session.query(Student.department).distinct().count()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        male_students=male_students,
        female_students=female_students,
        departments=departments,
        current_user=current_user
    
    )

@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():

    form = StudentForm()

    if request.method == "POST":
        print(form.errors)

    if form.validate_on_submit():

        filename = "default.png"

        if form.photo.data:
            file = form.photo.data
        filename = secure_filename(file.filename)

        upload_path = os.path.join(
            app.static_folder,
            "uploads",
            filename
        )

        file.save(upload_path)

        student = Student(

            student_id=form.student_id.data,

            full_name=form.full_name.data,

            gender=form.gender.data,

            email=form.email.data,

            phone=form.phone.data,

            department=form.department.data,

            year=form.year.data,

            section=form.section.data,

            address=form.address.data,

            photo=filename

        )

        db.session.add(student)

        db.session.commit()

        flash("Student Added Successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template("add_student.html", form=form)

@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    student = Student.query.get_or_404(id)

    form = StudentForm(obj=student)

    if form.validate_on_submit():

        student.student_id = form.student_id.data
        student.full_name = form.full_name.data
        student.gender = form.gender.data
        student.email = form.email.data
        student.phone = form.phone.data
        student.department = form.department.data
        student.year = form.year.data
        student.section = form.section.data
        student.address = form.address.data

        db.session.commit()

        flash("Student Updated Successfully!", "success")

        return redirect(url_for("view_students"))

    return render_template(
        "edit_student.html",
        form=form,
        student=student
    )

@app.route("/view_students")
@login_required
def view_students():

    search = request.args.get("search")

    if search:
        students = Student.query.filter(
            Student.full_name.contains(search)
        ).all()
    else:
        students = Student.query.all()

    return render_template(
        "view_students.html",
        students=students
    )

@app.route("/student/<int:id>")
@login_required
def student_profile(id):

    student = Student.query.get_or_404(id)

    return render_template(
        "student_profile.html",
        student=student
    )

@app.route("/delete_student/<int:id>")
@login_required
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)

    db.session.commit()

    flash("Student Deleted Successfully!", "success")

    return redirect(url_for("view_students"))


@app.route("/export_pdf")
@login_required
def export_pdf():

    students = Student.query.all()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    data = [["ID", "Name", "Department", "Year"]]

    for student in students:
        data.append([
            student.student_id,
            student.full_name,
            student.department,
            student.year
        ])

    table = Table(data)

    doc.build([table])

    buffer.seek(0)

    return send_file(
        buffer,
        download_name="students.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )

@app.route("/export_excel")
@login_required
def export_excel():

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    ws.append([
        "Student ID",
        "Name",
        "Gender",
        "Email",
        "Phone",
        "Department",
        "Year",
        "Section"
    ])

    students = Student.query.all()

    for student in students:
        ws.append([
            student.student_id,
            student.full_name,
            student.gender,
            student.email,
            student.phone,
            student.department,
            student.year,
            student.section
        ])

    file_name = "students.xlsx"
    wb.save(file_name)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully", "success")

    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)