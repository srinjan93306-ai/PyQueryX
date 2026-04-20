# PyQueryX

<p>
  <img src="assets/pyqueryx-icon.svg" width="96" alt="PyQueryX icon">
</p>

PyQueryX is a friendly Python SQL toolkit that wraps DB-API drivers and keeps
common database work simple. It hides cursors, manages commits, supports
parameterized queries, and gives you config helpers for real applications.

## Install

From GitHub:

```bash
pip install "git+https://github.com/srinjan93306-ai/PyQueryX.git"
```

With optional database drivers:

```bash
pip install "PyQueryX[postgres] @ git+https://github.com/srinjan93306-ai/PyQueryX.git"
pip install "PyQueryX[mysql] @ git+https://github.com/srinjan93306-ai/PyQueryX.git"
pip install "PyQueryX[oracle] @ git+https://github.com/srinjan93306-ai/PyQueryX.git"
pip install "PyQueryX[all] @ git+https://github.com/srinjan93306-ai/PyQueryX.git"
```

After PyPI publishing:

```bash
pip install PyQueryX
pip install "PyQueryX[all]"
```

SQLite works with Python's standard library. PostgreSQL uses pure-Python
`pg8000` by default, while still supporting existing `psycopg2` or `psycopg`
installs.

## Quick Start

```python
from pyqueryx import connect

with connect("sqlite", database="test.db") as db:
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)")
    db.execute("INSERT INTO users VALUES (?, ?)", (1, "Srinjan"))

    rows = db.query("SELECT * FROM users WHERE id = ?", (1,))
    print(rows)
```

Output:

```python
[(1, "Srinjan")]
```

## Better Query Helpers

```python
db = connect("sqlite", database="app.db")

db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
db.executemany(
    "INSERT INTO users VALUES (?, ?)",
    [(1, "Srinjan"), (2, "Alex")],
)

print(db.one("SELECT name FROM users WHERE id = ?", (1,)))
print(db.scalar("SELECT COUNT(*) FROM users"))

db.close()
```

## Config Options

Use a config object:

```python
from pyqueryx import DatabaseConfig, connect_from_config

config = DatabaseConfig(
    db_type="postgres",
    database="app",
    host="localhost",
    user="postgres",
    password="secret",
    port=5432,
    timeout=10,
)

db = connect_from_config(config)
```

Use environment variables:

```bash
set PYQUERYX_DB_TYPE=sqlite
set PYQUERYX_DATABASE=app.db
```

```python
from pyqueryx import connect_from_env

db = connect_from_env()
```

Use a URL:

```python
db = connect(url="sqlite:///app.db")
db = connect(url="postgres://postgres:secret@localhost:5432/app")
db = connect(url="mysql://root:secret@localhost:3306/app")
```

## Connectivity

Supported database types:

- `sqlite`
- `postgres` or `postgresql`
- `mysql` or `myssql`
- `oracle`

Extra connection options can be passed directly:

```python
db = connect(
    "mysql",
    database="app",
    host="localhost",
    user="root",
    password="secret",
    port=3306,
    timeout=10,
    echo=True,
)
```

## Transactions

```python
with connect("sqlite", database="app.db") as db:
    with db.transaction():
        db.execute("INSERT INTO users VALUES (?, ?)", (1, "Srinjan"))
        db.execute("INSERT INTO users VALUES (?, ?)", (2, "Alex"))
```

If anything fails inside the transaction block, PyQueryX rolls back.

## Compatibility

New code should use:

```python
from pyqueryx import connect
```

These compatibility imports still work for older code:

```python
from ezsql import connect
import EzSQL
import PyQueryX
```

## Development

Run tests:

```bash
python -m unittest discover
```

Run syntax checks:

```bash
python -m compileall PyQueryX.py EzSQL.py pyqueryx ezsql tests examples
```

## Repository Artwork

Use `assets/pyqueryx-social-preview.png` as the GitHub social preview image.

## PyPI Publishing

This project includes a GitHub Actions workflow for PyPI Trusted Publishing.
Configure the trusted publisher on PyPI with these fields:

- PyPI project name: `PyQueryX`
- Owner: `srinjan93306-ai`
- Repository: `PyQueryX`
- Workflow name: `publish.yml`
- Environment name: `pypi`

Then run the `Publish` workflow manually from GitHub Actions on the `main`
branch and type `publish` when prompted.
