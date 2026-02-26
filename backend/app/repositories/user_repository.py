from __future__ import annotations

from app.extensions import db
from app.models.user import User


class UserRepository:
    def get_by_id(self, user_id: int) -> User | None:
        return db.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).one_or_none()

    def list(self, limit: int = 50, offset: int = 0) -> list[User]:
        return (
            User.query.order_by(User.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, *, username: str, password_hash: str) -> User:
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user
