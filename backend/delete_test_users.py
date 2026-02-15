from app import app, db
from models import User, UserPreference, MonitoredURL, SentAlert, JobNotification

def delete_all_users():
    with app.app_context():
        try:
            # Delete in correct order (foreign keys)
            print("Deleting sent alerts...")
            SentAlert.query.delete()
            
            print("Deleting user preferences...")
            UserPreference.query.delete()
            
            print("Deleting monitored URLs...")
            MonitoredURL.query.delete()
            
            print("Deleting users...")
            user_count = User.query.count()
            User.query.delete()
            
            db.session.commit()
            
            print(f"✓ Successfully deleted {user_count} users and all related data")
            print("You can now register with fresh accounts that have passwords!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error: {e}")

if __name__ == '__main__':
    confirmation = input("⚠️  This will DELETE ALL USERS and their data. Type 'DELETE' to confirm: ")
    if confirmation == "DELETE":
        delete_all_users()
    else:
        print("Cancelled.")
