from app import create_app, db
from app.models.user import User

def update_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        if admin:
            admin.confirmed = True
            db.session.commit()
            print("Admin user confirmed successfully!")
        else:
            print("Admin user not found!")

if __name__ == '__main__':
    update_admin()
