"""
Shared PostgreSQL engine and session configuration.

This module ows creation of SQLAlchemy database infrastructure.
ORM models do not create their own engines or sessions.

Keeping connection management centralized prevents persistance classes from becoming coupled to cridentials,
PostgreSQL connection details, or SQLAlchemy engine configuration.
"""

from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from local_ai_router.config import DatabaseSettings, get_database_settings


def build_database_url(database_settings: DatabaseSettings | None = None) -> URL:
    """
    Build a SQLAlchemy PostgreSQL connection URL.

    SQLAlchemy URL object is used instead of manually concatenating a string.
    This is important because passwords can contain characters such a '@', ':', or '/' that would otherwise require URL escaping.

    Args:
        database_settings:
            Optional explicit settings. When omitted, settings are loaded from the application's environment configuration.

    Returns:
        URL:
            SQLAlchemy URL configured for PostgreSQL using Psycopg 3.
    """

    if database_settings is None:
        database_settings = get_database_settings()

    return URL.create(
        drivername="postgresql+psycopg",
        username=database_settings.username,
        password=database_settings.password,
        host=database_settings.host,
        port=database_settings.port,
        database=database_settings.database_name,
    )


def create_database_engine(database_settings: DatabaseSettings | None = None) -> Engine:
    """
    Create the application's SqLAlchemy database engine.

    The engine manages PostgreSQL connections and SQLAlchemy's connection pool.

    No database connection occurs werely by importing this module.
    A connection is opened only when application code actually requests one from the engine.

    Args:
        database_settings:
            Optional database settings, primarily useful for testing or future alternate environments.

    Returns:
        Engie:
            Configured sychronous SQLAlchemy engine.
    """

    database_url = build_database_url(database_settings)

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def create_database_session_factory(database_engine: Engine) -> sessionmaker[Session]:
    """
    Create a SQLAlchemy session factory bound to an engine.

    A session represents a unit of database work.
    Repositories will later recieve sessions created by this factory
    rather than opening independent database connections themselves.

    Args:
        database_engine:
            SQLAlchemy engine that provides PostgreSQL connections.

    Returns:
        sessionmaker[Session]:
            Factory used to create SQLAlchemy Session instances.
    """

    return sessionmaker(
        bind=database_engine,
        autoflush=False,
        expire_on_commit=False,
    )
