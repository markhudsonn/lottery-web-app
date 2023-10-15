from wtforms import ValidationError
import re


def name_special_character_check(form, field):
    if re.search(r'[*?!\'^+%&/()=}\][{$#@<>]', field.data):
        raise ValidationError('Name must not contain any of: *?!\'^+%&/()=}\][{$#@<>')
