# book-memex

**book-memex** is a local-first eBook library manager and the book-domain archive of
the `*-memex` personal-data ecosystem. It stores book metadata, per-segment book
content, reading marginalia (highlights and notes), and reading sessions in a
SQLite database with FTS5 full-text search, and exposes them through a CLI, a
Python API, a web server with a browser-based EPUB/PDF reader, and an MCP server
for LLM clients.

!!! note "Renamed from ebk"
    This project was previously called `ebk`. The package is now `book_memex`
    and the console script is `book-memex`. A legacy `ebk` command is still
    installed as a deprecation shim that forwards to `book-memex`; it will be
    removed after v1. The configuration file keeps its old location
    (`~/.config/ebk/config.json`) for backward compatibility.

## Part of the memex ecosystem

Each `*-memex` archive covers one domain (chat logs, mail, bookmarks, photos,
books, ...) and satisfies a common contract: SQLite + FTS5 storage, an MCP server
with `execute_sql` and `get_schema`, a thin admin CLI, arkiv export, durable
record IDs, and marginalia. book-memex is deliberately narrow: it stores and
exposes books and reading data. It does **not** compute embeddings, build
knowledge graphs across archives, or wrap LLM calls; that work belongs to the
`memex` federation layer, which consumes this archive's RAG-ready MCP surface
(per-segment FTS5 search, segment retrieval, and URI resolution).

Records are addressable by URI:

```
book-memex://book/<unique_id>
book-memex://marginalia/<uuid>
book-memex://reading/<uuid>
book-memex://book/<unique_id>#page=47        (a position within a book)
```

## Features

- **SQLite + FTS5 backend** with a normalized SQLAlchemy schema: full-text search
  over titles, descriptions, and extracted text, plus a per-segment
  (`book_content`) index for chapter/page level search.
- **Hash-based deduplication**: the same file is skipped; the same book in a
  different format is added as an additional format.
- **Metadata and cover extraction** from EPUB, PDF, MOBI/AZW3, plaintext, and
  Calibre libraries.
- **Organization**: hierarchical tags (`Work/Projects/2024`), composable named
  views, a reading queue, ratings, favorites, reading status and progress, and
  structured reviews.
- **Marginalia and reading sessions**: URI-addressable highlights and notes
  (attached to zero, one, or many books) and reading sessions with start/end
  anchors.
- **Soft delete**: deleting a book or marginalia archives it by default so its
  URI keeps resolving; hard delete is opt-in.
- **Web server and reader**: a FastAPI REST API, an OPDS catalog, and a browser
  reader at `/read/{book_id}` for EPUB and PDF with highlight capture and
  progress sync. The reader libraries are vendored, so no CDN is needed.
- **MCP server**: read-only SQL, schema introspection, batch metadata updates,
  URI resolution (`get_record`, `get_record_kinds`), content search, and
  marginalia / reading-session tools.
- **Import and export**: import from files, folders, Calibre, OPDS feeds, URLs,
  ISBN lookups, and arkiv bundles; export to arkiv, a single-file HTML app, an
  HTML catalog, OPDS, JSON, CSV, Goodreads CSV, Calibre CSV, and ECHO archives.

## Quick example

```bash
book-memex lib init ~/books
book-memex import add ~/Downloads/book.epub ~/books
book-memex import folder ~/Downloads/ebooks ~/books
book-memex query search "title:python rating:>=4" ~/books
book-memex book rate 1 ~/books --rating 5
book-memex serve ~/books          # web UI at http://127.0.0.1:8000, reader at /read/1
book-memex mcp-serve ~/books      # MCP server over stdio
```

```python
from pathlib import Path
from book_memex.library_db import Library

lib = Library.open(Path("~/books").expanduser())

python_books = (lib.query()
    .filter_by_subject("Python")
    .filter_by_language("en")
    .filter_by_rating(4)
    .order_by("title")
    .limit(20)
    .all())

results = lib.search("title:python rating:>=4")
lib.close()
```

## Where to go next

1. **[Installation](getting-started/installation.md)**: install book-memex and its optional extras.
2. **[Quick Start](getting-started/quickstart.md)**: create a library and import books.
3. **[Configuration](getting-started/configuration.md)**: set a default library path and server defaults.
4. **[CLI Reference](user-guide/cli.md)**: every command group and subcommand.
5. **[MCP Server](integrations/mcp.md)**: connect an LLM client to your library.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ CLI (Typer + Rich) │ Web server + reader (FastAPI) │ MCP     │
├──────────────────────────────────────────────────────────────┤
│                       Services layer                         │
│ Import │ Export │ PersonalMetadata │ Marginalia │ ReadingSession│
│ Views  │ Queue  │ Tags │ ContentIndexer │ text/content extraction│
├──────────────────────────────────────────────────────────────┤
│          Core library (Library, QueryBuilder, URIs)          │
├──────────────────────────────────────────────────────────────┤
│        SQLAlchemy ORM + SQLite + FTS5 (books_fts,            │
│        book_content_fts)                                     │
└──────────────────────────────────────────────────────────────┘
```

## Support

- [GitHub Issues](https://github.com/queelius/book-memex/issues): bug reports and feature requests
- [Contact](mailto:lex@metafunctor.com): direct inquiries
