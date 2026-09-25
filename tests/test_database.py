"""
Unit tests for PostgreSQL connection configuration.

These tests verify database configuration without connecting to a real
PostgreSQL server. Real database connectivity is tested separately as an
integration concern.
"""

import pytest

from local_ai_router.config import DatabaseSettings, get_database_settings
from local_ai_router.persistence.database import build_database_url


def test_database_settings_use_expected_local_defaults(monkeypatch) -> None:
    """
    Verify local development settings use the expected project defaults.
    """

    monkeypatch.setenv(
        "LOCAL_AI_ROUTER_DB_PASSWORD",
        "test-password",
    )

    monkeypatch.delenv(
        "LOCAL_AI_ROUTER_DB_HOST",
        raising=False,
    )
    monkeypatch.delenv(
        "LOCAL_AI_ROUTER_DB_PORT",
        raising=False,
    )
    monkeypatch.delenv(
        "LOCAL_AI_ROUTER_DB_NAME",
        raising=False,
    )
    monkeypatch.delenv(
        "LOCAL_AI_ROUTER_DB_USER",
        raising=False,
    )

    database_settings = get_database_settings()

    assert database_settings.host == "127.0.0.1"
    assert database_settings.port == 5432
    assert database_settings.database_name == "local_ai_router"
    assert database_settings.username == "local_ai_router_app"
    assert database_settings.password == "test-password"


def test_database_password_is_required(monkeypatch) -> None:
    """
    Verify that the application refuses to invent or hard-code a DB password.
    """

    monkeypatch.delenv(
        "LOCAL_AI_ROUTER_DB_PASSWORD",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="LOCAL_AI_ROUTER_DB_PASSWORD",
    ):
        get_database_settings()


def test_database_url_uses_psycopg_driver() -> None:
    """
    Verify SQLAlchemy uses PostgreSQL through the Psycopg 3 driver.
    """

    database_settings = DatabaseSettings(
        host="127.0.0.1",
        port=5432,
        database_name="local_ai_router",
        username="local_ai_router_app",
        password="test-password",
    )

    database_url = build_database_url(database_settings)

    assert database_url.drivername == "postgresql+psycopg"
    assert database_url.host == "127.0.0.1"
    assert database_url.port == 5432
    assert database_url.database == "local_ai_router"
    assert database_url.username == "local_ai_router_app"
