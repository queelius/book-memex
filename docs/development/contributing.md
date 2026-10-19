# Contributing

Contributions are welcome: bug fixes, features, documentation, and issue reports.

## Development setup

Prerequisites: Python 3.10+ and Git.

```bash
git clone https://github.com/queelius/book-memex.git
cd book-memex

make setup            # create a virtual environment and install ".[dev,all]"

# or manually:
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"          # dev pulls in the mcp, server, and similarity extras
```

## Running tests

```bash
pytest                                             # full suite
pytest tests/test_server_marginalia.py -v          # one file
make test-file FILE=tests/test_server_marginalia.py
pytest -k "marginalia or reading" -v               # keyword filter
pytest -m "not slow"                               # skip slow tests
pytest --cov=book_memex --cov-report=term-missing  # coverage
make test-coverage
```

## Code quality

```bash
make lint            # linters
make format          # black + isort
make format-check    # check formatting without changing files
```

## Building the documentation

The site is built with MkDocs (Material theme). CI builds it in strict mode, so
broken links or nav entries fail the build:

```bash
pip install "mkdocs>=1.6,<2" mkdocs-material "mkdocstrings[python]" pymdown-extensions
mkdocs build --clean --strict
mkdocs serve          # live preview at http://127.0.0.1:8000
```

Add new pages under `docs/` and list them in the `nav` section of `mkdocs.yml`.
`docs/superpowers/` holds internal design specs and plans and is intentionally
not in the nav.

## Making changes

1. Create a branch: `git checkout -b feature/my-change`.
2. Keep `cli.py` and `server.py` thin; put logic in `services/`.
3. New record tables get an `archived_at TIMESTAMP NULL` column and a migration in
   `db/migrations.py` (idempotent, bump `CURRENT_SCHEMA_VERSION`).
4. Keep REST and MCP in parity: a new REST operation should have a matching MCP
   tool, and vice versa.
5. Route user-supplied FTS5 queries through `book_memex.core.fts.safe_fts_query`.
6. Add tests, and update `docs/` for user-facing changes.
7. Open a pull request on GitHub.

### Adding a CLI command

Add the function to the relevant Typer sub-app in `book_memex/cli.py`
(`import_app`, `export_app`, `book_app`, ...), give it help text and examples,
resolve the library path with the config fallback where the argument is
optional, and document it in `docs/user-guide/cli.md`.

## Code style

- Type hints on public functions; Google-style docstrings.
- `snake_case` functions and variables, `PascalCase` classes, `UPPER_CASE` constants.
- Line length 100.

## Reporting issues

Include the book-memex version (`pip show book-memex`), Python version, OS, steps
to reproduce, expected vs. actual behavior, and any error output.

- [GitHub Issues](https://github.com/queelius/book-memex/issues)
- [Architecture](architecture.md)

## License

By contributing you agree that your contributions are licensed under the
project's MIT License.
