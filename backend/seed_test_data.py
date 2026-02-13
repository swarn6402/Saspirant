from datetime import datetime, timedelta

from app import app, db
from models import JobNotification, SentAlert, User


def seed_test_notifications():
    """Add sample job notifications to test dashboard display."""
    with app.app_context():
        sample_jobs = [
            {
                "source_url": "https://upsc.gov.in/test1",
                "job_title": "Civil Services Examination (Prelims) 2025",
                "organization": "UPSC",
                "notification_date": datetime.now() - timedelta(days=2),
                "last_date_to_apply": datetime.now() + timedelta(days=25),
                "age_limit": "21-32 years",
                "qualification_required": "Graduate",
                "exam_category": "UPSC",
                "full_details": "UPSC invites applications for Civil Services Examination 2025...",
                "pdf_url": "https://upsc.gov.in/sample.pdf",
            },
            {
                "source_url": "https://ssc.gov.in/test1",
                "job_title": "SSC CGL 2025 - Tier 1 Examination",
                "organization": "SSC",
                "notification_date": datetime.now() - timedelta(days=5),
                "last_date_to_apply": datetime.now() + timedelta(days=15),
                "age_limit": "18-27 years",
                "qualification_required": "Graduate",
                "exam_category": "SSC",
                "full_details": "Staff Selection Commission Combined Graduate Level Exam...",
                "pdf_url": "https://ssc.gov.in/sample.pdf",
            },
            {
                "source_url": "https://upsc.gov.in/test2",
                "job_title": "National Defence Academy (NDA) Examination II/2025",
                "organization": "UPSC",
                "notification_date": datetime.now() - timedelta(days=1),
                "last_date_to_apply": datetime.now() + timedelta(days=30),
                "age_limit": "16.5-19.5 years",
                "qualification_required": "12th",
                "exam_category": "UPSC",
                "full_details": "UPSC NDA & NA Examination notification...",
                "pdf_url": "https://upsc.gov.in/nda.pdf",
            },
            {
                "source_url": "https://upsc.gov.in/test3",
                "job_title": "Combined Defence Services (CDS) Exam I/2025",
                "organization": "UPSC",
                "notification_date": datetime.now(),
                "last_date_to_apply": datetime.now() + timedelta(days=5),
                "age_limit": "19-25 years",
                "qualification_required": "Graduate",
                "exam_category": "UPSC",
                "full_details": "Combined Defence Services Examination notification...",
                "pdf_url": "https://upsc.gov.in/cds.pdf",
            },
        ]

        for job_data in sample_jobs:
            existing = JobNotification.query.filter_by(job_title=job_data["job_title"]).first()
            if not existing:
                job = JobNotification(**job_data)
                db.session.add(job)
                print(f"Added: {job_data['job_title']}")

        db.session.commit()
        print("\n[OK] Test notifications seeded successfully!")

        test_user = User.query.first()
        if test_user:
            print(f"\nCreating sample alerts for user: {test_user.name}")

            notifications = JobNotification.query.limit(2).all()
            for notif in notifications:
                alert_exists = SentAlert.query.filter_by(
                    user_id=test_user.id, job_notification_id=notif.id
                ).first()

                if not alert_exists:
                    sent_alert = SentAlert(
                        user_id=test_user.id,
                        job_notification_id=notif.id,
                        email_status="sent",
                        sent_at=datetime.now() - timedelta(hours=2),
                    )
                    db.session.add(sent_alert)
                    print(f"  - Alert created for: {notif.job_title}")

            db.session.commit()
            print("\n[OK] Sample alerts created!")


if __name__ == "__main__":
    seed_test_notifications()
