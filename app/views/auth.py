from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import SignupForm, LoginForm, SetPasswordForm
from app.utils.token import generate_confirmation_token, verify_confirmation_token
from app.utils.email import send_confirmation_email

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.signup'))

        # Create user with email only
        user = User(email=email, role='admin', name='Pending Setup')
        db.session.add(user)
        db.session.commit()

        # Generate token and send confirmation email
        token = generate_confirmation_token(email)
        try:
            if not current_app.config['MAIL_SUPPRESS_SEND']:
                send_confirmation_email(email, token)
                flash('Please check your email for confirmation link', 'info')
            else:
                # In development, display the confirmation link
                confirmation_url = f"{current_app.config['BASE_URL']}/auth/confirm/{token}"
                flash(f'Development mode - use this link to confirm: {confirmation_url}', 'info')
        except Exception as e:
            current_app.logger.error(f'Error sending email: {str(e)}')
            flash('Account created. In development mode, no email is sent.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)

@auth.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    email = verify_confirmation_token(token)
    if not email:
        flash('Invalid or expired confirmation link', 'error')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.signup'))

    if user.confirmation_token_used:
        flash('This confirmation link has already been used', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        user.name = request.form.get('name')
        user.mark_token_as_used()  # Mark token as used
        user.confirmed = True  # Set confirmed status
        db.session.commit()
        flash('Account setup completed successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/set_password.html', form=SetPasswordForm(), token=token)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(f"Request method: {request.method}")  # Debug log
    print(f"Form data: {request.form}")  # Debug log
    print(f"CSRF token in form: {form.csrf_token.current_token}")  # Debug log
    print(f"CSRF token in session: {session.get('csrf_token')}")  # Debug log
    print(f"Form errors before validation: {form.errors}")  # Debug log

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(f"Login attempt - Email: {email}")  # Debug log

        user = User.query.filter_by(email=email).first()
        print(f"User found: {user is not None}")  # Debug log
        if user:
            print(f"Password check result: {user.check_password(password)}")  # Debug log
            print(f"User confirmed status: {user.confirmed}")  # Debug log

        if user and user.check_password(password) and user.confirmed:
            login_user(user)
            return redirect(url_for('main.dashboard'))

        flash('Invalid email or password', 'error')
    else:
        print(f"Form validation errors: {form.errors}")  # Debug log
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
