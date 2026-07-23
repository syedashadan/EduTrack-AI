from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    SelectField,
)

from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")


class StudentForm(FlaskForm):

    student_id = StringField(
        "Student ID",
        validators=[DataRequired()]
    )

    full_name = StringField(
        "Full Name",
        validators=[DataRequired()]
    )

    gender = SelectField(
        "Gender",
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
    )

    email = StringField(
        "Email",
        validators=[Email()]
    )

    phone = StringField("Phone")

    department = StringField("Department")

    year = StringField("Year")

    section = StringField("Section")

    address = TextAreaField("Address")

    photo = FileField(
    "Student Photo",
    validators=[
        FileAllowed(["jpg", "jpeg", "png"], "Images only!")
    ]
)

    submit = SubmitField("Save Student")