import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_confirmation_token(email):
    """Generate a non-expiring confirmation token."""
    payload = {
        'email': email,
        'iat': datetime.utcnow(),
        'type': 'confirmation'
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_confirmation_token(token):
    """Verify the confirmation token."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        if payload.get('type') != 'confirmation':
            return None
        return payload.get('email')
    except jwt.InvalidTokenError:
        return None
