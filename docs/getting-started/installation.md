# Installation

## Requirements

- Python 3.10 or higher
- pip (or another PEP 517 installer such as `uv`)

## Install from source

book-memex is not yet published to PyPI under the `book-memex` name, so install it
from the GitHub repository:

```bash
git clone https://github.com/queelius/book-memex.git
cd book-memex
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -e ".[all]"          # or: pip install .  for the core only
```

This installs two console scripts:

- `book-memex`: the CLI.
- `ebk`: a legacy alias for `book-memex` that prints a deprecation notice. It
  will be removed after v1, so update scripts to call `book-memex`.

## Optional extras

The core install covers the CLI, the Python API, import, and every exporter.
Some features need extra dependencies:

| Extra | Installs | Needed for |
|-------|----------|------------|
| `server` | FastAPI, python-multipart | `book-memex serve` (REST API, OPDS catalog, browser reader) |
| `mcp` | `mcp`, pydantic | `book-memex mcp-serve` |
| `similarity` | numpy, scikit-learn | `book-memex book similar` and `Library.find_similar()` |
| `all` | `server` + `mcp` + `similarity` | everything above |
| `dev` | pytest, coverage, black, ruff, mypy, pre-commit, plus `all` | running the test suite |
| `docs` | mkdocs, mkdocs-material, mkdocstrings | building this documentation |

```bash
pip install -e ".[server]"
pip install -e ".[mcp]"
pip install -e ".[server,mcp,similarity]"
pip install -e ".[dev]"
```

`serve` itself also needs an ASGI server; if `uvicorn` is not already present in
your environment, install it with `pip install uvicorn`.

## Using the Makefile

The repository includes a Makefile for common development tasks:

```bash
make setup          # create a virtual environment and install dependencies
make test           # run the test suite
make test-coverage  # run tests with a coverage report
make format         # black + isort
make lint           # linters
make docs           # build this documentation
```

## Verifying the installation

```bash
book-memex --help
book-memex about
```

## Next steps

- Follow the [Quick Start Guide](quickstart.md) to create your first library.
- Read about [Configuration](configuration.md).
- Explore the [CLI Reference](../user-guide/cli.md).
