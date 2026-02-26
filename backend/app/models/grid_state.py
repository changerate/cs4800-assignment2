from __future__ import annotations

import json

from app.extensions import db

class GridState(db.Model):
    """Singleton row holding the full grid state for all workers."""

    __tablename__ = "grid_state"

    id = db.Column(db.Integer, primary_key=True)
    cells_json = db.Column(db.Text, nullable=False, default="[]")

    def get_cells(self) -> list[dict | None]:
        try:
            data = json.loads(self.cells_json)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_cells(self, cells: list[dict | None]) -> None:
        self.cells_json = json.dumps(cells)
