from __future__ import annotations

from flask import Blueprint

from app.api.v1.routes.grid import grid_bp
from app.api.v1.routes.health import health_bp
from app.api.v1.routes.users import users_bp

api_v1_bp = Blueprint("api_v1", __name__)

api_v1_bp.register_blueprint(health_bp)
api_v1_bp.register_blueprint(users_bp, url_prefix="/users")
api_v1_bp.register_blueprint(grid_bp, url_prefix="/grid")
