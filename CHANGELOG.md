# Changelog

All notable changes to this project will be documented in this file.

## 0.4.1 - 2026-04-20

- Fixed GitHub Actions package install failures by upgrading packaging tools
  and installing with `--no-build-isolation`.
- Disabled automatic PyPI publishing on GitHub release until Trusted Publishing
  is configured, preventing repeated publish-failure emails.

## 0.4.0 - 2026-04-20

- Renamed project and distribution to `PyQueryX`.
- Added new `pyqueryx` package and `PyQueryX.py` compatibility module.
- Kept `ezsql` and `EzSQL` compatibility imports for existing users.
- Added parameterized query support across `query()`, `execute()`, and
  `executemany()`.
- Added `one()`, `scalar()`, context manager support, and transaction helper.
- Added `DatabaseConfig`, `connect_from_config()`, `connect_from_env()`, and
  connection URL support.
- Added `timeout`, `autocommit`, `echo`, and driver-specific connection
  options.

## 0.3.3 - 2026-04-20

- Added PyPI Trusted Publishing workflow.
- Added PNG social preview asset.
- Modernized package license metadata.

## 0.3.2 - 2026-04-20

- Added repository artwork for README and GitHub social preview.
- Added PostgreSQL and MySQL connection argument tests.
- Added pure-Python PostgreSQL fallback support through `pg8000`.
- Verified PostgreSQL and MySQL driver installation in the local environment.

## 0.3.1 - 2026-04-20

- Updated package metadata and README links for the renamed GitHub repository.
- Added direct GitHub installation instructions for other users.
- Switched the PostgreSQL optional dependency to pure-Python `pg8000` while
  keeping compatibility with existing `psycopg2` and `psycopg` installs.

## 0.3.0 - 2026-04-20

- Renamed the distribution/project display name to `EzSQL.py`.
- Added `EzSQL.py` compatibility module for `import EzSQL`.
- Kept the recommended Python package import as `from ezsql import connect`.

## 0.2.0 - 2026-04-20

- Added MySQL support through `mysql-connector-python`.
- Added Oracle support through `oracledb`.
- Added optional package extras: `postgres`, `mysql`, `oracle`, and `all`.
- Updated README connection examples for PostgreSQL, MySQL, and Oracle.

## 0.1.0 - 2026-04-20

- Added `connect()` for SQLite and PostgreSQL.
- Added `EZConnection.query()`, `EZConnection.execute()`, and `EZConnection.close()`.
- Added automatic cursor handling and automatic commits for write queries.
- Added `EZSQLError` for clean database error wrapping.
- Added `is_select_query()` helper.
- Added project packaging metadata, README, example script, and tests.
