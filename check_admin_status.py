from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # First, delete any existing admin user to start fresh
    admin = User.query.filter_by(email='admin@test.com').first()
    if admin:
        db.session.delete(admin)
        db.session.commit()
        print("Deleted existing admin user")

    # Create new admin user with proper password hashing
    print("Creating new admin user...")
    admin = User(
        email='admin@test.com',
        role='admin',
        name='Admin User',
        confirmed=True
    )
    admin.set_password('admin123')  # Use the model's method to properly hash password
    db.session.add(admin)
    db.session.commit()
    print("Created new admin user with hashed password")
