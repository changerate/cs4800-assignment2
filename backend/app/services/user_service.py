from __future__ import annotations

from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository | None = None) -> None:
        self._repo = repo or UserRepository()

    def list_users(self, *, limit: int = 50, offset: int = 0):
        limit = max(1, min(200, limit))
        offset = max(0, offset)
        return self._repo.list(limit=limit, offset=offset)

    def create_user(self, *, username: str, password_hash: str):
        username_norm = (username or "").strip()
        if not username_norm:
            raise ValueError("invalid_username")

        existing = self._repo.get_by_username(username_norm)
        if existing is not None:
            raise ValueError("username_already_exists")

        return self._repo.create(username=username_norm, password_hash=password_hash)
