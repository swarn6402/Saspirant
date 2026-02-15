import re
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from models import User, db
from services.email_service import EmailService

auth_bp = Blueprint("auth_routes", __name__)

ALLOWED_QUALIFICATIONS = {
    "10th",
    "12th",
    "Graduate",
    "Post-Graduate",
    "Doctorate",
}


def validate_email(email):
    if not isinstance(email, str):
        return False
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def format_user_response(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "qualification": user.highest_qualification,
    }


@auth_bp.post("/register")
def register_user():
    try:
        payload = request.get_json(silent=True) or {}

        name = payload.get("name")
        email = payload.get("email")
        password = payload.get("password")
        dob_str = payload.get("date_of_birth")
        highest_qualification = payload.get("highest_qualification")

        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Name is required"}), 400

        if not email or not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        if not password or not isinstance(password, str):
            return jsonify({"error": "Password is required"}), 400

        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        if not dob_str or not isinstance(dob_str, str):
            return jsonify({"error": "date_of_birth is required in YYYY-MM-DD format"}), 400

        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "date_of_birth must be in YYYY-MM-DD format"}), 400

        if calculate_age(dob) < 15:
            return jsonify({"error": "User must be at least 15 years old"}), 400

        if highest_qualification not in ALLOWED_QUALIFICATIONS:
            return (
                jsonify(
                    {
                        "error": (
                            "highest_qualification must be one of: "
                            "10th, 12th, Graduate, Post-Graduate, Doctorate"
                        )
                    }
                ),
                400,
            )

        normalized_email = email.strip().lower()
        existing_user = User.query.filter_by(email=normalized_email).first()
        if existing_user:
            return jsonify({"error": "Email already exists"}), 400

        user = User(
            name=name.strip(),
            email=normalized_email,
            date_of_birth=dob,
            highest_qualification=highest_qualification,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Send welcome email
        try:
            email_service = EmailService()
            result = email_service.send_welcome_email(user.email, user.name)
            print(f"Welcome email result: {result}")
            if not result.get('success'):
                print(f"Welcome email failed: {result.get('message')}")
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")
            import traceback
            traceback.print_exc()

        return jsonify({"message": "User registered successfully", "user_id": user.id}), 201
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error during user registration.")
        return jsonify({"error": "Database error while registering user"}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error during user registration.")
        return jsonify({"error": "Unexpected error while registering user"}), 500


@auth_bp.post("/login")
def login():
    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.exception("Unexpected error during login.")
        return jsonify({"error": str(e)}), 500


@auth_bp.post("/logout")
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.get("/user/<int:user_id>")
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(format_user_response(user)), 200
    except SQLAlchemyError:
        current_app.logger.exception("Database error while fetching user.")
        return jsonify({"error": "Database error while fetching user"}), 500
    except Exception:
        current_app.logger.exception("Unexpected error while fetching user.")
        return jsonify({"error": "Unexpected error while fetching user"}), 500


@auth_bp.patch("/user/<int:user_id>")
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        highest_qualification = payload.get("highest_qualification")

        if name is None and highest_qualification is None:
            return (
                jsonify({"error": "At least one field is required: name, highest_qualification"}),
                400,
            )

        if name is not None:
            if not isinstance(name, str) or not name.strip():
                return jsonify({"error": "name must be a non-empty string"}), 400
            user.name = name.strip()

        if highest_qualification is not None:
            if highest_qualification not in ALLOWED_QUALIFICATIONS:
                return (
                    jsonify(
                        {
                            "error": (
                                "highest_qualification must be one of: "
                                "10th, 12th, Graduate, Post-Graduate, Doctorate"
                            )
                        }
                    ),
                    400,
                )
            user.highest_qualification = highest_qualification

        db.session.commit()
        return jsonify(format_user_response(user)), 200
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Database error while updating user.")
        return jsonify({"error": "Database error while updating user"}), 500
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Unexpected error while updating user.")
        return jsonify({"error": "Unexpected error while updating user"}), 500
