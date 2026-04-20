# Contributing

Thanks for improving `EzSQL.py`.

## Development Setup

Create and activate a virtual environment, then install the project locally:

```bash
python -m venv .venv
python -m pip install -e .
```

SQLite support requires no extra dependencies. Other database drivers are
optional:

```bash
python -m pip install -e ".[postgres]"
python -m pip install -e ".[mysql]"
python -m pip install -e ".[oracle]"
python -m pip install -e ".[all]"
```

## Run Tests

```bash
python -m unittest discover
```

## Run Syntax Checks

```bash
python -m compileall EzSQL.py ezsql tests examples
```

## Project Principles

- Keep the public API small.
- Do not expose cursors to users.
- Prefer beginner-friendly names and behavior.
- Wrap database driver errors in `EZSQLError`.
- Avoid adding dependencies unless they clearly improve the library.
