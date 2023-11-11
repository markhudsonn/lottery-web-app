import re

from wtforms import ValidationError


def name_special_character_validation(form, field):
    """Checks if first or last name contain any special characters"""
    if re.search(r'[*?!\'^+%&/()=}\][{$#@<>]', field.data):
        raise ValidationError("Name must not contain any of: *?!\'^+%&/()=}\][{$#@<>")


def phone_number_validation(form, field):
    """"Checks if phone number in correct format"""
    if not re.search(r'^\d{4}-\d{3}-\d{4}$', field.data):
        raise ValidationError("Phone number must be in format: XXXX-XXX-XXXX")


def password_digit_validation(form, field):
    """Checks password has at least 1 digit"""
    if not re.search(r'\d', field.data):
        raise ValidationError("Password must contain at least 1 digit")


def password_lowercase_validation(form, field):
    """Checks password has at least 1 lowercase letter"""
    if not re.search(r'(?=.*[a-z])', field.data):
        raise ValidationError("Password must contain at least 1 lowercase letter")


def password_uppercase_validation(form, field):
    """Checks password has at least 1 uppercase letter"""
    if not re.search(r'(?=.*[A-Z])', field.data):
        raise ValidationError("Password must contain at least 1 uppercase letter")


def password_special_character_validation(form, field):
    """Checks password has at least 1 special character"""
    if not re.search(r'(?=.*[*?!\'^+%&/()=}\][{$#@<>])', field.data):
        raise ValidationError("Password must contain at least 1 special character")


def date_of_birth_validation(form, field):
    """Checks dob in format DD/MM/YYYY"""
    pass


def postcode_validation(form, field):
    """Checks postcode in correct format"""
    pass
