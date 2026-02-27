from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.models.grid_state import GridState
from app.models.user import User
from app.models.user_log import UserLog

GRID_SIZE = 10
GRID_CELL_COUNT = GRID_SIZE * GRID_SIZE

# Singleton row id for grid state
GRID_STATE_ID = 1

grid_bp = Blueprint("grid", __name__)


def _add_user_log(user_id: int, message: str) -> None:
    """Persist a log message for the given user."""
    if not user_id or not message:
        return
    try:
        entry = UserLog(user_id=user_id, message=message)
        db.session.add(entry)
    except OperationalError:
        db.session.rollback()
        db.create_all()
        try:
            entry = UserLog(user_id=user_id, message=message)
            db.session.add(entry)
        except OperationalError:
            db.session.rollback()


def _get_user_logs(user_id: int, limit: int = 50) -> list[str]:
    """Return recent log messages for the given user, newest first."""
    if not user_id:
        return []
    try:
        logs = (
            UserLog.query.filter_by(user_id=user_id)
            .order_by(UserLog.created_at.desc())
            .limit(limit)
            .all()
        )
    except OperationalError:
        db.session.rollback()
        db.create_all()
        try:
            logs = (
                UserLog.query.filter_by(user_id=user_id)
                .order_by(UserLog.created_at.desc())
                .limit(limit)
                .all()
            )
        except OperationalError:
            db.session.rollback()
            return []
    return [log.message for log in logs]


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
    user_id = session.get("user_id")
    if not user_id:
        return _unauthorized()
    cells = [_serialize_cell(c) for c in _get_cells()]
    logs = _get_user_logs(user_id)
    return jsonify({"size": GRID_SIZE, "cells": cells, "logs": logs})


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
        try:
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            db.create_all()
            db.session.commit()
        return jsonify({"index": index, "cell": _serialize_cell(cells[index])})

    # If another user removes this vehicle, log it for the original owner.
    current_user_id = current.get("user_id") if isinstance(current, dict) else None
    if current_user_id and current_user_id != user_id:
        towed_user = db.session.get(User, current_user_id)
        if towed_user:
            vehicle_emoji = current.get("vehicle") if isinstance(current, dict) else None
            vehicle_label = vehicle_emoji or "vehicle"
            message = f"{user.username} towed your {vehicle_label} from its spot!"
            _add_user_log(towed_user.id, message)

    cells[index] = None
    row.set_cells(cells)
    try:
        db.session.commit()
    except OperationalError:
        db.session.rollback()
        db.create_all()
        db.session.commit()
    return jsonify({"index": index, "cell": None})
