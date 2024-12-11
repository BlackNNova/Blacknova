from app import create_app, db
from app.models.user import User

def verify_security_features():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='admin@test.com').first()
        print('\nUser Details:')
        print(f'Email: {user.email}')
        print(f'Name: {user.name}')
        print(f'Password Hash: {user.password_hash[:50]}...')  # Show first 50 chars
        print(f'Token Used: {user.confirmation_token_used}')
        
        # Verify password hashing works
        print('\nPassword Verification:')
        print(f'Correct password validates: {user.check_password("SecurePass123!")}')
        print(f'Wrong password fails: {user.check_password("WrongPassword123!")}')

if __name__ == '__main__':
    verify_security_features()
