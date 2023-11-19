import re

from wtforms import ValidationError


def name_special_character_validation(form, field):
    """Checks if first or last name contain any special characters"""
    if re.search(r'[*?!\'^+%&/()=}\]\[{$#@<>]', field.data):
        raise ValidationError("Name must not contain any special characters")


def phone_number_validation(form, field):
    """"Checks if phone number in format XXXX-XXX-XXXX"""
    if not re.search(r'^\d{4}-\d{3}-\d{4}$', field.data):
        raise ValidationError("Phone number must be in format: XXXX-XXX-XXXX")


def password_digit_validation(form, field):
    """Checks password has at least 1 digit"""
    if not re.search(r'\d', field.data):
        raise ValidationError("Password must contain at least 1 digit")


def password_lowercase_validation(form, field):
    """Checks password has at least 1 lowercase letter"""
    if not re.search(r'[a-z]', field.data):
        raise ValidationError("Password must contain at least 1 lowercase letter")


def password_uppercase_validation(form, field):
    """Checks password has at least 1 uppercase letter"""
    if not re.search(r'[A-Z]', field.data):
        raise ValidationError("Password must contain at least 1 uppercase letter")


def password_special_character_validation(form, field):
    """Checks password has at least 1 special character"""
    if not re.search(r'[*?!\'^+%&/()=}\]\[{$#@<>]', field.data):
        raise ValidationError("Password must contain at least 1 special character")


def date_of_birth_validation(form, field):
    """Checks dob in format DD/MM/YYYY"""
    days_pattern = r'^(0?[1-9])|([12][0-9]|3[01])$'  # 01-31
    months_pattern = r'^(0?[1-9]|1[012])$'  # 01-12
    years_pattern = r'^(19|20)\d\d$'  # 19XX-20XX
    if not re.search(r'^\d{2}/\d{2}/\d{4}$', field.data):
        raise ValidationError("Date of birth must be in format: DD/MM/YYYY")
    if not re.search(days_pattern, field.data[0:2]):
        raise ValidationError("Date of birth must be in format: DD/MM/YYYY, DD must be between 01-31")
    if not re.search(months_pattern, field.data[3:5]):
        raise ValidationError("Date of birth must be in format: DD/MM/YYYY, MM must be between 01-12")
    if not re.search(years_pattern, field.data[6:10]):
        raise ValidationError("Date of birth must be in format: DD/MM/YYYY, YYYY must be between 1900-2099")


def postcode_validation(form, field):
    """Checks postcode in correct format"""
    pattern1 = r'^[A-Z][0-9] [0-9][A-Z][A-Z]$'  # XYY YXX
    pattern2 = r'^[A-Z][0-9][0-9] [0-9][A-Z][A-Z]$'  # XYY YXX
    pattern3 = r'^[A-Z][A-Z][0-9] [0-9][A-Z][A-Z]$'  # XXY YXX

    if not re.search(pattern1, field.data) and not re.search(pattern2, field.data) and not re.search(pattern3,
                                                                                                     field.data):
        raise ValidationError(
            "Postcode must be in format: XYY YXX, XYY YXX or XXY YXX (X = uppercase letter, Y = number)")
