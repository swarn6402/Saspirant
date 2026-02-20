from urllib.parse import urlparse

import requests
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from models import MonitoredURL, User, UserPreference, db

preference_bp = Blueprint("preference_routes", __name__)

ALLOWED_SCRAPER_TYPES = {"html", "pdf", "dynamic"}
REQUEST_TIMEOUT_SECONDS = 8


def is_valid_url(url):
    if not isinstance(url, str) or not url.strip():
        return False

    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False

    try:
        response = requests.head(
            url.strip(), allow_redirects=True, timeout=REQUEST_TIMEOUT_SECONDS
        )
        if response.status_code < 400:
            return True
        response = requests.get(url.strip(), allow_redirects=True, timeout=REQUEST_TIMEOUT_SECONDS)
        return response.status_code < 400
    except requests.RequestException:
        return False


def detect_scraper_type(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=REQUEST_TIMEOUT_SECONDS)
        content_type = response.headers.get("Content-Type", "").lower()
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            return "pdf"

        body = response.text.lower()
        if ".pdf" in body:
            return "pdf"

        dynamic_markers = (
            "__next_data__",
            "ng-version",
            "data-reactroot",
            "window.__initial_state__",
            "id=\"app\"",
        )
        if any(marker in body for marker in dynamic_markers):
            return "dynamic"
    except requests.RequestException:
        pass

    return "html"


def _format_preference_response(preferences):
    if not preferences:
        return {
            "exam_categories": [],
            "min_age": None,
            "max_age": None,
            "preferred_locations": [],
        }

    first = preferences[0]
    return {
        "exam_categories": [pref.exam_category for pref in preferences],
        "min_age": first.min_age,
        "max_age": first.max_age,
        "preferred_locations": first.preferred_locations or [],
    }


def _format_url_response(monitored_url):
    return {
        "id": monitored_url.id,
        "url": monitored_url.url,
        "website_name": monitored_url.website_name,
        "scraper_type": monitored_url.scraper_type,
        "last_scraped_at": (
            monitored_url.last_scraped_at.isoformat() if monitored_url.last_scraped_at else None
        ),
        "is_active": monitored_url.is_active,
    }


