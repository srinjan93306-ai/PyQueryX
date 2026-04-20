# Changelog

All notable changes to this project will be documented in this file.

## 0.3.1 - 2026-04-20

- Updated package metadata and README links for the renamed GitHub repository.
- Added direct GitHub installation instructions for other users.

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
