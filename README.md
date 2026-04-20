# EzSQL.py

`EzSQL.py` is a small Python library that wraps Python DB-API connections with a
simple interface. It hides cursors and routine transaction handling so beginners
can run SQL with two methods: `query()` and `execute()`.

## Installation

Install directly from GitHub:

```bash
pip install "git+https://github.com/srinjan93306-ai/EzSQL.py.git"
```

For optional database drivers from GitHub:

```bash
pip install "EzSQL.py[postgres] @ git+https://github.com/srinjan93306-ai/EzSQL.py.git"
pip install "EzSQL.py[mysql] @ git+https://github.com/srinjan93306-ai/EzSQL.py.git"
pip install "EzSQL.py[oracle] @ git+https://github.com/srinjan93306-ai/EzSQL.py.git"
pip install "EzSQL.py[all] @ git+https://github.com/srinjan93306-ai/EzSQL.py.git"
```

For local development:

```bash
pip install -e .
```

SQLite works with Python's standard library. After publishing to PyPI, these
optional extras can be installed with:

```bash
pip install "EzSQL.py[postgres]"
pip install "EzSQL.py[mysql]"
pip install "EzSQL.py[oracle]"
pip install "EzSQL.py[all]"
```

## Quick Start

```python
from ezsql import connect

conn = connect("sqlite", database="test.db")

conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'Srinjan')")

result = conn.query("SELECT * FROM users")

print(result)

conn.close()
```

Output:

```python
[(1, 'Srinjan')]
```

## API

### `connect(db_type="sqlite", database=None, host=None, user=None, password=None, port=None)`

Creates an `EZConnection`.

Supported database types:

- `"sqlite"`
- `"postgres"` or `"postgresql"`
- `"mysql"` or `"myssql"`
- `"oracle"`

SQLite creates the database file automatically when it does not already exist.
If `database` is omitted for SQLite, EzSQL.py uses an in-memory database.

For PostgreSQL and MySQL, `database` is the database name.

For Oracle, `database` can be either the service name used with `host` and
`port`, or a full DSN/Easy Connect string when `host` is omitted.

## More Connection Examples

```python
postgres = connect(
    "postgres",
    database="app",
    host="localhost",
    user="postgres",
    password="secret",
    port=5432,
)

mysql = connect(
    "mysql",
    database="app",
    host="localhost",
    user="root",
    password="secret",
    port=3306,
)

oracle = connect(
    "oracle",
    database="ORCLPDB1",
    host="localhost",
    user="hr",
    password="secret",
    port=1521,
)
```

### `EZConnection.query(sql)`

Executes SQL and returns all rows as a list of tuples. Statements with no result
return an empty list. Write statements are committed automatically.

### `EZConnection.execute(sql)`

Executes SQL and returns `None`. Use it for `CREATE TABLE`, `INSERT`, `UPDATE`,
and `DELETE`.

### `EZConnection.close()`

Closes the database connection.

## Errors

Database errors are wrapped in `EZSQLError`:

```python
from ezsql import EZSQLError

try:
    conn.query("SELECT * FROM missing_table")
except EZSQLError as error:
    print(error)
```

## Import Name

After installation, users can import the library with the stable lowercase
package name:

```python
from ezsql import connect
```

For users who prefer the branded name, this also works:

```python
import EzSQL

conn = EzSQL.connect("sqlite")
```

## Development

Run the test suite:

```bash
python -m unittest discover
```

Run a syntax check:

```bash
python -m compileall EzSQL.py ezsql tests examples
```
