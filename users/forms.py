from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, email_validator
from users.validation import name_special_character_check, phone_number_check


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), name_special_character_check])
    lastname = StringField('Last Name', validators=[DataRequired(), name_special_character_check])
    phone = StringField('Phone Number', validators=[DataRequired(), phone_number_check])
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()
