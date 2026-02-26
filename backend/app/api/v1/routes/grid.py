from __future__ import annotations

from flask import Blueprint, jsonify, request, session

GRID_SIZE = 16
GRID_CELL_COUNT = GRID_SIZE * GRID_SIZE

_grid_state: list[bool] = [False] * GRID_CELL_COUNT

grid_bp = Blueprint("grid", __name__)


def _unauthorized():
    return jsonify({"error": "unauthorized"}), 401


@grid_bp.get("")
def get_grid():
    if not session.get("user_id"):
        return _unauthorized()
    return jsonify({"size": GRID_SIZE, "cells": _grid_state})


@grid_bp.post("/toggle")
def toggle_cell():
    if not session.get("user_id"):
        return _unauthorized()
    data = request.get_json(silent=True) or {}
    index = data.get("index")

    if not isinstance(index, int) or not (0 <= index < GRID_CELL_COUNT):
        return jsonify({"error": "invalid_index"}), 400

    _grid_state[index] = not _grid_state[index]
    return jsonify({"index": index, "value": _grid_state[index]})

