from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from users.validation import *


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), name_special_character_validation])
    lastname = StringField('Last Name', validators=[DataRequired(), name_special_character_validation])
    phone = StringField('Phone Number', validators=[DataRequired(), phone_number_validation])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=12), password_digit_validation,
                                                     password_lowercase_validation, password_uppercase_validation,
                                                     password_special_character_validation])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=12)])
    pin = StringField('Pin', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
