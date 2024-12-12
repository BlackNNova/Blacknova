from app import db
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    pages = db.Column(db.Integer)
    price = db.Column(db.Float)
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='unclaimed')  # unclaimed, in_progress, completed, revision, invoice, paid
    summary = db.Column(db.Text)
    subtle_points = db.Column(db.Text)

    # Foreign Keys
    writer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    files = db.relationship('File', backref='order', lazy=True, cascade='all, delete-orphan')
