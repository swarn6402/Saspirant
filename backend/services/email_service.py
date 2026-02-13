import logging
import os
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jinja2 import Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailService:
    """Send email alerts and notifications using SendGrid."""

    DAILY_LIMIT = 100
    DIGEST_THRESHOLD = 5

    # In-memory counters for MVP usage.
    _daily_counts: dict[str, int] = defaultdict(int)
    _daily_user_alerts: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    _daily_digest_sent: dict[str, dict[str, bool]] = defaultdict(lambda: defaultdict(bool))

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_key = os.getenv("SENDGRID_API_KEY", "").strip()
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "").strip()
        self.dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:5000/dashboard")
        self.unsubscribe_url = os.getenv("UNSUBSCRIBE_URL", "http://localhost:5000/unsubscribe")
        self.templates_dir = Path(__file__).resolve().parent.parent / "templates" / "email"

        if not self.api_key:
            self.logger.warning("SENDGRID_API_KEY is not configured.")
        if not self.from_email:
            self.logger.warning("SENDGRID_FROM_EMAIL is not configured.")

    def send_job_alert(self, user_email: str, user_name: str, job_notification: Any) -> dict[str, Any]:
        """
        Send a single job alert email, with digest grouping if alerts exceed threshold.
        """
        if not self._can_send():
            return {"success": False, "message": "Daily SendGrid limit reached."}

        if not user_email:
            return {"success": False, "message": "Missing user email."}

        today = date.today().isoformat()
        job_payload = self._normalize_job_payload(job_notification)
        self._daily_user_alerts[today][user_email].append(job_payload)
        user_alert_count = len(self._daily_user_alerts[today][user_email])

        if user_alert_count > self.DIGEST_THRESHOLD:
            if self._daily_digest_sent[today][user_email]:
                return {
                    "success": True,
                    "message": "Alert queued for daily digest (digest already sent today).",
                }

            digest_subject = f"Daily Job Digest: {user_alert_count} new alerts"
            digest_html = self._render_digest_html(user_name, self._daily_user_alerts[today][user_email])
            send_result = self._send_email(user_email, digest_subject, digest_html)
            if send_result["success"]:
                self._daily_digest_sent[today][user_email] = True
            return send_result

        last_date_color = self._deadline_color(job_payload.get("last_date_to_apply"))
        subject = f"🎯 New Job Alert: {job_payload.get('job_title', 'Opportunity')}"
        html_body = self._render_template(
            "job_alert_template.html",
            {
                "user_name": user_name or "User",
                "job_title": job_payload.get("job_title", "Not specified"),
                "organization": job_payload.get("organization", "Not specified"),
                "last_date_to_apply": job_payload.get("last_date_to_apply", "Not specified"),
                "last_date_color": last_date_color,
                "age_limit": job_payload.get("age_limit", "Not specified"),
                "qualification_required": job_payload.get("qualification_required", "Not specified"),
                "source_url": job_payload.get("source_url", "#"),
                "dashboard_url": self.dashboard_url,
                "unsubscribe_url": self.unsubscribe_url,
            },
        )
        return self._send_email(user_email, subject, html_body)

    def send_welcome_email(self, user_email: str, user_name: str) -> dict[str, Any]:
        """Send a welcome email to a newly registered user."""
        if not self._can_send():
            return {"success": False, "message": "Daily SendGrid limit reached."}

        subject = "Welcome to Saspirant"
        html_body = self._render_template(
            "welcome_template.html",
            {
                "user_name": user_name or "User",
                "dashboard_url": self.dashboard_url,
            },
        )
        return self._send_email(user_email, subject, html_body)

    def send_test_email(self, user_email: str) -> dict[str, Any]:
        """Send a test email to verify SendGrid integration."""
        if not self._can_send():
            return {"success": False, "message": "Daily SendGrid limit reached."}

        subject = "Saspirant SendGrid Test Email"
        html_body = """
        <html>
          <body style="font-family: Arial, sans-serif; background:#f5f8fc; padding:16px;">
            <div style="max-width:600px;margin:auto;background:#fff;border:1px solid #dbe7f3;padding:20px;border-radius:8px;">
              <h2 style="color:#0f4c81;">SendGrid test successful</h2>
              <p>If you received this message, your SendGrid integration is working.</p>
            </div>
          </body>
        </html>
        """
        return self._send_email(user_email, subject, html_body)

    def _send_email(self, to_email: str, subject: str, html_content: str) -> dict[str, Any]:
        try:
            if not self.api_key or not self.from_email:
                return {
                    "success": False,
                    "message": "Missing SENDGRID_API_KEY or SENDGRID_FROM_EMAIL.",
                }

            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )
            client = SendGridAPIClient(self.api_key)
            response = client.send(message)

            if 200 <= response.status_code < 300:
                self._increment_daily_count()
                return {"success": True, "message": "Email sent successfully."}

            self.logger.error(
                "SendGrid send failed: status=%s body=%s",
                response.status_code,
                response.body,
            )
            return {
                "success": False,
                "message": f"SendGrid returned status {response.status_code}.",
            }
        except Exception as exc:
            self.logger.exception("Failed to send email to %s: %s", to_email, exc)
            return {"success": False, "message": f"Email send failed: {exc}"}

    def _render_template(self, template_file: str, context: dict[str, Any]) -> str:
        template_path = self.templates_dir / template_file
        if not template_path.exists():
            self.logger.error("Email template not found: %s", template_path)
            return "<p>Template missing.</p>"
        template = Template(template_path.read_text(encoding="utf-8"))
        return template.render(**context)

    def _render_digest_html(self, user_name: str, alerts: list[dict[str, Any]]) -> str:
        rows = []
        for alert in alerts:
            rows.append(
                f"""
                <tr>
                  <td style="padding:10px;border-bottom:1px solid #e5e7eb;">{alert.get('job_title', 'Not specified')}</td>
                  <td style="padding:10px;border-bottom:1px solid #e5e7eb;">{alert.get('organization', 'Not specified')}</td>
                  <td style="padding:10px;border-bottom:1px solid #e5e7eb;">{alert.get('last_date_to_apply', 'Not specified')}</td>
                </tr>
                """
            )
        table_rows = "".join(rows)
        return f"""
        <html>
          <body style="margin:0;padding:18px;background:#f3f7fb;font-family:Arial,Helvetica,sans-serif;">
            <div style="max-width:680px;margin:auto;background:#fff;border:1px solid #dbe7f3;border-radius:10px;overflow:hidden;">
              <div style="background:#0f4c81;color:#fff;padding:16px 20px;">
                <h2 style="margin:0;">Saspirant Daily Digest</h2>
              </div>
              <div style="padding:18px;">
                <p>Hi {user_name or 'User'},</p>
                <p>You have multiple new matching alerts today. Here is your digest:</p>
                <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-size:14px;">
                  <tr>
                    <th align="left" style="padding:10px;background:#eff6ff;border-bottom:1px solid #dbe7f3;">Job</th>
                    <th align="left" style="padding:10px;background:#eff6ff;border-bottom:1px solid #dbe7f3;">Organization</th>
                    <th align="left" style="padding:10px;background:#eff6ff;border-bottom:1px solid #dbe7f3;">Last Date</th>
                  </tr>
                  {table_rows}
                </table>
                <p style="margin-top:16px;"><a href="{self.dashboard_url}" style="color:#0f4c81;">Open dashboard</a></p>
              </div>
            </div>
          </body>
        </html>
        """

    def _normalize_job_payload(self, job_notification: Any) -> dict[str, Any]:
        if isinstance(job_notification, dict):
            source = job_notification
        else:
            source = {
                "job_title": getattr(job_notification, "job_title", None),
                "organization": getattr(job_notification, "organization", None),
                "last_date_to_apply": getattr(job_notification, "last_date_to_apply", None),
                "age_limit": getattr(job_notification, "age_limit", None),
                "qualification_required": getattr(job_notification, "qualification_required", None),
                "source_url": getattr(job_notification, "source_url", None),
            }
        normalized = {
            "job_title": source.get("job_title") or "Not specified",
            "organization": source.get("organization") or "Not specified",
            "last_date_to_apply": self._to_iso_date(source.get("last_date_to_apply")) or "Not specified",
            "age_limit": source.get("age_limit") or "Not specified",
            "qualification_required": source.get("qualification_required") or "Not specified",
            "source_url": source.get("source_url") or "#",
        }
        return normalized

    def _to_iso_date(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value
        return str(value)

    def _deadline_color(self, last_date: str | None) -> str:
        if not last_date or last_date == "Not specified":
            return "#111827"
        try:
            parsed = datetime.fromisoformat(last_date).date()
            days_left = (parsed - date.today()).days
            return "#b91c1c" if days_left < 7 else "#111827"
        except ValueError:
            return "#111827"

    def _daily_count(self) -> int:
        return self._daily_counts[date.today().isoformat()]

    def _increment_daily_count(self) -> None:
        key = date.today().isoformat()
        self._daily_counts[key] += 1
        self._warn_if_near_limit()

    def _warn_if_near_limit(self) -> None:
        count = self._daily_count()
        if count >= int(self.DAILY_LIMIT * 0.8):
            self.logger.warning(
                "SendGrid usage high: %s/%s emails sent today.",
                count,
                self.DAILY_LIMIT,
            )

    def _can_send(self) -> bool:
        return self._daily_count() < self.DAILY_LIMIT


def test_email_service() -> None:
    """
    Run a quick integration test.
    Set TEST_EMAIL in environment before executing:
        TEST_EMAIL=you@example.com python backend/services/email_service.py
    """
    logging.basicConfig(level=logging.INFO)
    service = EmailService()
    recipient = os.getenv("TEST_EMAIL", "").strip()
    if not recipient:
        print("Set TEST_EMAIL environment variable to run email test.")
        return

    result = service.send_test_email(recipient)
    print(result)


if __name__ == "__main__":
    test_email_service()

