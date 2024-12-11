from app import create_app, db
from app.models import User, Order, File

def test_models():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Test creating a user
        admin = User(name='Test Admin', email='admin@test.com', role='admin')
        admin.set_password('test123')
        db.session.add(admin)
        db.session.commit()
        
        # Verify user was created
        test_user = User.query.filter_by(email='admin@test.com').first()
        print('Database tables created successfully')
        print('Test user created:', test_user is not None)
        print('User role:', test_user.role)

if __name__ == '__main__':
    test_models()
