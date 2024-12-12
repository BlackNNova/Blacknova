import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
from datetime import datetime
from sqlalchemy import text

def upgrade():
    app = create_app()
    with app.app_context():
        # Add updated_at column
        db.session.execute(text('ALTER TABLE "order" ADD COLUMN updated_at DATETIME'))
        # Update existing records to have the same timestamp as created_at
        db.session.execute(text('UPDATE "order" SET updated_at = created_at'))
        db.session.commit()

if __name__ == '__main__':
    upgrade()
