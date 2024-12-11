from app import create_app, db
from app.models.user import User

def init_db():
    app = create_app()
    with app.app_context():
        db.drop_all()  # Reset database
        db.create_all()  # Create fresh tables

        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@test.com',
            phone='123-456-7890',
            role='admin',
            confirmation_token_used=True,
            confirmed=True
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        print("Database initialized successfully with admin user!")

if __name__ == '__main__':
    init_db()
