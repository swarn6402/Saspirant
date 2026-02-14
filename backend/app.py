import logging
import os
from datetime import date

import click
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
from sqlalchemy import text

from config import get_config
from models import User, db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.preference_routes import preference_bp
from services.scheduler_service import SchedulerService


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    if os.environ.get("FLASK_ENV") == "production":
        app.config["DEBUG"] = False
        app.config["TESTING"] = False

        @app.before_request
        def force_https():
            if not request.is_secure and request.headers.get("X-Forwarded-Proto") != "https":
                url = request.url.replace("http://", "https://", 1)
                return redirect(url, code=301)

    db.init_app(app)
    register_blueprints(app)
    apply_cors(app)
    register_error_handlers(app)
    register_cli_commands(app)
    configure_logging(app)
    register_scheduler(app)

    @app.get("/api/health")
    def api_health_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception:
            app.logger.exception("Health check failed while testing database connectivity.")
            return jsonify({"status": "error", "database": "disconnected"}), 500

    @app.route("/health")
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            scheduler_service = app.extensions.get("scheduler_service")
            scheduler_state = (
                "running"
                if scheduler_service and scheduler_service.scheduler.running
                else "stopped"
            )
            return (
                jsonify(
                    {
                        "status": "healthy",
                        "database": "connected",
                        "scheduler": scheduler_state,
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.get("/")
    def root_status():
        return jsonify({"service": "Saspirant API", "status": "running"}), 200

    @app.route("/api/routes", methods=["GET"])
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": sorted(list(rule.methods)),
                    "path": str(rule),
                }
            )
        return jsonify(routes), 200

    return app


def init_database(seed_sample: bool = False):
    db.create_all()

    if seed_sample and User.query.count() == 0:
        sample_user = User(
            name="Sample User",
            email="sample.user@example.com",
            date_of_birth=date(2000, 1, 1),
            highest_qualification="Graduate",
        )
        db.session.add(sample_user)
        db.session.commit()


def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(preference_bp, url_prefix="/api/preferences")
    app.register_blueprint(dashboard_bp)


def apply_cors(app: Flask):
    # Apply CORS after all blueprints are registered.
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-User-Id"],
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    )

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,X-User-Id",
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,PUT,POST,DELETE,PATCH,OPTIONS",
        )
        return response


def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found.",
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Unhandled internal server error: %s", error)
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )


def register_cli_commands(app: Flask):
    @app.cli.command("init-db")
    @click.option("--seed", is_flag=True, help="Seed one sample user.")
    def init_db_command(seed):
        with app.app_context():
            init_database(seed_sample=seed)
        click.echo("Database initialized.")


def configure_logging(app: Flask):
    if app.logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def register_scheduler(app: Flask):
    scheduler = SchedulerService(app=app)
    app.extensions["scheduler_service"] = scheduler

    if hasattr(app, "before_first_request"):
        @app.before_first_request
        def init_scheduler():
            scheduler.start_scheduler()
    else:
        # Flask 3 compatibility: emulate first-request startup.
        app.config["_scheduler_started"] = False

        @app.before_request
        def init_scheduler_fallback():
            if not app.config.get("_scheduler_started", False):
                scheduler.start_scheduler()
                app.config["_scheduler_started"] = True


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        init_database(seed_sample=False)
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
