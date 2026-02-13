import logging
from datetime import date

import click
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from config import get_config
from models import User, db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.preference_routes import preference_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                ]
            }
        },
    )

    db.init_app(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli_commands(app)
    configure_logging(app)

    @app.get("/api/health")
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception:
            app.logger.exception("Health check failed while testing database connectivity.")
            return jsonify({"status": "error", "database": "disconnected"}), 500

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
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")


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


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        init_database(seed_sample=False)
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
