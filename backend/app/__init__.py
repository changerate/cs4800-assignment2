from __future__ import annotations

from flask import Flask, jsonify, render_template, request, session

from app.api.v1 import api_v1_bp
from app.core.config import load_config
from app.core.logging import configure_logging
from app.extensions import db, migrate
from app.models.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError


def create_app(env: str | None = None) -> Flask:
    app = Flask(__name__)

    app.config.from_object(load_config(env))

    configure_logging(app)
    _register_extensions(app)
    _register_models(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"error": "missing_credentials"}), 400

        user = User.query.filter_by(username=username).one_or_none()

        status = "ok"
        if user is None:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return jsonify({"error": "username_already_exists"}), 400
            status = "registered"
        else:
            if not check_password_hash(user.password_hash, password):
                return jsonify({"error": "invalid_credentials"}), 400

        session["user_id"] = user.id

        # Ensure a default vehicle for older rows without one.
        if not getattr(user, "vehicle", None):
            user.vehicle = "🚗"
            db.session.commit()

        return jsonify({"status": status, "username": user.username, "vehicle": user.vehicle})

    @app.post("/logout")
    def logout():
        session.pop("user_id", None)
        return jsonify({"status": "ok"})

    @app.get("/me")
    def me():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "unauthorized"}), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "unauthorized"}), 401

        return jsonify({"username": user.username, "vehicle": getattr(user, "vehicle", "🚗")})

    @app.post("/me/vehicle")
    def update_vehicle():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        vehicle = (data.get("vehicle") or "").strip()
        allowed = ["🚗", "🛸", "🚀", "✈️", "🚢", "🚁", "🚙", "🚣", "🚂", "🚃", "🚆", "🚋", "🚌", "🚑", "🚒"]

        if vehicle not in allowed:
            return jsonify({"error": "invalid_vehicle"}), 400

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "unauthorized"}), 401

        user.vehicle = vehicle
        db.session.commit()

        return jsonify({"vehicle": user.vehicle})

    return app


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def _register_models(app: Flask) -> None:
    # Ensure SQLAlchemy knows about all models before creating tables/migrations.
    import importlib

    importlib.import_module("app.models")

    if app.config.get("TESTING"):
        with app.app_context():
            db.create_all()


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"error": "not_found"}), 404

    @app.errorhandler(500)
    def internal_error(_err):
        return jsonify({"error": "internal_server_error"}), 500
