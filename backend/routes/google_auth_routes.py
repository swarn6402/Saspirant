from datetime import date
import os
from urllib.parse import urlencode

from authlib.integrations.requests_client import OAuth2Session
from flask import Blueprint, current_app, redirect, request, session

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from models import User, db

google_auth_bp = Blueprint("google_auth", __name__)

GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


@google_auth_bp.route("/api/auth/google/login", methods=["GET"])
def google_login():
    """Initiate Google OAuth flow."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        current_app.logger.error("Google OAuth credentials are not configured.")
        return redirect(f"{FRONTEND_URL}/login?error=oauth_not_configured")

    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=GOOGLE_REDIRECT_URI,
    )

    authorization_url, state = oauth.create_authorization_url(GOOGLE_AUTHORIZATION_URL)
    # session["oauth_state"] = state  # Disabled for now

    return redirect(authorization_url)


@google_auth_bp.route("/api/auth/google/callback", methods=["GET"])
def google_callback():
    """Handle Google OAuth callback."""
    login_redirect = f"{FRONTEND_URL}/login"
    callback_redirect = f"{FRONTEND_URL}/auth/callback"

    try:
        # State validation is temporarily disabled for local development.
        # state = request.args.get("state")
        # stored_state = session.get("oauth_state")
        # if not state or not stored_state or state != stored_state:
        #     return redirect(f"{login_redirect}?error=invalid_state")

        code = request.args.get("code")
        if not code:
            return redirect(f"{login_redirect}?error=no_code")

        oauth = OAuth2Session(
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            redirect_uri=GOOGLE_REDIRECT_URI,
        )
        oauth.fetch_token(GOOGLE_TOKEN_URL, code=code)

        resp = oauth.get(GOOGLE_USERINFO_URL)
        user_info = resp.json()

        email = (user_info.get("email") or "").strip().lower()
        name = (user_info.get("name") or "").strip()

        if not email:
            return redirect(f"{login_redirect}?error=no_email")

        user = User.query.filter_by(email=email).first()

        if not user:
            # Existing schema requires these fields; populate safe defaults for OAuth users.
            user = User(
                name=name or "Google User",
                email=email,
                date_of_birth=date(2000, 1, 1),
                highest_qualification="Graduate",
                password_hash=None,
            )
            db.session.add(user)
            db.session.commit()

        session.pop("oauth_state", None)
        query = urlencode(
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
            }
        )
        return redirect(f"{callback_redirect}?{query}")
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Google OAuth error: %s", exc)
        return redirect(f"{login_redirect}?error=oauth_failed")
