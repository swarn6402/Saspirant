from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    highest_qualification = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    preferences = db.relationship(
        "UserPreference", back_populates="user", cascade="all, delete-orphan", lazy=True
    )
    monitored_urls = db.relationship(
        "MonitoredURL", back_populates="user", cascade="all, delete-orphan", lazy=True
    )
    sent_alerts = db.relationship(
        "SentAlert", back_populates="user", cascade="all, delete-orphan", lazy=True
    )


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    exam_category = db.Column(db.String(100), nullable=False)
    min_age = db.Column(db.Integer, nullable=True)
    max_age = db.Column(db.Integer, nullable=True)
    preferred_locations = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="preferences")


class MonitoredURL(db.Model):
    __tablename__ = "monitored_urls"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    url = db.Column(db.String(2048), nullable=False)
    website_name = db.Column(db.String(150), nullable=True)
    scraper_type = db.Column(db.String(20), nullable=False)
    last_scraped_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    scrape_frequency_hours = db.Column(db.Integer, nullable=False, default=6)

    user = db.relationship("User", back_populates="monitored_urls")


class JobNotification(db.Model):
    __tablename__ = "job_notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_url = db.Column(db.String(2048), nullable=True)
    job_title = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=True)
    notification_date = db.Column(db.Date, nullable=True)
    last_date_to_apply = db.Column(db.Date, nullable=True)
    age_limit = db.Column(db.String(100), nullable=True)
    qualification_required = db.Column(db.String(255), nullable=True)
    exam_category = db.Column(db.String(100), nullable=True)
    full_details = db.Column(db.Text, nullable=True)
    pdf_url = db.Column(db.String(2048), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    sent_alerts = db.relationship(
        "SentAlert", back_populates="job_notification", cascade="all, delete-orphan", lazy=True
    )


class SentAlert(db.Model):
    __tablename__ = "sent_alerts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    job_notification_id = db.Column(
        db.Integer, db.ForeignKey("job_notifications.id"), nullable=False, index=True
    )
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    email_status = db.Column(db.String(20), nullable=False)

    user = db.relationship("User", back_populates="sent_alerts")
    job_notification = db.relationship("JobNotification", back_populates="sent_alerts")

