from wtforms import ValidationError
import re


def name_special_character_check(form, field):
    """Checks if first or last name contain any special characters"""
    if re.search(r'[*?!\'^+%&/()=}\][{$#@<>]', field.data):
        raise ValidationError("Name must not contain any of: *?!\'^+%&/()=}\][{$#@<>")


def phone_number_check(form, field):
    """"Checks if phone number in correct format"""
    if not re.search(r'^\d{4}-\d{3}-\d{4}$', field.data):
        raise ValidationError("Phone number must be in format: XXXX-XXX-XXXX")
