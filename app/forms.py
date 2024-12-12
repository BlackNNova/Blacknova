from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, TextAreaField, DateTimeField, DecimalField, FileField, SubmitField
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
    submit = SubmitField('Update Order')

class CreateWriterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])

class FileUploadForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])

class ProfileUpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])

class MarkAllPaidForm(FlaskForm):
    pass  # Only CSRF token needed from parent class

class DeadlineForm(FlaskForm):
    new_deadline = DateTimeField('New Deadline', validators=[DataRequired()])

class StatusForm(FlaskForm):
    new_status = SelectField('New Status', choices=[
        ('unclaimed', 'Unclaimed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('revision', 'Revision'),
        ('invoice', 'Invoice'),
        ('paid', 'Paid')
    ], validators=[DataRequired()])

class ReassignForm(FlaskForm):
    new_writer_id = SelectField('New Writer', coerce=int, validators=[DataRequired()])
