# Architecture

## Principles

1. **Thin domain archive.** book-memex stores and exposes books and reading data.
   Embeddings, cross-archive graphs, trails, and LLM orchestration belong to the
   `memex` federation layer, not here.
2. **SQLAlchemy + SQLite + FTS5.** A normalized schema in one `library.db`, with
   two FTS5 indexes.
3. **Thin routers, fat services.** `cli.py` and `server.py` delegate to
   `services/`; the MCP tools in `mcp/tools.py` sit on the same services.
4. **Durable identity.** Books have a canonical `unique_id`; marginalia and
   reading sessions have UUIDs; all are addressable as `book-memex://` URIs.
5. **Soft delete.** Record tables carry `archived_at`; deletes archive by default.

## Package layout (`book_memex/`)

| Module | Role |
|--------|------|
| `cli.py` | Typer CLI (`book-memex <group> <command>`). |
| `_ebk_alias.py` | Legacy `ebk` entry point: deprecation notice, then forwards to the CLI. |
| `library_db.py` | `Library` (open, add, search, query, personal data, arkiv) and the fluent `QueryBuilder`. |
| `server.py` | FastAPI app: REST endpoints, library UI, `/read/{book_id}` reader shell. |
| `server/static/`, `server/templates/` | Reader assets (`reader.js`, `reader.css`, vendored EPUB.js / JSZip / PDF.js). |
| `opds.py` | Live OPDS 1.2 catalog router mounted at `/opds`. |
| `mcp/` | `server.py` (FastMCP tool registration), `tools.py` (`*_impl` functions), `sql_executor.py` (read-only SQL). |
| `config.py` | Configuration dataclasses; reads `~/.config/ebk/config.json`. |
| `search_parser.py` | Field / boolean / comparison search syntax compiled to FTS5 + SQL. |
| `ident.py` | Canonical `unique_id` generation. |
| `extract_metadata.py`, `calibre_import.py` | Metadata extraction and Calibre import. |
| `core/` | DB-free helpers: `uri.py` (build/parse URIs), `soft_delete.py` (`filter_active`, `archive`, `restore`, `hard_delete`), `fts.py` (`safe_fts_query`). |
| `db/` | `models.py` (ORM), `session.py` (init, FTS5 setup), `migrations.py` (schema version 12). |
| `services/` | Domain operations (see below). |
| `exports/` | `arkiv.py`, `html_app.py`, `html_library.py`, `opds_export.py`, `echo_export.py`, and helpers. |
| `views/` | Views DSL (`dsl.py`) and `ViewService` (`service.py`). |
| `similarity/` | Book-similarity extractors, metrics, and `BookSimilarity` (optional `similarity` extra). |

### Services

- `import_service`: imports with hash-based deduplication, metadata, and covers.
- `text_extraction`: full-file text (PyMuPDF with a pypdf fallback, ebooklib, plaintext).
- `content_extraction/{epub,pdf,txt}.py` + `content_indexer`: per-segment
  extraction into `book_content`, maintaining `book_content_fts`.
- `annotation_extraction`: imports highlights/notes embedded in PDF/EPUB files.
- `marginalia_service`, `reading_session_service`, `personal_metadata_service`,
  `tag_service`, `queue_service`, `view_service`, `export_service`,
  `arkiv_import`.

## Data model

Core tables: `books`, `authors`, `subjects`, `contributors`, `identifiers`,
`files`, `covers`, `tags` (hierarchical), `personal_metadata` (rating, favorite,
reading status, `reading_progress`, `progress_anchor`), `reviews`, `marginalia`
(+ `marginalia_books`), `reading_sessions`, `book_content` (per-segment text with
`segment_type`, `segment_index`, and a JSON `anchor`), `views` / `view_overrides`,
`extracted_texts`, and the migration log `schema_versions`. The
`concepts` / `book_concepts` / `concept_relations` tables are a legacy knowledge-graph
schema flagged to move to the federation layer.

Full-text search:

- **`books_fts`**: title, description, and extracted text (truncated). Drives
  `Library.search()`, `query search`, and `/api/search`. It is written when text
  is extracted and on `reindex-metadata`.
- **`book_content_fts`**: an external-content FTS5 table over `book_content`.
  Drives the content-search REST endpoints and MCP tools; rebuilt by
  `reindex-content`.

Migrations are idempotent functions in `db/migrations.py`, recorded in
`schema_versions`, and run automatically on `Library.open()`.

## Surfaces

- **CLI** for imports, exports, and housekeeping.
- **REST + reader** (`book-memex serve`), loopback-only unless `--allow-remote`.
- **MCP** (`book-memex mcp-serve`), the LLM-facing query surface: read-only SQL,
  schema, URI resolution, content search, and marginalia/reading CRUD.

## Design patterns

### Fluent query API

```python
results = (lib.query()
    .filter_by_language("en")
    .filter_by_author("Knuth")
    .order_by("title")
    .limit(20)
    .all())
```

### Hash-based deduplication

Files are hashed with SHA-256 and stored as `files/<prefix>/<hash>.<ext>`. The same
file is skipped; the same book in another format becomes an additional `File`.

### URIs and fragments

Records get URI kinds (`book`, `marginalia`, `reading`); positions within a book
are fragments on the book URI (`#epubcfi(...)`, `#page=47`). Content-search hits
come with a ready-made fragment.

### Configuration hierarchy

Command-line options override the config file, which overrides built-in defaults.

## Key technologies

SQLAlchemy, SQLite FTS5, FastAPI, Typer + Rich, PyMuPDF / pypdf, ebooklib,
Pillow, FastMCP (`mcp`), EPUB.js, PDF.js, sql.js (HTML app export), and the
`arkiv` package for bundle I/O.

## Extension points

1. **Export formats**: add a module under `book_memex/exports/` and a command in
   the `export` group.
2. **Content extractors**: add an adapter under `services/content_extraction/`.
3. **MCP tools**: add an `*_impl` in `mcp/tools.py` and register it in
   `mcp/server.py`; keep REST and MCP in parity.

## See also

- [Contributing Guide](contributing.md)
- [API Reference](api-reference.md)
- Source code on [GitHub](https://github.com/queelius/book-memex)
