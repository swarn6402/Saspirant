from app import app, db
from sqlalchemy import text, inspect

def migrate():
    with app.app_context():
        # Get inspector to check if column exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'password_hash' in columns:
            print("✓ password_hash column already exists")
        else:
            print("Adding password_hash column...")
            try:
                # Use raw connection to avoid SQLAlchemy transaction issues
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(256)"))
                    conn.commit()
                print("✓ password_hash column added successfully")
            except Exception as e:
                print(f"✗ Error adding column: {e}")

if __name__ == '__main__':
    migrate()
