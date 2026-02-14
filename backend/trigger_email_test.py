from datetime import date, datetime, timedelta

from app import app
from models import JobNotification, SentAlert, User, UserPreference, db
from services.email_service import EmailService
from services.matching_service import MatchingService


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def trigger_test_email():
    """Add a fresh notification and send email alert."""
    with app.app_context():
        email = input("Enter your email address: ").strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"User with email {email} not found!")
            return

        print(f"Found user: {user.name} (ID: {user.id})")

        preferences = UserPreference.query.filter_by(user_id=user.id).all()
        categories = [p.exam_category for p in preferences]
        print(f"User preferences: {categories}")

        if not categories:
            print("User has no preferences set!")
            return

        category = categories[0]
        now = datetime.now()
        user_age = calculate_age(user.date_of_birth)

        test_notification = JobNotification(
            source_url=f"https://test-email-{now.strftime('%Y%m%d-%H%M%S')}.com",
            job_title=f"TEST EMAIL ALERT - {category} Examination 2026",
            organization="TEST ORG",
            notification_date=now.date(),
            last_date_to_apply=(now + timedelta(days=30)).date(),
            age_limit=f"{max(18, user_age - 5)}-{user_age + 10} years",
            qualification_required=user.highest_qualification,
            exam_category=category,
            full_details=f"This is a test notification to verify email alerts are working for {user.name}.",
            pdf_url="https://test.com/notification.pdf",
        )

        db.session.add(test_notification)
        db.session.flush()

        print("Created test notification:")
        print(f"  - Title: {test_notification.job_title}")
        print(f"  - Category: {category}")
        print(f"  - Age limit: {test_notification.age_limit} (User is {user_age} years old)")
        print(f"  - Qualification: {user.highest_qualification}")

        matcher = MatchingService()
        is_match = matcher.is_match(test_notification, preferences, user.date_of_birth)
        print(f"Match check: {is_match}")

        if not is_match:
            print("Notification doesn't match user criteria!")
            db.session.rollback()
            return

        print(f"Sending email to {user.email}...")
        email_service = EmailService()
        result = email_service.send_job_alert(
            user.email,
            user.name,
            test_notification,
        )

        print(f"Email result: {result}")

        if result.get("success"):
            alert = SentAlert(
                user_id=user.id,
                job_notification_id=test_notification.id,
                email_status="sent",
            )
            db.session.add(alert)
            db.session.commit()
            print(f"\nSUCCESS! Email sent to {user.email}")
            print("Check your inbox!")
        else:
            print(f"\nEmail failed: {result.get('message')}")
            db.session.rollback()


if __name__ == "__main__":
    trigger_test_email()
