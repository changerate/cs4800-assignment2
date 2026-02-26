from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")

    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    JSON_SORT_KEYS: bool = False


@dataclass(frozen=True)
class DevelopmentConfig(BaseConfig):
    ENV: str = "development"
    DEBUG: bool = True


@dataclass(frozen=True)
class TestingConfig(BaseConfig):
    ENV: str = "testing"
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"


@dataclass(frozen=True)
class ProductionConfig(BaseConfig):
    ENV: str = "production"
    DEBUG: bool = False


def load_config(env: str | None) -> type[BaseConfig]:
    env_norm = (env or os.getenv("FLASK_ENV") or "development").strip().lower()
    if env_norm in {"prod", "production"}:
        return ProductionConfig
    if env_norm in {"test", "testing"}:
        return TestingConfig
    return DevelopmentConfig
