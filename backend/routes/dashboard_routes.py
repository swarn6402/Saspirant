from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import desc, func

from models import db, JobNotification, MonitoredURL, SentAlert, User, UserPreference

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/<int:user_id>/summary", methods=["GET"])
def get_dashboard_summary(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        total_alerts = SentAlert.query.filter_by(user_id=user_id).count()

        week_ago = datetime.now() - timedelta(days=7)
        alerts_this_week = SentAlert.query.filter(
            SentAlert.user_id == user_id,
            SentAlert.sent_at >= week_ago,
        ).count()

        monitored_urls = MonitoredURL.query.filter_by(user_id=user_id, is_active=True).count()

        preferences = UserPreference.query.filter_by(user_id=user_id).all()
        active_preferences = [p.exam_category for p in preferences]

        recent_alerts_query = (
            db.session.query(SentAlert, JobNotification)
            .join(JobNotification, SentAlert.job_notification_id == JobNotification.id)
            .filter(SentAlert.user_id == user_id)
            .order_by(desc(SentAlert.sent_at))
            .limit(10)
            .all()
        )

        recent_alerts = []
        for alert, job in recent_alerts_query:
            recent_alerts.append(
                {
                    "id": alert.id,
                    "job_title": job.job_title,
                    "organization": job.organization,
                    "sent_at": alert.sent_at.isoformat() if alert.sent_at else None,
                    "exam_category": job.exam_category,
                    "last_date_to_apply": (
                        job.last_date_to_apply.isoformat() if job.last_date_to_apply else None
                    ),
                    "source_url": job.source_url,
                }
            )

        return (
            jsonify(
                {
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "qualification": user.highest_qualification,
                    },
                    "stats": {
                        "total_alerts_received": total_alerts,
                        "alerts_this_week": alerts_this_week,
                        "monitored_urls": monitored_urls,
                        "active_preferences": active_preferences,
                    },
                    "recent_alerts": recent_alerts,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.exception("Error in dashboard summary for user_id=%s", user_id)
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/dashboard/<int:user_id>/alerts", methods=["GET"])
def get_user_alerts(user_id):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        query = (
            db.session.query(SentAlert, JobNotification)
            .join(JobNotification, SentAlert.job_notification_id == JobNotification.id)
            .filter(SentAlert.user_id == user_id)
        )

        exam_category = request.args.get("exam_category")
        if exam_category:
            query = query.filter(JobNotification.exam_category == exam_category)

        query = query.order_by(desc(SentAlert.sent_at))

        total = query.count()
        alerts_query = query.offset((page - 1) * per_page).limit(per_page).all()

        alerts = []
        for alert, job in alerts_query:
            alerts.append(
                {
                    "id": alert.id,
                    "job_title": job.job_title,
                    "organization": job.organization,
                    "sent_at": alert.sent_at.isoformat() if alert.sent_at else None,
                    "exam_category": job.exam_category,
                    "last_date_to_apply": (
                        job.last_date_to_apply.isoformat() if job.last_date_to_apply else None
                    ),
                    "source_url": job.source_url,
                    "age_limit": job.age_limit,
                    "qualification_required": job.qualification_required,
                    "email_status": alert.email_status,
                }
            )

        return (
            jsonify(
                {
                    "alerts": alerts,
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.exception("Error in dashboard alerts for user_id=%s", user_id)
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/dashboard/<int:user_id>/trigger-scrape/<int:url_id>", methods=["POST"])
def trigger_manual_scrape(user_id, url_id):
    try:
        from scrapers import get_scraper
        from services.matching_service import MatchingService
        from services.email_service import EmailService

        print("\n" + "=" * 60)
        print("MANUAL SCRAPE TRIGGERED")
        print(f"User ID: {user_id}, URL ID: {url_id}")
        print("=" * 60)

        monitored_url = MonitoredURL.query.get(url_id)
        if not monitored_url or monitored_url.user_id != user_id:
            print("ERROR: URL not found or does not belong to user")
            return jsonify({"error": "URL not found"}), 404

        print(f"Scraping URL: {monitored_url.url}")
        print(f"Website: {monitored_url.website_name}")

        scraper = get_scraper(monitored_url.url, monitored_url.scraper_type)
        print(f"Using scraper: {scraper.__class__.__name__}")

        print("\nStarting scrape...")
        notifications = scraper.scrape(last_scraped_time=monitored_url.last_scraped_at)
        print(f"[OK] Scrape completed: Found {len(notifications)} notifications")

        for i, notif in enumerate(notifications, 1):
            print(f"\n--- Notification {i} ---")
            print(f"Title: {notif.get('job_title', 'N/A')}")
            print(f"Category: {notif.get('exam_category', 'N/A')}")
            print(f"Source: {notif.get('source_url', 'N/A')}")

        user = User.query.get(user_id)
        preferences = UserPreference.query.filter_by(user_id=user_id).all()

        print(f"\nUser: {user.name}")
        print(f"User DOB: {user.date_of_birth}")
        print(f"User Qualification: {user.highest_qualification}")
        print(f"User Preferences: {[p.exam_category for p in preferences]}")

        def _coerce_date_value(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value.date()
            if hasattr(value, "isoformat") and not isinstance(value, str):
                return value
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value).date()
                except ValueError:
                    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d %b %Y"):
                        try:
                            return datetime.strptime(value, fmt).date()
                        except ValueError:
                            continue
            return None

        new_notifications = 0
        matched_notifications = 0
        alerts_sent = 0

        for notif_data in notifications:
            existing = JobNotification.query.filter_by(
                job_title=notif_data.get("job_title"),
                source_url=notif_data.get("source_url"),
            ).first()

            if existing:
                print(f"\n[X] Skipping '{notif_data.get('job_title')}' - already in database")
                job_notif = existing
            else:
                print(f"\n[OK] New notification: '{notif_data.get('job_title')}'")
                normalized = {
                    "source_url": notif_data.get("source_url"),
                    "job_title": notif_data.get("job_title") or "Not specified",
                    "organization": notif_data.get("organization"),
                    "notification_date": _coerce_date_value(notif_data.get("notification_date")),
                    "last_date_to_apply": _coerce_date_value(notif_data.get("last_date_to_apply")),
                    "age_limit": notif_data.get("age_limit"),
                    "qualification_required": notif_data.get("qualification_required"),
                    "exam_category": notif_data.get("exam_category"),
                    "full_details": notif_data.get("full_details"),
                    "pdf_url": notif_data.get("pdf_url"),
                }
                job_notif = JobNotification(**normalized)
                db.session.add(job_notif)
                db.session.flush()
                new_notifications += 1

            matcher = MatchingService()
            is_match = matcher.is_match(
                job_notif,
                preferences,
                user.date_of_birth,
                user_qualification=user.highest_qualification,
            )

            print(f"  Match check result: {is_match}")

            if is_match:
                matched_notifications += 1
                print("  [OK] Matches user preferences")

                alert_exists = SentAlert.query.filter_by(
                    user_id=user_id,
                    job_notification_id=job_notif.id,
                ).first()

                if alert_exists:
                    print("  [X] Alert already sent to user")
                else:
                    print("  -> Sending email alert...")
                    email_service = EmailService()
                    result = email_service.send_job_alert(user.email, user.name, job_notif)
                    print(f"  Email result: {result}")

                    sent_alert = SentAlert(
                        user_id=user_id,
                        job_notification_id=job_notif.id,
                        email_status="sent" if result.get("success") else "failed",
                    )
                    db.session.add(sent_alert)
                    alerts_sent += 1
                    print("  [OK] Alert recorded in database")
            else:
                print("  [X] Does NOT match user preferences")

        db.session.commit()

        monitored_url.last_scraped_at = datetime.now()
        db.session.commit()

        print("\n" + "=" * 60)
        print("SCRAPE SUMMARY")
        print(f"Total found: {len(notifications)}")
        print(f"New in DB: {new_notifications}")
        print(f"Matched preferences: {matched_notifications}")
        print(f"Alerts sent: {alerts_sent}")
        print("=" * 60 + "\n")

        return (
            jsonify(
                {
                    "message": "Scrape completed",
                    "notifications_found": len(notifications),
                    "new_notifications": new_notifications,
                    "matched_notifications": matched_notifications,
                    "alerts_sent": alerts_sent,
                }
            ),
            200,
        )
    except Exception as e:
        print(f"\n[ERROR] SCRAPE ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        current_app.logger.exception("Error in trigger manual scrape for user_id=%s, url_id=%s", user_id, url_id)
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/dashboard/<int:user_id>/activity", methods=["GET"])
def get_activity(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        last_scrapes = (
            MonitoredURL.query.filter(
                MonitoredURL.user_id == user_id,
                MonitoredURL.last_scraped_at.isnot(None),
            )
            .order_by(MonitoredURL.last_scraped_at.desc())
            .limit(5)
            .all()
        )
        scrape_runs = [
            {
                "url_id": row.id,
                "url": row.url,
                "website_name": row.website_name,
                "scraped_at": row.last_scraped_at.isoformat() if row.last_scraped_at else None,
                "result": "completed",
            }
            for row in last_scrapes
        ]

        email_rows = (
            SentAlert.query.filter(SentAlert.user_id == user_id)
            .join(JobNotification, SentAlert.job_notification_id == JobNotification.id)
            .order_by(SentAlert.sent_at.desc())
            .limit(5)
            .all()
        )
        emails_sent = [
            {
                "alert_id": row.id,
                "job_title": row.job_notification.job_title if row.job_notification else "Not specified",
                "email_status": row.email_status,
                "sent_at": row.sent_at.isoformat() if row.sent_at else None,
            }
            for row in email_rows
        ]

        error_rows = (
            SentAlert.query.filter(
                SentAlert.user_id == user_id,
                SentAlert.email_status.in_(["failed", "bounced"]),
            )
            .order_by(SentAlert.sent_at.desc())
            .limit(5)
            .all()
        )
        errors_warnings = [
            {
                "type": "email_error",
                "alert_id": row.id,
                "status": row.email_status,
                "timestamp": row.sent_at.isoformat() if row.sent_at else None,
                "message": "Email delivery failed or bounced.",
            }
            for row in error_rows
        ]

        # Use `func.count` to keep sqlalchemy func import meaningful and ready for future KPI expansion.
        _ = (
            db.session.query(func.count(SentAlert.id))
            .filter(SentAlert.user_id == user_id)
            .scalar()
        )

        return (
            jsonify(
                {
                    "scraping_runs": scrape_runs,
                    "emails_sent": emails_sent,
                    "errors_warnings": errors_warnings,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.exception("Error in dashboard activity for user_id=%s", user_id)
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/dashboard/<int:user_id>/alert/<int:alert_id>", methods=["DELETE"])
def dismiss_alert(user_id, alert_id):
    try:
        alert = SentAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if not alert:
            return jsonify({"error": "Alert not found"}), 404

        alert.email_status = "dismissed"
        db.session.commit()
        return jsonify({"message": "Alert archived"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error archiving alert_id=%s for user_id=%s", alert_id, user_id)
        return jsonify({"error": str(e)}), 500
