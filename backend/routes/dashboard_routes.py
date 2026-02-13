from datetime import date, datetime, time, timedelta

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from models import JobNotification, MonitoredURL, SentAlert, User, UserPreference, db

dashboard_bp = Blueprint("dashboard_routes", __name__)


def _authorize_user(user_id: int):
    """
    Basic MVP authorization check:
    - Accepts requesting user id via `X-User-Id` header or `requesting_user_id` query param.
    - Access allowed only when requesting id matches path user_id.
    """
    incoming = request.headers.get("X-User-Id") or request.args.get("requesting_user_id")
    if incoming is None:
        return False, (jsonify({"error": "Unauthorized: missing requesting user id"}), 401)
    try:
        incoming_id = int(incoming)
    except (TypeError, ValueError):
        return False, (jsonify({"error": "Unauthorized: invalid requesting user id"}), 401)
    if incoming_id != user_id:
        return False, (jsonify({"error": "Forbidden: user mismatch"}), 403)
    return True, None


def _parse_date(value: str | None):
    if not value:
        return None
    formats = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def format_alert_response(alert: SentAlert):
    job = alert.job_notification
    return {
        "id": alert.id,
        "job_title": job.job_title if job else "Not specified",
        "organization": job.organization if job else "Not specified",
        "sent_at": alert.sent_at.isoformat() if alert.sent_at else None,
        "exam_category": job.exam_category if job else "Not specified",
        "last_date_to_apply": (
            job.last_date_to_apply.isoformat() if job and job.last_date_to_apply else None
        ),
        "source_url": job.source_url if job else None,
        "email_status": alert.email_status,
    }


def get_recent_alerts(user_id: int, limit: int = 10):
    alerts = (
        SentAlert.query.filter(
            SentAlert.user_id == user_id,
            SentAlert.email_status != "dismissed",
        )
        .join(JobNotification, SentAlert.job_notification_id == JobNotification.id)
        .order_by(SentAlert.sent_at.desc())
        .limit(limit)
        .all()
    )
    return [format_alert_response(alert) for alert in alerts]


def get_user_stats(user_id: int):
    week_start = datetime.utcnow() - timedelta(days=7)

    total_alerts_received = (
        SentAlert.query.filter(
            SentAlert.user_id == user_id,
            SentAlert.email_status == "sent",
        ).count()
    )
    alerts_this_week = (
        SentAlert.query.filter(
            SentAlert.user_id == user_id,
            SentAlert.email_status == "sent",
            SentAlert.sent_at >= week_start,
        ).count()
    )
    monitored_urls = MonitoredURL.query.filter_by(user_id=user_id, is_active=True).count()
    active_preferences = sorted(
        {
            pref.exam_category
            for pref in UserPreference.query.filter_by(user_id=user_id).all()
            if pref.exam_category
        }
    )

    return {
        "total_alerts_received": total_alerts_received,
        "alerts_this_week": alerts_this_week,
        "monitored_urls": monitored_urls,
        "active_preferences": active_preferences,
    }


@dashboard_bp.get("/<int:user_id>/summary")
def dashboard_summary(user_id: int):
    allowed, error_response = _authorize_user(user_id)
    if not allowed:
        return error_response

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        summary = {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "highest_qualification": user.highest_qualification,
            },
            "stats": get_user_stats(user_id),
            "recent_alerts": get_recent_alerts(user_id, limit=10),
        }
        return jsonify(summary), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database error while loading summary"}), 500
    except Exception:
        current_app.logger.exception("Unexpected error in dashboard summary")
        return jsonify({"error": "Unexpected error while loading summary"}), 500


@dashboard_bp.get("/<int:user_id>/alerts")
def list_alerts(user_id: int):
    allowed, error_response = _authorize_user(user_id)
    if not allowed:
        return error_response

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        exam_category = request.args.get("exam_category", type=str)
        date_from = _parse_date(request.args.get("date_from", type=str))
        date_to = _parse_date(request.args.get("date_to", type=str))

        if page < 1 or per_page < 1:
            return jsonify({"error": "page and per_page must be positive integers"}), 400

        query = (
            SentAlert.query.filter(
                SentAlert.user_id == user_id,
                SentAlert.email_status != "dismissed",
            )
            .join(JobNotification, SentAlert.job_notification_id == JobNotification.id)
            .order_by(SentAlert.sent_at.desc())
        )

        if exam_category:
            query = query.filter(JobNotification.exam_category == exam_category)
        if date_from:
            query = query.filter(
                SentAlert.sent_at >= datetime.combine(date_from, time.min)
            )
        if date_to:
            query = query.filter(
                SentAlert.sent_at <= datetime.combine(date_to, time.max)
            )
        if (request.args.get("date_from") and not date_from) or (
            request.args.get("date_to") and not date_to
        ):
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return (
            jsonify(
                {
                    "alerts": [format_alert_response(alert) for alert in pagination.items],
                    "total": pagination.total,
                    "page": page,
                    "per_page": per_page,
                }
            ),
            200,
        )
    except SQLAlchemyError:
        return jsonify({"error": "Database error while fetching alerts"}), 500
    except Exception:
        current_app.logger.exception("Unexpected error in alert listing")
        return jsonify({"error": "Unexpected error while fetching alerts"}), 500


@dashboard_bp.post("/<int:user_id>/trigger-scrape/<int:url_id>")
def trigger_manual_scrape(user_id: int, url_id: int):
    allowed, error_response = _authorize_user(user_id)
    if not allowed:
        return error_response

    try:
        monitored_url = MonitoredURL.query.filter_by(id=url_id, user_id=user_id).first()
        if not monitored_url:
            return jsonify({"error": "Monitored URL not found for user"}), 404

        scheduler_service = current_app.extensions.get("scheduler_service")
        if not scheduler_service:
            return jsonify({"error": "Scheduler service is not initialized"}), 500

        result = scheduler_service.run_manual_scrape(url_id)
        if result.get("success"):
            return (
                jsonify(
                    {
                        "message": "Scraping started",
                        "notifications_found": result.get("notifications_found", 0),
                    }
                ),
                200,
            )
        return jsonify({"error": result.get("message", "Scraping failed")}), 500
    except Exception:
        current_app.logger.exception("Unexpected error while triggering manual scrape")
        return jsonify({"error": "Unexpected error while triggering scrape"}), 500


@dashboard_bp.get("/<int:user_id>/activity")
def get_activity(user_id: int):
    allowed, error_response = _authorize_user(user_id)
    if not allowed:
        return error_response

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
    except SQLAlchemyError:
        return jsonify({"error": "Database error while fetching activity"}), 500
    except Exception:
        current_app.logger.exception("Unexpected error in activity endpoint")
        return jsonify({"error": "Unexpected error while fetching activity"}), 500


@dashboard_bp.delete("/<int:user_id>/alert/<int:alert_id>")
def dismiss_alert(user_id: int, alert_id: int):
    allowed, error_response = _authorize_user(user_id)
    if not allowed:
        return error_response

    try:
        alert = SentAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if not alert:
            return jsonify({"error": "Alert not found"}), 404

        # MVP archive behavior: mark status as dismissed for UI cleanup.
        alert.email_status = "dismissed"

        db.session.commit()
        return jsonify({"message": "Alert archived"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while archiving alert"}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error while archiving alert")
        return jsonify({"error": "Unexpected error while archiving alert"}), 500
