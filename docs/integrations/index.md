# Integrations

## MCP server

[MCP Server](mcp.md): connect an LLM client (Claude Code or any MCP-aware client)
to your library over stdio.

## The `*-memex` ecosystem

book-memex is the book-domain archive of the `*-memex` family of personal-data
archives (alongside, for example, `llm-memex` for AI conversations, `mail-memex`
for email, and `bookmark-memex` for bookmarks). Each archive is an independent
package that satisfies a shared contract, and the `memex` federation layer works
across them. What book-memex provides to that ecosystem:

- **Durable, URI-addressable records**: `book-memex://book/<unique_id>`,
  `book-memex://marginalia/<uuid>`, `book-memex://reading/<uuid>`. Positions
  inside a book are fragments (`#epubcfi(...)`, `#page=47`), not separate records.
- **Record resolution over MCP**: `get_record` resolves any of those URIs (archived
  records included) and `get_record_kinds` declares the kinds, tables, and id
  columns, so the federation can follow cross-archive trail steps.
- **A RAG-ready surface**: per-segment FTS5 search (`search_book_content`,
  `search_library_content`) and paginated segment text (`get_segment`,
  `get_segments`). The federation pulls text through these tools and does any
  embedding itself; the archive computes no embeddings and wraps no LLM calls.
- **arkiv interchange**: `book-memex export arkiv` writes the ecosystem's
  JSONL + `schema.yaml` bundle (as a directory, `.zip`, or `.tar.gz`), and
  `book-memex import arkiv` reads it back without clobbering local data. See
  [Import/Export](../user-guide/import-export.md#arkiv-the-interchange-format).
- **A durable offline export**: `book-memex export html-app` produces a single
  self-contained HTML file (vendored sql.js, gzipped database, hash routing).
- **Soft delete everywhere**: archived records keep their URIs until explicitly
  purged, so references held by trails and notes elsewhere stay valid.

## Other formats

- **Calibre**: `book-memex import calibre` and `book-memex export calibre`.
- **Goodreads**: `book-memex export goodreads` produces an importable CSV.
- **OPDS**: `book-memex serve` publishes a live OPDS catalog at `/opds/`;
  `book-memex import opds` and `book-memex export opds` read and write feeds.
