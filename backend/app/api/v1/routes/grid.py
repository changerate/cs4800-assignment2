from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.models.grid_state import GridState
from app.models.user import User

GRID_SIZE = 16
GRID_CELL_COUNT = GRID_SIZE * GRID_SIZE

# Singleton row id for grid state
GRID_STATE_ID = 1

grid_bp = Blueprint("grid", __name__)


def _unauthorized():
    return jsonify({"error": "unauthorized"}), 401


def _serialize_cell(cell: dict | None) -> dict | None:
    if cell is None:
        return None
    return {"user_id": cell["user_id"], "vehicle": cell["vehicle"]}


def _get_grid_state() -> GridState:
    """Get or create the singleton grid state row; ensure cells length is GRID_CELL_COUNT."""
    try:
        row = db.session.get(GridState, GRID_STATE_ID)
    except OperationalError:
        db.session.rollback()
        db.create_all()
        row = db.session.get(GridState, GRID_STATE_ID)
    if row is None:
        row = GridState(id=GRID_STATE_ID, cells_json="[]")
        db.session.add(row)
        db.session.commit()
    cells = row.get_cells()
    if len(cells) != GRID_CELL_COUNT:
        # Pad with None or trim to fixed size
        if len(cells) < GRID_CELL_COUNT:
            cells = cells + [None] * (GRID_CELL_COUNT - len(cells))
        else:
            cells = cells[:GRID_CELL_COUNT]
        row.set_cells(cells)
        db.session.commit()
    return row


def _get_cells() -> list[dict | None]:
    return _get_grid_state().get_cells()


@grid_bp.get("")
def get_grid():
    if not session.get("user_id"):
        return _unauthorized()
    cells = [_serialize_cell(c) for c in _get_cells()]
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

    row = _get_grid_state()
    cells = row.get_cells()
    current = cells[index]

    if current is None:
        cells[index] = {"user_id": user_id, "vehicle": user.vehicle}
        row.set_cells(cells)
        db.session.commit()
        return jsonify({"index": index, "cell": _serialize_cell(cells[index])})
    cells[index] = None
    row.set_cells(cells)
    db.session.commit()
    return jsonify({"index": index, "cell": None})
