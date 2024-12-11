from app import create_app, db
from app.models.user import User

def check_db():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        if admin:
            print(f"Admin user found:")
            print(f"Name: {admin.name}")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            print(f"Password hash exists: {bool(admin.password_hash)}")
            print(f"Password hash: {admin.password_hash}")
            print(f"Confirmed: {admin.confirmed}")
        else:
            print("No admin user found in database")

if __name__ == '__main__':
    check_db()
