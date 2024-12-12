from app import create_app, db
from app.models.user import User

def check_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        print(f'Admin exists: {admin is not None}')
        if admin:
            print(f'Admin name: {admin.name}')
            print(f'Admin password hash: {admin.password_hash}')
            print(f'Admin confirmed: {admin.confirmed}')

if __name__ == '__main__':
    check_admin()
