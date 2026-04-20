"""Tests for the ezsql public API."""

import os
import importlib
import sqlite3
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from ezsql import EZConnection, EZSQLError, connect
from ezsql.helpers import is_select_query


class EZSQLTests(unittest.TestCase):
    """SQLite-backed tests for ezsql behavior."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temp_dir.name, "test.db")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def connect_sqlite(self) -> EZConnection:
        output = StringIO()

        with redirect_stdout(output):
            return connect("sqlite", database=self.database_path)

    def test_sqlite_usage_example(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            conn = connect("sqlite", database=self.database_path)

        self.assertIn("Connected to SQLite", output.getvalue())

        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Srinjan')")

        result = conn.query("SELECT * FROM users")

        self.assertEqual(result, [(1, "Srinjan")])
        conn.close()

    def test_execute_returns_none(self) -> None:
        conn = self.connect_sqlite()

        result = conn.execute("CREATE TABLE users (id INTEGER)")

        self.assertIsNone(result)
        conn.close()

    def test_query_returns_empty_list_for_write_query(self) -> None:
        conn = self.connect_sqlite()

        result = conn.query("CREATE TABLE users (id INTEGER)")

        self.assertEqual(result, [])
        conn.close()

    def test_repr_includes_database_type(self) -> None:
        conn = self.connect_sqlite()

        self.assertEqual(repr(conn), "<EZSQL Connection (sqlite)>")
        conn.close()

    def test_unsupported_database_type_raises_ezsql_error(self) -> None:
        with self.assertRaisesRegex(EZSQLError, "unsupported database type"):
            connect("db2")

    def test_mysql_missing_driver_raises_clean_error(self) -> None:
        with patch("builtins.__import__", side_effect=self.fail_import("mysql")):
            with self.assertRaisesRegex(EZSQLError, "mysql-connector-python"):
                connect("mysql")

    def test_postgres_missing_driver_raises_clean_error(self) -> None:
        with patch(
            "builtins.__import__",
            side_effect=self.fail_imports({"pg8000", "psycopg", "psycopg2"}),
        ):
            with self.assertRaisesRegex(EZSQLError, "psycopg2, psycopg, or pg8000"):
                connect("postgres")

    def test_myssql_alias_uses_mysql_driver(self) -> None:
        with patch("builtins.__import__", side_effect=self.fail_import("mysql")):
            with self.assertRaisesRegex(EZSQLError, "mysql-connector-python"):
                connect("myssql")

    def test_oracle_missing_driver_raises_clean_error(self) -> None:
        with patch("builtins.__import__", side_effect=self.fail_import("oracledb")):
            with self.assertRaisesRegex(EZSQLError, "oracledb"):
                connect("oracle")

    def test_postgres_connection_arguments(self) -> None:
        captured = {}
        raw_connection = object()

        def fake_connect(**kwargs):
            captured.update(kwargs)
            return raw_connection

        psycopg2 = types.ModuleType("psycopg2")
        psycopg2.connect = fake_connect
        psycopg2.Error = RuntimeError

        with patch.dict(sys.modules, {"psycopg2": psycopg2}):
            conn = connect(
                "postgres",
                database="app",
                host="localhost",
                user="postgres",
                password="secret",
                port=5432,
            )

        self.assertIs(conn.conn, raw_connection)
        self.assertEqual(conn.db_type, "postgres")
        self.assertEqual(
            captured,
            {
                "dbname": "app",
                "host": "localhost",
                "user": "postgres",
                "password": "secret",
                "port": 5432,
            },
        )

    def test_postgres_pg8000_fallback_connection_arguments(self) -> None:
        captured = {}
        raw_connection = object()

        def fake_connect(**kwargs):
            captured.update(kwargs)
            return raw_connection

        pg8000 = types.ModuleType("pg8000")
        pg8000_dbapi = types.ModuleType("pg8000.dbapi")
        pg8000_dbapi.connect = fake_connect
        pg8000_dbapi.Error = RuntimeError
        pg8000.dbapi = pg8000_dbapi

        with patch(
            "builtins.__import__",
            side_effect=self.fail_imports({"psycopg", "psycopg2"}),
        ):
            with patch.dict(
                sys.modules,
                {"pg8000": pg8000, "pg8000.dbapi": pg8000_dbapi},
            ):
                conn = connect(
                    "postgres",
                    database="app",
                    host="localhost",
                    user="postgres",
                    password="secret",
                    port=5432,
                )

        self.assertIs(conn.conn, raw_connection)
        self.assertEqual(conn.db_type, "postgres")
        self.assertEqual(
            captured,
            {
                "database": "app",
                "host": "localhost",
                "user": "postgres",
                "password": "secret",
                "port": 5432,
            },
        )

    def test_mysql_connection_arguments(self) -> None:
        captured = {}
        raw_connection = object()

        def fake_connect(**kwargs):
            captured.update(kwargs)
            return raw_connection

        mysql = types.ModuleType("mysql")
        mysql_connector = types.ModuleType("mysql.connector")
        mysql_connector.connect = fake_connect
        mysql_connector.Error = RuntimeError
        mysql.connector = mysql_connector

        with patch.dict(
            sys.modules,
            {"mysql": mysql, "mysql.connector": mysql_connector},
        ):
            conn = connect(
                "mysql",
                database="app",
                host="localhost",
                user="root",
                password="secret",
                port=3306,
            )

        self.assertIs(conn.conn, raw_connection)
        self.assertEqual(conn.db_type, "mysql")
        self.assertEqual(
            captured,
            {
                "database": "app",
                "host": "localhost",
                "user": "root",
                "password": "secret",
                "port": 3306,
            },
        )

    def test_database_errors_are_wrapped(self) -> None:
        conn = self.connect_sqlite()

        with self.assertRaisesRegex(EZSQLError, "EZSQL Error:"):
            conn.query("SELECT * FROM missing_table")

        conn.close()

    def test_close_errors_are_wrapped(self) -> None:
        class BadConnection:
            def close(self) -> None:
                raise sqlite3.Error("close failed")

        conn = EZConnection(BadConnection(), "sqlite")

        with self.assertRaisesRegex(EZSQLError, "close failed"):
            conn.close()

    def test_is_select_query(self) -> None:
        self.assertTrue(is_select_query("SELECT * FROM users"))
        self.assertTrue(is_select_query("   select * from users"))
        self.assertFalse(is_select_query("INSERT INTO users VALUES (1)"))

    def test_branded_import_module(self) -> None:
        branded_module = importlib.import_module("EzSQL")

        self.assertIs(branded_module.connect, connect)
        self.assertEqual(branded_module.__version__, "0.3.3")

    def fail_import(self, blocked_name: str):
        return self.fail_imports({blocked_name})

    def fail_imports(self, blocked_names):
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            for blocked_name in blocked_names:
                if name == blocked_name or name.startswith(f"{blocked_name}."):
                    raise ImportError(f"No module named {blocked_name}")

            return original_import(name, globals, locals, fromlist, level)

        return fake_import


if __name__ == "__main__":
    unittest.main()
