from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.exc import SQLAlchemyError

from models import JobNotification, MonitoredURL, SentAlert, User, UserPreference, db
from scrapers import get_scraper
from services.email_service import EmailService
from services.matching_service import MatchingService


class SchedulerService:
    """APScheduler orchestration service for periodic scraping and alert delivery."""

    def __init__(self, app=None) -> None:
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.email_service = EmailService()
        self.matching_service = MatchingService()

    def set_app(self, app) -> None:
        self.app = app

    def schedule_scraping_jobs(self) -> int:
        """Schedule scraping interval jobs for all active monitored URLs."""
        if not self.app:
            raise RuntimeError("SchedulerService requires a Flask app instance.")

        scheduled = 0
        with self.app.app_context():
            monitored_urls = MonitoredURL.query.filter_by(is_active=True).all()
            for monitored_url in monitored_urls:
                frequency = monitored_url.scrape_frequency_hours or 6
                job_id = f"scrape_{monitored_url.id}"
                self.scheduler.add_job(
                    func=self.scrape_and_notify,
                    trigger=IntervalTrigger(hours=frequency),
                    args=[monitored_url.id],
                    id=job_id,
                    replace_existing=True,
                    max_instances=1,
                    coalesce=True,
                )
                scheduled += 1
        return scheduled

    def scrape_and_notify(self, monitored_url_id: int, attempt: int = 1) -> dict[str, Any]:
        """
        Scrape one monitored URL and send alerts for matching users.

        Retries once after 1 hour when scraper execution fails.
        """
        if not self.app:
            self.logger.error("App context missing. Cannot run scraping job.")
            return {"success": False, "notifications_found": 0, "message": "App context missing."}

        try:
            with self.app.app_context():
                monitored_url = MonitoredURL.query.get(monitored_url_id)
                if not monitored_url or not monitored_url.is_active:
                    self.logger.info("Monitored URL %s is missing/inactive. Skipping.", monitored_url_id)
                    return {"success": False, "notifications_found": 0, "message": "Monitored URL missing/inactive."}

                scraper = get_scraper(
                    monitored_url.url,
                    scraper_type=monitored_url.scraper_type,
                    config={
                        "organization_name": monitored_url.website_name or "Not specified",
                    },
                )

                notifications = scraper.scrape(last_scraped_time=monitored_url.last_scraped_at)
                saved_count = 0

                for notification in notifications:
                    job_notification = self._get_or_create_notification(notification)
                    if job_notification is None:
                        continue
                    saved_count += 1
                    self._process_alerts_for_notification(monitored_url, job_notification)

                monitored_url.last_scraped_at = datetime.utcnow()
                db.session.commit()
                self.logger.info(
                    "Scraped %s - Found %s notifications",
                    monitored_url.url,
                    len(notifications),
                )
                return {
                    "success": True,
                    "notifications_found": len(notifications),
                    "new_notifications_saved": saved_count,
                    "message": "Scrape completed.",
                }
        except Exception as e:
            print(f"[ERROR] SCRAPER ERROR for URL ID {monitored_url_id}")
            print(f"[ERROR] Error: {str(e)}")
            import traceback

            traceback.print_exc()
            self.logger.exception("Scraping job failed for monitored_url_id=%s", monitored_url_id)

            try:
                with self.app.app_context():
                    monitored_url = MonitoredURL.query.get(monitored_url_id)
                    if monitored_url:
                        monitored_url.last_scraped_at = datetime.now()
                        db.session.commit()
            except Exception:
                pass

            self._schedule_retry(monitored_url_id, attempt)
            return {
                "success": False,
                "notifications_found": 0,
                "message": "Scrape failed; retry scheduled if eligible.",
            }

    def start_scheduler(self) -> None:
        """Start APScheduler and register all scraping jobs."""
        if self.scheduler.running:
            self.logger.info("Scheduler already running.")
            return

        job_count = self.schedule_scraping_jobs()
        self.scheduler.start()
        self.logger.info("Scheduler started with %s jobs", job_count)

    def stop_scheduler(self) -> None:
        """Gracefully stop APScheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.logger.info("Scheduler stopped.")

    def run_manual_scrape(self, monitored_url_id: int) -> dict[str, Any]:
        """Run immediate scrape for one monitored URL (useful for dashboard testing)."""
        try:
            result = self.scrape_and_notify(monitored_url_id=monitored_url_id, attempt=1)
            return result
        except Exception as exc:
            self.logger.exception("Manual scrape failed for monitored_url_id=%s", monitored_url_id)
            return {"success": False, "notifications_found": 0, "message": str(exc)}

    def _schedule_retry(self, monitored_url_id: int, attempt: int) -> None:
        if attempt >= 2:
            return
        retry_id = f"retry_scrape_{monitored_url_id}"
        self.scheduler.add_job(
            func=self.scrape_and_notify,
            trigger=DateTrigger(run_date=datetime.utcnow() + timedelta(hours=1)),
            args=[monitored_url_id, attempt + 1],
            id=retry_id,
            replace_existing=True,
            max_instances=1,
        )
        self.logger.info(
            "Scheduled retry for monitored_url_id=%s after 1 hour.",
            monitored_url_id,
        )

    def _get_or_create_notification(self, data: dict[str, Any]) -> JobNotification | None:
        title = (data.get("job_title") or "Not specified").strip()
        source_url = (data.get("source_url") or "").strip()
        if not source_url:
            source_url = data.get("pdf_url") or "Not specified"

        existing = JobNotification.query.filter_by(job_title=title, source_url=source_url).first()
        if existing:
            return existing

        try:
            job = JobNotification(
                source_url=source_url,
                job_title=title,
                organization=data.get("organization") or "Not specified",
                notification_date=self._coerce_date(data.get("notification_date")),
                last_date_to_apply=self._coerce_date(data.get("last_date_to_apply")),
                age_limit=data.get("age_limit") or "Not specified",
                qualification_required=data.get("qualification_required") or "Not specified",
                exam_category=data.get("exam_category") or "Not specified",
                full_details=data.get("full_details") or "Not specified",
                pdf_url=data.get("pdf_url"),
                is_active=True,
            )
            db.session.add(job)
            db.session.flush()
            return job
        except SQLAlchemyError:
            db.session.rollback()
            self.logger.exception("Failed to persist JobNotification for title=%s", title)
            return None

    def _process_alerts_for_notification(
        self, monitored_url: MonitoredURL, job_notification: JobNotification
    ) -> None:
        user_rows = MonitoredURL.query.filter_by(url=monitored_url.url, is_active=True).all()
        user_ids = sorted({row.user_id for row in user_rows if row.user_id})

        for user_id in user_ids:
            user = User.query.get(user_id)
            if not user or not user.is_active:
                continue

            preferences = UserPreference.query.filter_by(user_id=user_id).all()
            if not preferences:
                continue

            matches = self.matching_service.is_match(
                job_notification=job_notification,
                user_preferences=preferences,
                user_dob=user.date_of_birth,
                user_qualification=user.highest_qualification,
            )
            if not matches:
                continue

            already_sent = SentAlert.query.filter_by(
                user_id=user_id, job_notification_id=job_notification.id
            ).first()
            if already_sent:
                continue

            send_result = self.email_service.send_job_alert(
                user_email=user.email,
                user_name=user.name,
                job_notification=job_notification,
            )
            status = "sent" if send_result.get("success") else "failed"
            sent_alert = SentAlert(
                user_id=user_id,
                job_notification_id=job_notification.id,
                email_status=status,
            )
            db.session.add(sent_alert)
            db.session.flush()

            if status == "sent":
                self.logger.info(
                    "Alert sent to %s for %s",
                    user.email,
                    job_notification.job_title,
                )
            else:
                self.logger.warning(
                    "Failed alert for %s (%s): %s",
                    user.email,
                    job_notification.job_title,
                    send_result.get("message"),
                )

    def _coerce_date(self, value: Any) -> date | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                pass
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d %b %Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

