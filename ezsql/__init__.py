"""A small, beginner-friendly SQL wrapper for Python DB-API drivers."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, Optional

from .connection import EZConnection
from .exceptions import EZSQLError

__version__ = "0.3.0"

__all__ = ["connect", "EZConnection", "EZSQLError", "__version__"]


def connect(
    db_type: str = "sqlite",
    database: Optional[str] = None,
    host: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    port: Optional[int] = None,
) -> EZConnection:
    """Create and return an :class:`EZConnection`.

    Args:
        db_type: Database backend to use. Supported values are ``"sqlite"``,
            ``"postgres"``, ``"mysql"``, ``"myssql"``, and ``"oracle"``.
        database: SQLite file path, database name, Oracle service name or DSN,
            or ``None`` for an in-memory SQLite database.
        host: Database server host for client/server databases.
        user: Database username.
        password: Database password.
        port: Database server port.

    Raises:
        EZSQLError: If the database type is unsupported, a driver is missing,
            or the database connection fails.
    """
    normalized_db_type = db_type.lower().strip()

    if normalized_db_type == "sqlite":
        try:
            connection = sqlite3.connect(database or ":memory:")
        except sqlite3.Error as exc:
            raise EZSQLError(f"EZSQL Error: {exc}") from exc

        print("Connected to SQLite")
        return EZConnection(connection, normalized_db_type)

    if normalized_db_type in {"postgres", "postgresql"}:
        try:
            import psycopg2
        except ImportError as exc:
            raise EZSQLError(
                "EZSQL Error: PostgreSQL support requires psycopg2 to be installed."
            ) from exc

        connection_args = {
            "dbname": database,
            "host": host,
            "user": user,
            "password": password,
            "port": port,
        }
        connection_args = {
            key: value for key, value in connection_args.items() if value is not None
        }

        try:
            connection = psycopg2.connect(**connection_args)
        except psycopg2.Error as exc:
            raise EZSQLError(f"EZSQL Error: {exc}") from exc

        return EZConnection(connection, "postgres")

    if normalized_db_type in {"mysql", "myssql"}:
        try:
            import mysql.connector
        except ImportError as exc:
            raise EZSQLError(
                "EZSQL Error: MySQL support requires mysql-connector-python "
                "to be installed."
            ) from exc

        connection_args = _clean_connection_args(
            {
                "database": database,
                "host": host,
                "user": user,
                "password": password,
                "port": port,
            }
        )

        try:
            connection = mysql.connector.connect(**connection_args)
        except mysql.connector.Error as exc:
            raise EZSQLError(f"EZSQL Error: {exc}") from exc

        return EZConnection(connection, "mysql")

    if normalized_db_type == "oracle":
        try:
            import oracledb
        except ImportError as exc:
            raise EZSQLError(
                "EZSQL Error: Oracle support requires oracledb to be installed."
            ) from exc

        connection_args = _build_oracle_connection_args(
            oracledb=oracledb,
            database=database,
            host=host,
            user=user,
            password=password,
            port=port,
        )

        try:
            connection = oracledb.connect(**connection_args)
        except oracledb.Error as exc:
            raise EZSQLError(f"EZSQL Error: {exc}") from exc

        return EZConnection(connection, "oracle")

    raise EZSQLError(f"EZSQL Error: unsupported database type '{db_type}'.")


def _clean_connection_args(args: Dict[str, Any]) -> Dict[str, Any]:
    """Return connection arguments after removing unset values."""
    return {key: value for key, value in args.items() if value is not None}


def _build_oracle_connection_args(
    *,
    oracledb: Any,
    database: Optional[str],
    host: Optional[str],
    user: Optional[str],
    password: Optional[str],
    port: Optional[int],
) -> Dict[str, Any]:
    """Build Python-oracledb connection arguments.

    If ``host`` and ``database`` are provided, ``database`` is treated as the
    Oracle service name. If no host is provided, ``database`` is passed as the
    DSN so callers can use an existing Oracle DSN or Easy Connect string.
    """
    args = _clean_connection_args({"user": user, "password": password})

    if host and database:
        args["dsn"] = oracledb.makedsn(host, port or 1521, service_name=database)
    elif database:
        args["dsn"] = database
    elif host:
        args["dsn"] = host

    return args
