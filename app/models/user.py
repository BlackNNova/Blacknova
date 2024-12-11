from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'writer'
    confirmation_token_used = db.Column(db.Boolean, default=False)  # Track token usage
    confirmed = db.Column(db.Boolean, default=False)  # Track if user has confirmed their account

    # Relationships
    orders_assigned = db.relationship('Order', backref='writer', lazy=True,
                                    foreign_keys='Order.writer_id')

    @property
    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def mark_token_as_used(self):
        self.confirmation_token_used = True
        db.session.commit()
