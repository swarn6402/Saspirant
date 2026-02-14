import sys
from datetime import datetime, timedelta

from app import app
from models import JobNotification, SentAlert, User, UserPreference, db


def seed_fresh_notifications(user_id):
    """Add fresh notifications for a specific user."""
    with app.app_context():
        user = User.query.get(int(user_id))
        if not user:
            print(f"User with ID {user_id} not found!")
            return

        print(f"Adding fresh notifications for user: {user.name} (ID: {user.id})")

        preferences = UserPreference.query.filter_by(user_id=user.id).all()
        user_categories = [p.exam_category for p in preferences]
        print(f"User preferences: {user_categories}")

        now = datetime.now()
        fresh_jobs = []

        if "UPSC" in user_categories:
            fresh_jobs.extend(
                [
                    {
                        "source_url": f"https://upsc.gov.in/fresh-{now.strftime('%Y%m%d')}-1",
                        "job_title": "UPSC Combined Medical Services Examination 2026",
                        "organization": "UPSC",
                        "notification_date": (now - timedelta(hours=2)).date(),
                        "last_date_to_apply": (now + timedelta(days=28)).date(),
                        "age_limit": "21-32 years",
                        "qualification_required": "Graduate",
                        "exam_category": "UPSC",
                        "full_details": "UPSC invites applications for Combined Medical Services Examination 2026. Apply online before deadline.",
                        "pdf_url": "https://upsc.gov.in/cms2026.pdf",
                    },
                    {
                        "source_url": f"https://upsc.gov.in/fresh-{now.strftime('%Y%m%d')}-2",
                        "job_title": "Engineering Services Examination (Prelims) 2026",
                        "organization": "UPSC",
                        "notification_date": (now - timedelta(hours=5)).date(),
                        "last_date_to_apply": (now + timedelta(days=35)).date(),
                        "age_limit": "21-30 years",
                        "qualification_required": "Engineering Graduate",
                        "exam_category": "UPSC",
                        "full_details": "UPSC Engineering Services Preliminary Examination 2026 notification.",
                        "pdf_url": "https://upsc.gov.in/ese2026.pdf",
                    },
                ]
            )

        if "University" in user_categories:
            fresh_jobs.extend(
                [
                    {
                        "source_url": f"https://www.makautexam.net/fresh-{now.strftime('%Y%m%d')}-1",
                        "job_title": "MAKAUT B.Tech Semester 6 Examination Form Fill-Up Notice",
                        "organization": "MAKAUT",
                        "notification_date": (now - timedelta(hours=1)).date(),
                        "last_date_to_apply": (now + timedelta(days=10)).date(),
                        "age_limit": "18-30 years",
                        "qualification_required": "Undergraduate",
                        "exam_category": "University",
                        "full_details": "Notice for B.Tech 6th semester examination form fill-up for 2025-26.",
                        "pdf_url": "https://makaut.edu.in/notice2026.pdf",
                    },
                    {
                        "source_url": f"https://du.ac.in/fresh-{now.strftime('%Y%m%d')}-1",
                        "job_title": "Delhi University M.A Admission 2026 - Registration Open",
                        "organization": "Delhi University",
                        "notification_date": (now - timedelta(minutes=30)).date(),
                        "last_date_to_apply": (now + timedelta(days=20)).date(),
                        "age_limit": "No limit",
                        "qualification_required": "Graduate",
                        "exam_category": "University",
                        "full_details": "Delhi University M.A admission process for academic year 2026-27.",
                        "pdf_url": "https://du.ac.in/ma2026.pdf",
                    },
                ]
            )

        if "Medical" in user_categories:
            fresh_jobs.extend(
                [
                    {
                        "source_url": f"https://nbe.edu.in/fresh-{now.strftime('%Y%m%d')}-1",
                        "job_title": "NEET PG 2026 - Registration Started",
                        "organization": "NBE",
                        "notification_date": (now - timedelta(hours=3)).date(),
                        "last_date_to_apply": (now + timedelta(days=15)).date(),
                        "age_limit": "No upper limit",
                        "qualification_required": "MBBS",
                        "exam_category": "Medical",
                        "full_details": "National Eligibility cum Entrance Test for PG medical courses 2026.",
                        "pdf_url": "https://nbe.edu.in/neetpg2026.pdf",
                    }
                ]
            )

        notifications_added = 0
        for job_data in fresh_jobs:
            existing = JobNotification.query.filter_by(source_url=job_data["source_url"]).first()
            if existing:
                continue

            job = JobNotification(**job_data)
            db.session.add(job)
            db.session.flush()

            alert = SentAlert(
                user_id=user.id,
                job_notification_id=job.id,
                email_status="sent",
                sent_at=datetime.now(),
            )
            db.session.add(alert)

            notifications_added += 1
            print(f"  Added: {job_data['job_title']}")

        db.session.commit()

        print(f"\n[OK] Added {notifications_added} fresh notifications.")
        print("[OK] Refresh your dashboard to see them.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_fresh_notifications.py <user_id>")
        print("Example: python seed_fresh_notifications.py 15")
        sys.exit(1)

    seed_fresh_notifications(sys.argv[1])
