from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, email_validator


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = StringField()
    lastname = StringField()
    phone = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()
