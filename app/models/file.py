from app import db
from datetime import datetime

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # For file type validation
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_submission = db.Column(db.Boolean, default=False)  # False for task files, True for submitted work

    # Foreign Key
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
