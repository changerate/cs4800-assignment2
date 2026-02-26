from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from app.extensions import db
from app.models.user import User

GRID_SIZE = 16
GRID_CELL_COUNT = GRID_SIZE * GRID_SIZE

# Each cell is None (empty) or {"user_id": int, "vehicle": str}
_grid_state: list[dict | None] = [None] * GRID_CELL_COUNT

grid_bp = Blueprint("grid", __name__)


def _unauthorized():
    return jsonify({"error": "unauthorized"}), 401


def _serialize_cell(cell: dict | None) -> dict | None:
    if cell is None:
        return None
    return {"user_id": cell["user_id"], "vehicle": cell["vehicle"]}


@grid_bp.get("")
def get_grid():
    if not session.get("user_id"):
        return _unauthorized()
    cells = [_serialize_cell(c) for c in _grid_state]
    return jsonify({"size": GRID_SIZE, "cells": cells})


@grid_bp.post("/toggle")
def toggle_cell():
    user_id = session.get("user_id")
    if not user_id:
        return _unauthorized()

    user = db.session.get(User, user_id)
    if not user:
        return _unauthorized()

    data = request.get_json(silent=True) or {}
    index = data.get("index")

    if not isinstance(index, int) or not (0 <= index < GRID_CELL_COUNT):
        return jsonify({"error": "invalid_index"}), 400

    current = _grid_state[index]

    if current is None:
        _grid_state[index] = {"user_id": user_id, "vehicle": user.vehicle}
        return jsonify({"index": index, "cell": _serialize_cell(_grid_state[index])})
    _grid_state[index] = None
    return jsonify({"index": index, "cell": None})

