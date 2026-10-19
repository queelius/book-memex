# MCP Server

book-memex includes a [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) server that lets LLM clients such as Claude Code work with your library
directly. Like every `*-memex` archive, it exposes primitives (read-only SQL,
schema introspection, FTS5 content search, segment retrieval, URI resolution, and
CRUD on marginalia and reading sessions) and leaves reasoning to the client: no
tool wraps an LLM call, and the archive computes no embeddings.

It requires the `mcp` extra: `pip install -e ".[mcp]"`.

## Starting the server

```bash
book-memex mcp-serve /path/to/library
book-memex mcp-serve          # uses library.default_path from the config
```

The server speaks MCP over **stdio**. Log output goes to stderr so stdout stays a
clean JSON-RPC channel.

## Client configuration

Claude Code (`~/.claude.json` or a project-level `.mcp.json`):

```json
{
  "mcpServers": {
    "book-memex": {
      "command": "book-memex",
      "args": ["mcp-serve", "/path/to/library"]
    }
  }
}
```

If `book-memex` is not on the client's `PATH`, use the absolute path to the
script inside your virtual environment (for example
`/home/you/.venvs/memex/bin/book-memex`).

## Tools

The server registers 22 tools.

| Group | Tools |
|-------|-------|
| Database | `get_schema`, `execute_sql`, `update_books` |
| Record resolution | `get_record`, `get_record_kinds` |
| Marginalia | `list_marginalia`, `get_marginalia`, `add_marginalia`, `update_marginalia`, `delete_marginalia`, `restore_marginalia` |
| Reading sessions and progress | `start_reading_session`, `end_reading_session`, `list_reading_sessions`, `delete_reading_session`, `restore_reading_session`, `get_reading_progress`, `set_reading_progress` |
| Content search and segments | `search_book_content`, `search_library_content`, `get_segment`, `get_segments` |

Tools that take a marginalia or reading-session `uuid` accept either the bare
UUID or the full `book-memex://...` URI.

### `get_schema`

Returns the database schema: tables, columns (types, nullability, primary keys),
foreign keys, and ORM relationships. Use it before writing SQL.

**Parameters:** none.

### `execute_sql`

Runs a read-only `SELECT` against the library database.

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `sql` | `str` | required | A `SELECT` statement. Use `?` positional placeholders. |
| `params` | `list` | `None` | Values for the placeholders. |
| `max_rows` | `int` | `1000` | Maximum rows returned. |

**Returns:** `{"columns": [...], "rows": [[...], ...], "row_count": N}`, with
`"truncated": true` when more rows exist, or `{"error": "..."}`.

Read-only access is enforced in three layers: the statement must start with
`SELECT` (SQLite also rejects multiple statements per call), the connection is
opened with `?mode=ro`, and a SQLite authorizer allows only `SELECT`, `READ`, and
`FUNCTION` operations.

### `update_books`

Batch metadata updates: `{book_id: {field: value, ...}, ...}`.

- **Scalar fields**: any column of `Book` or `PersonalMetadata` (for example
  `title`, `language`, `rating`, `reading_status`, `favorite`).
- **Collection operations**: `add_tags` / `remove_tags`, `add_authors` /
  `remove_authors`, `add_subjects` / `remove_subjects` (lists of strings).
- **Merge**: `{"merge_into": target_id}` merges the book into the target; it
  cannot be combined with other fields.

```json
{
  "42": {"rating": 5.0, "add_tags": ["favorites", "technical/python"]},
  "99": {"merge_into": 42}
}
```

**Returns:** `{"updated": [book_id, ...], "errors": {book_id: "message", ...}}`.

### `get_record`

Resolves a `book-memex://` URI to its record. This is the archive's
record-resolution contract tool, used by the `memex` federation to follow
cross-archive trail steps.

| Name | Type | Description |
|------|------|-------------|
| `uri` | `str` | `book-memex://book/<unique_id>`, `book-memex://marginalia/<uuid>`, or `book-memex://reading/<uuid>`. |

Archived (soft-deleted) records still resolve.

### `get_record_kinds`

Declares the URI kinds this archive resolves and the table and id column behind
each. Part of the `*-memex` archive contract; the federation's conformance checks
use it. **Parameters:** none.

```json
{"kinds": [
  {"kind": "book", "table": "books", "id_column": "unique_id"},
  {"kind": "marginalia", "table": "marginalia", "id_column": "uuid"},
  {"kind": "reading", "table": "reading_sessions", "id_column": "uuid"}
]}
```

### Marginalia tools

| Tool | Parameters | Notes |
|------|------------|-------|
| `list_marginalia` | `book_id=None`, `scope=None`, `include_archived=False`, `limit=50` | With `book_id`, that book's marginalia; without it, collection notes. `scope` is one of `highlight`, `book_note`, `collection_note`, `cross_book_note`. |
| `get_marginalia` | `uuid` | UUID or URI. |
| `add_marginalia` | `book_uris`, `content`, `highlighted_text`, `page_number`, `position`, `category`, `color`, `pinned` | Linked to zero or more books by URI. One book plus a location is a highlight; one book without a location a book note; no books a collection note; several books a cross-book note. |
| `update_marginalia` | `uuid`, `content`, `highlighted_text`, `category`, `color`, `pinned` | Only the fields you pass change. |
| `delete_marginalia` | `uuid`, `hard=False` | Archives by default; `hard=True` deletes irreversibly. |
| `restore_marginalia` | `uuid` | Clears `archived_at`. |

### Reading tools

| Tool | Parameters | Notes |
|------|------------|-------|
| `start_reading_session` | `book_id`, `start_anchor=None` | Anchor is a CFI or page dict. |
| `end_reading_session` | `uuid`, `end_anchor=None` | Idempotent. |
| `list_reading_sessions` | `book_id`, `include_archived=False`, `limit=50` | |
| `delete_reading_session` | `uuid`, `hard=False` | Archives by default. |
| `restore_reading_session` | `uuid` | |
| `get_reading_progress` | `book_id` | Anchor plus percentage. |
| `set_reading_progress` | `book_id`, `anchor`, `percentage=None`, `force=False` | Rejects backward progress unless `force=True`. |

### Content search and segment tools

These are the RAG-ready surface: they operate on the per-segment
`book_content` table (EPUB chapters, PDF pages, plaintext files).

| Tool | Parameters | Notes |
|------|------------|-------|
| `search_book_content` | `book_id`, `query`, `limit=20`, `advanced=False` | FTS5 search within one book. Returns ranked snippets, each with its anchor and a pre-built URI fragment. Queries are sanitized against FTS5 operator injection unless `advanced=True`. |
| `search_library_content` | `query`, `limit=20`, `advanced=False` | Same, across all books; hits include `book_uri`. |
| `get_segment` | `book_id`, `segment_type`, `segment_index` | One segment's full text, anchor, and extractor version. |
| `get_segments` | `book_id`, `limit=50`, `offset=0` | Paginated segments with full text, ordered by `segment_index`. |

## Architecture

The server lives in `book_memex/mcp/`:

- `server.py`: creates the FastMCP instance, registers the tools, runs stdio.
- `tools.py`: the `*_impl` tool implementations. They sit on the same service
  layer (`MarginaliaService`, `ReadingSessionService`, ...) as the REST API, so the
  two surfaces expose matching operations and serialization.
- `sql_executor.py`: `ReadOnlySQLExecutor`, the three-layer read-only SQL runner.

## See also

- [Integrations overview](index.md)
- [Architecture](../development/architecture.md)
- [CLI Reference](../user-guide/cli.md)
