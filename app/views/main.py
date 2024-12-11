from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, send_from_directory, current_app, Response
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, DateTimeField
from wtforms.validators import DataRequired
from functools import wraps
from ..models import Order, User, File
from .. import db
from datetime import datetime
import secrets
import string
from ..utils.email import send_writer_credentials
from ..forms import OrderForm
import io
import csv
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

class StatusChangeForm(FlaskForm):
    new_status = SelectField('New Status', choices=[
        ('revision', 'Send to Revision'),
        ('invoice', 'Move to Invoice')
    ])

class DeadlineExtensionForm(FlaskForm):
    new_deadline = DateTimeField('New Deadline', validators=[DataRequired()])

class DeleteForm(FlaskForm):
    pass  # No fields needed, just CSRF protection

class ReassignForm(FlaskForm):
    new_writer_id = SelectField('New Writer', coerce=int, validators=[DataRequired()])

@main.route('/dashboard')
@login_required
@admin_required
def dashboard():
    unclaimed_count = Order.query.filter_by(status='unclaimed').count()
    in_progress_count = Order.query.filter_by(status='in_progress').count()
    completed_count = Order.query.filter_by(status='completed').count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                         unclaimed_count=unclaimed_count,
                         in_progress_count=in_progress_count,
                         completed_count=completed_count,
                         recent_orders=recent_orders)

@main.route('/orders/unclaimed')
@login_required
@admin_required
def unclaimed_orders():
    """View for listing unclaimed orders."""
    orders = Order.query.filter_by(status='unclaimed').all()
    writers = User.query.filter_by(role='writer').all()
    status_form = StatusChangeForm()
    deadline_form = DeadlineExtensionForm()
    delete_form = DeleteForm()
    reassign_form = ReassignForm()
    reassign_form.new_writer_id.choices = [(w.id, f"{w.name} ({w.email})") for w in writers]

    return render_template('admin/orders/unclaimed.html',
                         title='Unclaimed Orders',
                         orders=orders,
                         writers=writers,
                         form=deadline_form,
                         status_form=status_form,
                         delete_form=delete_form,
                         reassign_form=reassign_form)

