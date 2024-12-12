import sqlite3
import os

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'instance', 'writers_management.db')

def upgrade():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE "order" ADD COLUMN summary TEXT')
        cursor.execute('ALTER TABLE "order" ADD COLUMN subtle_points TEXT')
        conn.commit()
        print("Successfully added summary and subtle_points columns")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def downgrade():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TEMPORARY TABLE order_backup(
                id, title, description, pages, price, deadline, created_at,
                updated_at, status, writer_id
            )
        ''')

        cursor.execute('''
            INSERT INTO order_backup
            SELECT id, title, description, pages, price, deadline, created_at,
                   updated_at, status, writer_id
            FROM "order"
        ''')

        cursor.execute('DROP TABLE "order"')

        cursor.execute('''
            CREATE TABLE "order" (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                pages INTEGER,
                price FLOAT,
                deadline DATETIME NOT NULL,
                created_at DATETIME,
                updated_at DATETIME,
                status VARCHAR(20) NOT NULL,
                writer_id INTEGER REFERENCES user(id)
            )
        ''')

        cursor.execute('''
            INSERT INTO "order"
            SELECT * FROM order_backup
        ''')

        cursor.execute('DROP TABLE order_backup')

        conn.commit()
        print("Successfully removed summary and subtle_points columns")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade()
