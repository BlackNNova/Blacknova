from app import create_app, db
from app.models.user import User
from app.models.order import Order
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

app = create_app()

def create_test_data():
    with app.app_context():
        # Get existing admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            print("Error: Admin user not found. Please run init_db.py first.")
            return

        # Create test writers
        writers = []
        for i in range(1, 4):
            email = f'writer{i}@test.com'
            existing_writer = User.query.filter_by(email=email).first()
            if existing_writer:
                writers.append(existing_writer)
            else:
                writer = User(
                    name=f'Writer {i}',
                    email=email,
                    role='writer',
                    password_hash=generate_password_hash(f'writer{i}123'),
                    phone=f'123-456-789{i}',
                    confirmed=True
                )
                db.session.add(writer)
                writers.append(writer)
        db.session.commit()

        # Create test orders in different states
        orders = []

        # Unclaimed orders
        for i in range(1, 3):
            orders.append(Order(
                title=f'Unclaimed Order {i}',
                description=f'Test unclaimed order {i}',
                deadline=datetime.now() + timedelta(days=i),
                price=50.0 + i * 10,
                writer_id=writers[i-1].id,
                status='unclaimed'
            ))

        # Orders in progress
        for i in range(1, 3):
            orders.append(Order(
                title=f'In Progress Order {i}',
                description=f'Test in progress order {i}',
                deadline=datetime.now() + timedelta(days=i+2),
                price=70.0 + i * 10,
                writer_id=writers[i-1].id,
                status='in_progress'
            ))

        # Completed orders
        for i in range(1, 3):
            orders.append(Order(
                title=f'Completed Order {i}',
                description=f'Test completed order {i}',
                deadline=datetime.now() + timedelta(days=i+4),
                price=90.0 + i * 10,
                writer_id=writers[i-1].id,
                status='completed'
            ))

        # Orders in revision
        for i in range(1, 3):
            orders.append(Order(
                title=f'Revision Order {i}',
                description=f'Test revision order {i}',
                deadline=datetime.now() + timedelta(days=i+6),
                price=110.0 + i * 10,
                writer_id=writers[i-1].id,
                status='revision'
            ))

        # Invoice/Unpaid orders
        for i in range(1, 3):
            orders.append(Order(
                title=f'Invoice Order {i}',
                description=f'Test invoice order {i}',
                deadline=datetime.now() - timedelta(days=i),
                price=130.0 + i * 10,
                writer_id=writers[i-1].id,
                status='invoice'
            ))

        # Paid orders
        for i in range(1, 3):
            orders.append(Order(
                title=f'Paid Order {i}',
                description=f'Test paid order {i}',
                deadline=datetime.now() - timedelta(days=i+2),
                price=150.0 + i * 10,
                writer_id=writers[i-1].id,
                status='paid'
            ))

        # Add orders to database
        for order in orders:
            db.session.add(order)
        db.session.commit()

        print("Test data created successfully!")

if __name__ == '__main__':
    create_test_data()
