from flask_mail import Message
from flask import current_app, render_template
from app import mail

def send_confirmation_email(email, token):
    """Send confirmation email with token."""
    msg = Message('Confirm Your Account',
                 sender=current_app.config['MAIL_DEFAULT_SENDER'],
                 recipients=[email])

    confirmation_url = f"{current_app.config['BASE_URL']}/auth/confirm/{token}"
    msg.body = f'Please confirm your account by clicking on the following link: {confirmation_url}'
    msg.html = render_template('email/confirm.html', confirmation_url=confirmation_url)

    mail.send(msg)

def send_writer_credentials(email, password):
    msg = Message('Your Writer Account Credentials',
                 sender=current_app.config['MAIL_DEFAULT_SENDER'],
                 recipients=[email])

    login_url = f"{current_app.config['BASE_URL']}/auth/login"
    msg.body = f'Your account has been created.\nEmail: {email}\nPassword: {password}\nLogin at: {login_url}'
    msg.html = render_template('email/writer_credentials.html',
                             email=email,
                             password=password,
                             login_url=login_url)

    mail.send(msg)
