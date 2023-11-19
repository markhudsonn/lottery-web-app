from flask import flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class DrawForm(FlaskForm):
    number1 = IntegerField(id='no1', validators=[DataRequired(), NumberRange(min=1, max=60)])
    number2 = IntegerField(id='no2', validators=[DataRequired(), NumberRange(min=1, max=60)])
    number3 = IntegerField(id='no3', validators=[DataRequired(), NumberRange(min=1, max=60)])
    number4 = IntegerField(id='no4', validators=[DataRequired(), NumberRange(min=1, max=60)])
    number5 = IntegerField(id='no5', validators=[DataRequired(), NumberRange(min=1, max=60)])
    number6 = IntegerField(id='no6', validators=[DataRequired(), NumberRange(min=1, max=60)])

    submit = SubmitField("Submit Draw")

    # Flask custom validator
    def validate(self, **kwargs):
        standard_validators = FlaskForm.validate(self)
        if standard_validators:
            nums = [self.number1.data, self.number2.data, self.number3.data,
                    self.number4.data, self.number5.data, self.number6.data]

            if len(nums) != len(
                    set(nums)):  # if len of list not equal to len of set (unique values only) then duplicates exist
                flash('You cannot have duplicate numbers')
                return False
            return True
        return False
