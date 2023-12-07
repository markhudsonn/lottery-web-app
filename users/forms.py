from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from users.validation import *


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), name_special_character_validation])
    lastname = StringField('Last Name', validators=[DataRequired(), name_special_character_validation])
    date_of_birth = StringField('Date of Birth', validators=[DataRequired(), date_of_birth_validation])
    postcode = StringField('Postcode', validators=[DataRequired(), postcode_validation])
    phone = StringField('Phone Number', validators=[DataRequired(), phone_number_validation])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=12),
                                                     password_digit_validation,
                                                     password_lowercase_validation, password_uppercase_validation,
                                                     password_special_character_validation])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match'),
                                                 Length(min=6, max=12)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    pin = StringField('Pin', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Login")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(id='password', validators=[DataRequired()])
    show_password = BooleanField('Show password', id='check')
    new_password = PasswordField(
        validators=[DataRequired(), Length(min=6, max=12),
                    password_digit_validation, password_lowercase_validation, password_uppercase_validation,
                    password_special_character_validation])
    confirm_new_password = PasswordField(
        validators=[DataRequired(), EqualTo('new_password', message='Both new password fields must be equal')])
    submit = SubmitField('Change Password')
