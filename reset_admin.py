from app import create_app, db
from app.models.user import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            admin.set_password('adminpass123')
            admin.confirmed = True
            db.session.commit()
            print(f"Admin password reset successfully for {admin.email}")
        else:
            print("Admin user not found")

if __name__ == '__main__':
    reset_admin_password()