@main.route('/orders/<int:order_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status not in ['unclaimed', 'in_progress']:
        flash('Cannot delete orders in this status.', 'error')
        return redirect(url_for('main.unclaimed_orders'))

    try:
        db.session.delete(order)
        db.session.commit()
        flash('Order deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting order.', 'error')

    return redirect(url_for('main.unclaimed_orders'))

@main.route('/orders/<int:order_id>/reassign', methods=['POST'])
@login_required
@admin_required
def reassign_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status not in ['unclaimed', 'in_progress']:
        flash('Cannot reassign orders in this status.', 'error')
        return redirect(url_for('main.unclaimed_orders'))

    writer_id = request.form.get('new_writer_id')
    if not writer_id:
        flash('New writer must be selected.', 'error')
        return redirect(url_for('main.unclaimed_orders'))

    try:
        order.writer_id = writer_id
        order.status = 'unclaimed'
        db.session.commit()
        flash('Order reassigned successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error reassigning order.', 'error')

    return redirect(url_for('main.unclaimed_orders'))

@main.route('/orders/<int:order_id>/extend-deadline', methods=['POST'])
@login_required
@admin_required
def extend_deadline(order_id):
    order = Order.query.get_or_404(order_id)
    new_deadline = request.form.get('new_deadline')

    if not new_deadline:
        flash('New deadline must be provided.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))

    try:
        # Parse the datetime string from the form
        new_deadline_dt = datetime.strptime(new_deadline, '%Y-%m-%dT%H:%M')

        # Validate that new deadline is in the future
        if new_deadline_dt <= datetime.now():
            flash('New deadline must be in the future.', 'error')
            return redirect(request.referrer or url_for('main.dashboard'))

        order.deadline = new_deadline_dt
        db.session.commit()
        flash('Deadline extended successfully.', 'success')
    except ValueError as e:
        db.session.rollback()
        flash(f'Invalid deadline format: {str(e)}', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Error extending deadline.', 'error')

    return redirect(request.referrer or url_for('main.dashboard'))

@main.route('/orders/in-progress')
@login_required
@admin_required
def in_progress_orders():
    orders = Order.query.filter_by(status='in_progress').all()
    writers = User.query.filter_by(role='writer').all()
    now = datetime.now()
    form = DeadlineExtensionForm()  # Change back to 'form' to match template
    status_form = StatusChangeForm()
    delete_form = DeleteForm()
    reassign_form = ReassignForm()
    reassign_form.new_writer_id.choices = [(w.id, f"{w.name} ({w.email})") for w in writers]
    return render_template('admin/orders/in_progress.html', title='Orders in Progress',
                         orders=orders, writers=writers, now=now, form=form,
                         status_form=status_form, delete_form=delete_form,
                         reassign_form=reassign_form)

@main.route('/orders/completed')
@login_required
@admin_required
def completed_orders():
    orders = Order.query.filter_by(status='completed').all()
    writers = User.query.filter_by(role='writer').all()
    form = DeadlineExtensionForm()
    status_form = StatusChangeForm()
    reassign_form = ReassignForm()
    delete_form = DeleteForm()
    reassign_form.new_writer_id.choices = [(w.id, f"{w.name} ({w.email})") for w in writers]
    return render_template('admin/orders/completed.html',
                         title='Completed Orders',
                         orders=orders,
                         form=form,
                         status_form=status_form,
                         reassign_form=reassign_form,
                         delete_form=delete_form)

@main.route('/orders/<int:order_id>/change-status', methods=['POST'])
@login_required
@admin_required
def change_order_status(order_id):
    form = FlaskForm()  # Create a form instance for CSRF validation
    if not form.validate():
        flash('Invalid form submission.', 'error')
        return redirect(url_for('main.in_progress_orders'))

    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('new_status')
    current_status = order.status

    # Define valid transitions for each status
    valid_transitions = {
        'in_progress': ['completed', 'revision'],
        'completed': ['revision', 'invoice'],
        'revision': ['completed'],
        'invoice': ['paid'],
        'paid': ['invoice', 'completed', 'revision']
    }

    if not new_status or current_status not in valid_transitions or new_status not in valid_transitions[current_status]:
        flash('Invalid status change requested.', 'error')
        return redirect(url_for(f'main.{current_status}_orders'))

    try:
        order.status = new_status
        db.session.commit()
        flash(f'Order status changed to {new_status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error changing order status.', 'error')

    return redirect(url_for(f'main.{new_status}_orders'))

@main.route('/files/<int:file_id>/download')
@login_required
@admin_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                             file.filename,
                             as_attachment=True)

@main.route('/orders/revision')
@login_required
@admin_required
def revision_orders():
    orders = Order.query.filter_by(status='revision').all()
    form = StatusChangeForm()
    return render_template('admin/orders/revision.html',
                         title='Orders in Revision',
                         orders=orders,
                         form=form)

@main.route('/orders/<int:order_id>/mark-complete', methods=['POST'])
@login_required
@admin_required
def mark_order_complete(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'revision':
        flash('Only orders in revision can be marked as complete.', 'error')
        return redirect(url_for('main.revision_orders'))

    try:
        order.status = 'completed'
        db.session.commit()
        flash('Order marked as complete.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error marking order as complete.', 'error')

    return redirect(url_for('main.revision_orders'))

@main.route('/orders/invoice')
@login_required
@admin_required
def invoice_orders():
    writers_with_orders = db.session.query(User).join(Order).filter(
        User.role == 'writer',
        Order.status == 'invoice'
    ).distinct().all()

    writer_data = []
    total_amount = 0
    for writer in writers_with_orders:
        unpaid_orders = Order.query.filter_by(writer_id=writer.id, status='invoice').all()
        writer_total = sum(order.price for order in unpaid_orders)
        total_amount += writer_total

        writer_info = {
            'id': writer.id,
            'name': writer.name,
            'email': writer.email,
            'phone': writer.phone,
            'unpaid_count': len(unpaid_orders),
            'total_amount': writer_total
        }
        writer_data.append(writer_info)

    return render_template('admin/orders/invoice.html',
                         title='Invoice/Unpaid Orders',
                         writers=writer_data,
                         total_amount=total_amount)

@main.route('/writers/<int:writer_id>/mark-paid', methods=['POST'])
@login_required
@admin_required
def mark_writer_paid(writer_id):
    try:
        orders = Order.query.filter_by(writer_id=writer_id, status='invoice').all()
        for order in orders:
            order.status = 'paid'
        db.session.commit()
        flash('Orders marked as paid successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error marking orders as paid.', 'error')

    return redirect(url_for('main.invoice_orders'))

@main.route('/mark-all-paid', methods=['POST'])
@login_required
@admin_required
def mark_all_paid():
    try:
        orders = Order.query.filter_by(status='invoice').all()
        for order in orders:
            order.status = 'paid'
        db.session.commit()
        flash('All orders marked as paid successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error marking orders as paid.', 'error')

    return redirect(url_for('main.invoice_orders'))

@main.route('/export-invoice-csv')
@login_required
@admin_required
def export_invoice_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Writer Name', 'Email', 'Phone', 'Order Count', 'Total Amount'])

    writers_with_orders = db.session.query(User).join(Order).filter(
        User.role == 'writer',
        Order.status == 'invoice'
    ).distinct().all()

    for writer in writers_with_orders:
        unpaid_orders = Order.query.filter_by(writer_id=writer.id, status='invoice').all()
        writer_total = sum(order.price for order in unpaid_orders)
        writer.writerow([
            writer.name,
            writer.email,
            writer.phone,
            len(unpaid_orders),
            f"${writer_total:.2f}"
        ])

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=invoice_report.csv'}
    )

@main.route('/orders/paid')
@login_required
@admin_required
def paid_orders():
    orders = Order.query.filter_by(status='paid').all()
    return render_template('admin/orders/paid.html',
                         title='Paid Orders',
                         orders=orders)

@main.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    writers = User.query.filter_by(role='writer').all()
    form = OrderForm()
    form.writer_id.choices = [(w.id, f"{w.name} ({w.email})") for w in writers]

    if form.validate_on_submit():
        if order.status in ['invoice', 'paid']:
            flash('Cannot edit orders in invoice or paid status.', 'error')
            return redirect(url_for('main.dashboard'))

        try:
            order.writer_id = form.writer_id.data
            order.title = form.title.data
            order.description = form.description.data
            order.deadline = form.deadline.data
            order.price = form.price.data

            db.session.commit()
            flash('Order updated successfully.', 'success')

            # Redirect based on order status
            if order.status == 'unclaimed':
                return redirect(url_for('main.unclaimed_orders'))
            elif order.status == 'in_progress':
                return redirect(url_for('main.in_progress_orders'))
            elif order.status == 'completed':
                return redirect(url_for('main.completed_orders'))
            elif order.status == 'revision':
                return redirect(url_for('main.revision_orders'))
            else:
                return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash('Error updating order.', 'error')
            return redirect(url_for('main.dashboard'))

    # Pre-populate form with existing order data
    if request.method == 'GET':
        form.writer_id.data = order.writer_id
        form.title.data = order.title
        form.description.data = order.description
        form.deadline.data = order.deadline
        form.price.data = order.price

    return render_template('admin/orders/edit.html', form=form, order=order, writers=writers)

@main.route('/orders/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_order():
    writers = User.query.filter_by(role='writer').all()

    if request.method == 'POST':
        writer_id = request.form.get('writer_id')
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        price = request.form.get('price')
        files = request.files.getlist('files')

        # Debug logging
        current_app.logger.info(f'Raw deadline value: {deadline}')
        current_app.logger.info(f'Form data received: writer_id={writer_id}, title={title}, deadline={deadline}, price={price}')
        current_app.logger.info(f'Files received: {len(files)}')

        if not all([title, description, deadline, price]):  # Remove writer_id from required fields
            missing = [field for field, value in {'title': title,
                'description': description, 'deadline': deadline, 'price': price}.items() if not value]
            flash(f'Missing required fields: {", ".join(missing)}', 'error')
            return render_template('admin/create_order.html', writers=writers)

        try:
            # Try to fix the year if it's malformed
            if deadline and len(deadline) >= 4:
                year_str = deadline[:4]
                if int(year_str) > 9999:  # If year is malformed
                    current_app.logger.info(f'Fixing malformed year in deadline: {deadline}')
                    deadline = f"2024{deadline[4:]}"
                    current_app.logger.info(f'Fixed deadline: {deadline}')

            # Convert the datetime string to a datetime object
            deadline_dt = datetime.strptime(deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
            current_app.logger.info(f'Parsed deadline: {deadline_dt}')

            # Create the order
            order = Order(
                writer_id=writer_id,
                title=title,
                description=description,
                deadline=deadline_dt,
                price=float(price),
                status='unclaimed'
            )
            db.session.add(order)
            db.session.flush()  # Get order ID without committing

            # Handle file uploads
            for uploaded_file in files:
                if uploaded_file.filename:
                    # Generate secure filename
                    filename = secrets.token_hex(8) + '_' + secure_filename(uploaded_file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                    # Save file to disk
                    uploaded_file.save(filepath)

                    # Create file record
                    file_record = File(
                        order_id=order.id,
                        filename=filename,
                        original_filename=uploaded_file.filename
                    )
                    db.session.add(file_record)

            db.session.commit()
            flash('Order created successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating order: {str(e)}')
            flash(f'Error creating order: {str(e)}', 'error')
            return render_template('admin/create_order.html', writers=writers)

    return render_template('admin/create_order.html', writers=writers)

@main.route('/writers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_writer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if not all([name, email, phone]):
            flash('All fields are required.', 'error')
            return render_template('admin/create_writer.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('admin/create_writer.html')

        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        try:
            writer = User(
                name=name,
                email=email,
                phone=phone,
                role='writer'
            )
            writer.set_password(password)
            db.session.add(writer)
            db.session.commit()

            send_writer_credentials(writer.email, password)

            flash('Writer account created successfully! Login credentials have been sent to their email.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating writer account. Please try again.', 'error')
            return render_template('admin/create_writer.html')

    return render_template('admin/create_writer.html')
