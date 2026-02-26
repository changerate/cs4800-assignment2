from __future__ import annotations

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.schemas.user_schema import CreateUserSchema, UserSchema
from app.services.user_service import UserService
from werkzeug.security import generate_password_hash

users_bp = Blueprint("users", __name__)

_user_schema = UserSchema()
_users_schema = UserSchema(many=True)
_create_user_schema = CreateUserSchema()


@users_bp.get("")
def list_users():
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    users = UserService().list_users(limit=limit, offset=offset)
    return jsonify({"data": _users_schema.dump(users)})


@users_bp.post("")
def create_user():
    try:
        payload = _create_user_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validation_error", "details": e.messages}), 400

    try:
        password_hash = generate_password_hash(payload["password"])
        user = UserService().create_user(
            username=payload["username"],
            password_hash=password_hash,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"data": _user_schema.dump(user)}), 201
