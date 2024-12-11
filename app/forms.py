from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, TextAreaField, DateTimeField, DecimalField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from datetime import datetime

class SignupForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class SetPasswordForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class OrderForm(FlaskForm):
    writer_id = SelectField('Writer', coerce=int)  # Removed DataRequired validator
    title = StringField('Order Title', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    deadline = DateTimeField('Deadline', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    files = FileField('Files')