@preference_bp.post("/<int:user_id>")
def create_or_update_preferences(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        payload = request.get_json(silent=True) or {}
        exam_categories = payload.get("exam_categories")
        min_age = payload.get("min_age")
        max_age = payload.get("max_age")
        preferred_locations = payload.get("preferred_locations", [])

        if not isinstance(exam_categories, list) or len(exam_categories) == 0:
            return jsonify({"error": "exam_categories must be a non-empty array"}), 400

        cleaned_categories = []
        for category in exam_categories:
            if not isinstance(category, str) or not category.strip():
                return jsonify({"error": "Each exam category must be a non-empty string"}), 400
            cleaned_categories.append(category.strip())

        if min_age is not None and not isinstance(min_age, int):
            return jsonify({"error": "min_age must be an integer"}), 400
        if max_age is not None and not isinstance(max_age, int):
            return jsonify({"error": "max_age must be an integer"}), 400
        if min_age is not None and max_age is not None and min_age > max_age:
            return jsonify({"error": "min_age cannot be greater than max_age"}), 400

        if preferred_locations is None:
            preferred_locations = []
        if not isinstance(preferred_locations, list):
            return jsonify({"error": "preferred_locations must be an array"}), 400

        for location in preferred_locations:
            if not isinstance(location, str) or not location.strip():
                return jsonify({"error": "Each preferred location must be a non-empty string"}), 400

        UserPreference.query.filter_by(user_id=user_id).delete()

        created_preferences = []
        cleaned_locations = [location.strip() for location in preferred_locations]
        for category in cleaned_categories:
            pref = UserPreference(
                user_id=user_id,
                exam_category=category,
                min_age=min_age,
                max_age=max_age,
                preferred_locations=cleaned_locations,
            )
            db.session.add(pref)
            created_preferences.append(pref)

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Preferences updated",
                    "preferences": _format_preference_response(created_preferences),
                }
            ),
            200,
        )
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error while saving preferences.")
        return jsonify({"error": "Database error while saving preferences"}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error while saving preferences.")
        return jsonify({"error": "Unexpected error while saving preferences"}), 500


@preference_bp.get("/<int:user_id>")
def get_preferences(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        preferences = (
            UserPreference.query.filter_by(user_id=user_id).order_by(UserPreference.id.asc()).all()
        )
        return jsonify(_format_preference_response(preferences)), 200
    except SQLAlchemyError:
        current_app.logger.exception("Database error while fetching preferences.")
        return jsonify({"error": "Database error while fetching preferences"}), 500
    except Exception:
        current_app.logger.exception("Unexpected error while fetching preferences.")
        return jsonify({"error": "Unexpected error while fetching preferences"}), 500


@preference_bp.post("/<int:user_id>/urls")
def add_monitored_url(user_id):
    try:
        print(f"Received URL add request: {request.json}")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a valid JSON object"}), 400

        url = payload.get("url")
        website_name = payload.get("website_name")
        scraper_type = payload.get("scraper_type", "html")

        if not url or not isinstance(url, str):
            return jsonify({"error": "url is required and must be a string"}), 400

        if not website_name or not isinstance(website_name, str) or not website_name.strip():
            return jsonify({"error": "website_name is required and must be a non-empty string"}), 400

        clean_url = url.strip()
        parsed = urlparse(clean_url)
        if parsed.scheme not in {"http", "https"}:
            return jsonify({"error": "url must start with http:// or https://"}), 400
        if not parsed.netloc:
            return jsonify({"error": "url must include a valid domain"}), 400

        existing = MonitoredURL.query.filter_by(user_id=user_id, url=clean_url).first()
        if existing:
            return jsonify({"error": "URL already exists for this user"}), 400

        if scraper_type is None or (isinstance(scraper_type, str) and not scraper_type.strip()):
            scraper_type = "html"
        elif not isinstance(scraper_type, str):
            return jsonify({"error": "scraper_type must be a string"}), 400
        else:
            scraper_type = scraper_type.strip().lower()

        if scraper_type not in ALLOWED_SCRAPER_TYPES:
            return jsonify({"error": "scraper_type must be one of: html, pdf, dynamic"}), 400

        monitored_url = MonitoredURL(
            user_id=user_id,
            url=clean_url,
            website_name=website_name.strip(),
            scraper_type=scraper_type,
        )
        db.session.add(monitored_url)
        db.session.commit()

        return (
            jsonify({"message": "URL added", "monitored_url": _format_url_response(monitored_url)}),
            201,
        )
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error while adding monitored URL.")
        return jsonify({"error": "Database error while adding URL"}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error while adding monitored URL.")
        return jsonify({"error": "Unexpected error while adding URL"}), 500


@preference_bp.get("/<int:user_id>/urls")
def get_monitored_urls(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        urls = MonitoredURL.query.filter_by(user_id=user_id).order_by(MonitoredURL.id.asc()).all()
        return jsonify({"urls": [_format_url_response(item) for item in urls]}), 200
    except SQLAlchemyError:
        current_app.logger.exception("Database error while fetching monitored URLs.")
        return jsonify({"error": "Database error while fetching URLs"}), 500
    except Exception:
        current_app.logger.exception("Unexpected error while fetching monitored URLs.")
        return jsonify({"error": "Unexpected error while fetching URLs"}), 500


@preference_bp.delete("/<int:user_id>/urls/<int:url_id>")
def delete_monitored_url(user_id, url_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        monitored_url = MonitoredURL.query.filter_by(id=url_id, user_id=user_id).first()
        if not monitored_url:
            return jsonify({"error": "Monitored URL not found"}), 404

        db.session.delete(monitored_url)
        db.session.commit()
        return jsonify({"message": "URL removed"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error while deleting monitored URL.")
        return jsonify({"error": "Database error while deleting URL"}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error while deleting monitored URL.")
        return jsonify({"error": "Unexpected error while deleting URL"}), 500
