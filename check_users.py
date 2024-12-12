from app import create_app, db
from app.models.user import User

def check_users():
    app = create_app()
    with app.app_context():
        print("\nChecking all users:")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Confirmed: {user.confirmed}")

        print("\nChecking admin specifically:")
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print(f"Admin found:")
            print(f"ID: {admin.id}")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            print(f"Confirmed: {admin.confirmed}")
            print(f"Has password hash: {'Yes' if admin.password_hash else 'No'}")
        else:
            print("Admin user not found")

if __name__ == '__main__':
    check_users()
