"""A friendly SQL toolkit for Python DB-API drivers."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, Mapping, Optional, Union
from urllib.parse import parse_qs, unquote, urlparse

from .config import DatabaseConfig, config_from_env
from .connection import EZConnection, PyQueryXConnection
from .exceptions import EZSQLError, PyQueryXError

__version__ = "0.4.1"

__all__ = [
    "connect",
    "connect_from_config",
    "connect_from_env",
    "DatabaseConfig",
    "PyQueryXConnection",
    "PyQueryXError",
    "EZConnection",
    "EZSQLError",
    "__version__",
]


def connect(
    db_type: str = "sqlite",
    database: Optional[str] = None,
    host: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    port: Optional[int] = None,
    *,
    url: Optional[str] = None,
    config: Optional[Union[DatabaseConfig, Mapping[str, Any]]] = None,
    timeout: Optional[float] = None,
    autocommit: Optional[bool] = None,
    echo: bool = False,
    **options: Any,
) -> PyQueryXConnection:
    """Create and return a :class:`PyQueryXConnection`.

    Args:
        db_type: Backend name. Supports ``sqlite``, ``postgres``, ``mysql``,
            and ``oracle``.
        database: SQLite path, database name, Oracle service name, or DSN.
        host: Server host for client/server databases.
        user: Database username.
        password: Database password.
        port: Database server port.
        url: Optional connection URL, such as ``sqlite:///app.db`` or
            ``postgres://user:pass@localhost:5432/app``.
        config: Optional :class:`DatabaseConfig` or mapping.
        timeout: Optional connection timeout where the driver supports it.
        autocommit: Optional auto-commit behavior.
        echo: Print SQL before execution when True.
        **options: Extra driver-specific connection options.
    """
    merged = _merge_connection_inputs(
        db_type=db_type,
        database=database,
        host=host,
        user=user,
        password=password,
        port=port,
        url=url,
        config=config,
        timeout=timeout,
        autocommit=autocommit,
        echo=echo,
        options=options,
    )

    normalized_db_type = merged["db_type"].lower().strip()
    driver_options = merged.pop("options")
    connection_flags = {
        "autocommit": merged.pop("autocommit"),
        "echo": merged.pop("echo"),
    }

    if normalized_db_type == "sqlite":
        connection = _connect_sqlite(merged, driver_options)
        return PyQueryXConnection(connection, "sqlite", **connection_flags)

    if normalized_db_type in {"postgres", "postgresql"}:
        connection = _connect_postgres(merged, driver_options)
        return PyQueryXConnection(connection, "postgres", **connection_flags)

    if normalized_db_type in {"mysql", "myssql"}:
        connection = _connect_mysql(merged, driver_options)
        return PyQueryXConnection(connection, "mysql", **connection_flags)

    if normalized_db_type == "oracle":
        connection = _connect_oracle(merged, driver_options)
        return PyQueryXConnection(connection, "oracle", **connection_flags)

    raise PyQueryXError(f"PyQueryX Error: unsupported database type '{db_type}'.")


def connect_from_config(
    config: Union[DatabaseConfig, Mapping[str, Any]]
) -> PyQueryXConnection:
    """Create a connection from a config object or mapping."""
    return connect(config=config)


def connect_from_env(prefix: str = "PYQUERYX_") -> PyQueryXConnection:
    """Create a connection from environment variables."""
    return connect(config=config_from_env(prefix))


def _connect_sqlite(values: Dict[str, Any], options: Dict[str, Any]) -> Any:
    args = dict(options)
    if values.get("timeout") is not None:
        args["timeout"] = values["timeout"]

    try:
        return sqlite3.connect(values.get("database") or ":memory:", **args)
    except sqlite3.Error as exc:
        raise PyQueryXError(f"PyQueryX Error: {exc}") from exc


def _connect_postgres(values: Dict[str, Any], options: Dict[str, Any]) -> Any:
    postgres_driver = None
    postgres_driver_name = None
    postgres_import_error = None

    try:
        import psycopg2

        postgres_driver = psycopg2
        postgres_driver_name = "psycopg"
    except ImportError as exc:
        postgres_import_error = exc

    if postgres_driver is None:
        try:
            import psycopg

            postgres_driver = psycopg
            postgres_driver_name = "psycopg"
        except ImportError as exc:
            postgres_import_error = exc

    if postgres_driver is None:
        try:
            from pg8000 import dbapi as pg8000

            postgres_driver = pg8000
            postgres_driver_name = "pg8000"
        except ImportError as exc:
            postgres_import_error = exc

    if postgres_driver is None:
        raise PyQueryXError(
            "PyQueryX Error: PostgreSQL support requires psycopg2, psycopg, "
            "or pg8000 to be installed."
        ) from postgres_import_error

    database_key = "database" if postgres_driver_name == "pg8000" else "dbname"
    connection_args = _clean_connection_args(
        {
            database_key: values.get("database"),
            "host": values.get("host"),
            "user": values.get("user"),
            "password": values.get("password"),
            "port": values.get("port"),
            "connect_timeout": values.get("timeout"),
            **options,
        }
    )

    try:
        return postgres_driver.connect(**connection_args)
    except postgres_driver.Error as exc:
        raise PyQueryXError(f"PyQueryX Error: {exc}") from exc


def _connect_mysql(values: Dict[str, Any], options: Dict[str, Any]) -> Any:
    try:
        import mysql.connector
    except ImportError as exc:
        raise PyQueryXError(
            "PyQueryX Error: MySQL support requires mysql-connector-python "
            "to be installed."
        ) from exc

    connection_args = _clean_connection_args(
        {
            "database": values.get("database"),
            "host": values.get("host"),
            "user": values.get("user"),
            "password": values.get("password"),
            "port": values.get("port"),
            "connection_timeout": values.get("timeout"),
            **options,
        }
    )

    try:
        return mysql.connector.connect(**connection_args)
    except mysql.connector.Error as exc:
        raise PyQueryXError(f"PyQueryX Error: {exc}") from exc


def _connect_oracle(values: Dict[str, Any], options: Dict[str, Any]) -> Any:
    try:
        import oracledb
    except ImportError as exc:
        raise PyQueryXError(
            "PyQueryX Error: Oracle support requires oracledb to be installed."
        ) from exc

    connection_args = _build_oracle_connection_args(
        oracledb=oracledb,
        database=values.get("database"),
        host=values.get("host"),
        user=values.get("user"),
        password=values.get("password"),
        port=values.get("port"),
    )
    connection_args.update(options)

    try:
        return oracledb.connect(**connection_args)
    except oracledb.Error as exc:
        raise PyQueryXError(f"PyQueryX Error: {exc}") from exc


def _merge_connection_inputs(
    *,
    db_type: str,
    database: Optional[str],
    host: Optional[str],
    user: Optional[str],
    password: Optional[str],
    port: Optional[int],
    url: Optional[str],
    config: Optional[Union[DatabaseConfig, Mapping[str, Any]]],
    timeout: Optional[float],
    autocommit: Optional[bool],
    echo: bool,
    options: Dict[str, Any],
) -> Dict[str, Any]:
    values: Dict[str, Any] = {
        "db_type": db_type,
        "database": database,
        "host": host,
        "user": user,
        "password": password,
        "port": port,
        "timeout": timeout,
        "autocommit": autocommit,
        "echo": echo,
        "options": dict(options),
    }

    if config is not None:
        config_obj = (
            config
            if isinstance(config, DatabaseConfig)
            else DatabaseConfig.from_mapping(config)
        )
        values.update(
            {
                "db_type": config_obj.db_type,
                "database": config_obj.database,
                "host": config_obj.host,
                "user": config_obj.user,
                "password": config_obj.password,
                "port": config_obj.port,
                "timeout": config_obj.timeout,
                "autocommit": config_obj.autocommit,
                "echo": config_obj.echo,
                "options": dict(config_obj.options or {}),
            }
        )

    if url:
        values.update(_parse_url(url))

    explicit_values = {
        "database": database,
        "host": host,
        "user": user,
        "password": password,
        "port": port,
        "timeout": timeout,
        "autocommit": autocommit,
    }
    for key, value in explicit_values.items():
        if value is not None:
            values[key] = value

    if db_type != "sqlite":
        values["db_type"] = db_type
    if options:
        values["options"].update(options)

    return values


def _parse_url(url: str) -> Dict[str, Any]:
    parsed = urlparse(url)
    db_type = _normalize_url_scheme(parsed.scheme)
    query_options = {key: value[-1] for key, value in parse_qs(parsed.query).items()}

    if db_type == "sqlite":
        if parsed.netloc and parsed.path:
            database = f"{parsed.netloc}{parsed.path}"
        else:
            database = unquote(parsed.path.lstrip("/")) or ":memory:"
        return {"db_type": db_type, "database": database, "options": query_options}

    return {
        "db_type": db_type,
        "database": unquote(parsed.path.lstrip("/")) or None,
        "host": parsed.hostname,
        "user": unquote(parsed.username) if parsed.username else None,
        "password": unquote(parsed.password) if parsed.password else None,
        "port": parsed.port,
        "options": query_options,
    }


def _normalize_url_scheme(scheme: str) -> str:
    aliases = {
        "postgresql": "postgres",
        "postgres": "postgres",
        "mysql": "mysql",
        "oracle": "oracle",
        "sqlite": "sqlite",
    }
    return aliases.get(scheme.lower(), scheme.lower())


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
    """Build Python-oracledb connection arguments."""
    args = _clean_connection_args({"user": user, "password": password})

    if host and database:
        args["dsn"] = oracledb.makedsn(host, port or 1521, service_name=database)
    elif database:
        args["dsn"] = database
    elif host:
        args["dsn"] = host

    return args
