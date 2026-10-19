# Changelog

Project changelog and release notes. Entries before the April 2026 rename refer
to the project by its old name, `ebk`, and use the command names of that time;
many of those commands have since been renamed or removed (see the
[CLI Reference](../user-guide/cli.md) for the current surface).

## Unreleased: book-memex (2026-04 onward)

### Rename

- `ebk` was renamed to **book-memex**: package `book_memex`, console script
  `book-memex`, GitHub repository `queelius/book-memex`. The `ebk` command remains
  as a deprecation shim until after v1. The config file stays at
  `~/.config/ebk/config.json`.

### memex ecosystem integration

- URI-addressable records (`book-memex://book/...`, `.../marginalia/...`,
  `.../reading/...`) with position fragments.
- Soft delete (`archived_at`) across record tables; `book delete` archives by
  default, `--hard` opts into physical deletion.
- Marginalia (highlights, book notes, cross-book notes, collection notes) and
  reading sessions over REST and MCP.
- Per-segment content extraction (`book_content`, `book_content_fts`), content
  search endpoints and MCP tools, `extract`, `reindex-content`, and
  `reindex-metadata` commands.
- Browser EPUB/PDF reader at `/read/{book_id}` with vendored reader libraries.
- arkiv export/import (`export arkiv`, `import arkiv`) using the `arkiv` package's
  bundle I/O, and the single-file `export html-app`.
- MCP `get_record` and `get_record_kinds` (record-resolution contract), plus
  marginalia, reading, and content-search tools.
- `serve` binds loopback by default and requires `--allow-remote` otherwise.

## v0.5.1 (2026-03-13)

- Code quality fixes for the MCP module.

## v0.5.0 (2026-03-13)

- Added the MCP server (`ebk mcp-serve`) with `get_schema`, `execute_sql`, and
  `update_books`.
- Removed the AI/LLM layer (including `ebk enrich`), the interactive REPL shell,
  the VFS module, and the skills system, all superseded by MCP and the REST API.

## v0.4.5 (2026-03-10)

### Security Fixes

- **SQL injection fix in Views DSL**: Replaced bypassable keyword blocklist with defense-in-depth: read-only SQLite connections, authorizer callback whitelist (SELECT/READ/FUNCTION only), and multi-statement rejection
- **CORS restriction**: Server CORS policy restricted from wildcard (`*`) to localhost origins only, preventing cross-origin attacks on the local library API
- **Gemini API key protection**: Moved API key from URL query parameter (visible in logs/proxies) to `x-goog-api-key` header; added `LLMConfig.__repr__` with key redaction

### Bug Fixes

- **`Tag.full_path` AttributeError**: Added missing `full_path` property to Tag model, fixing export failures for tagged books
- **Circular view references**: Added cycle detection to Views DSL evaluator, preventing infinite recursion when views reference each other
- **Missing migration**: Added migration v7 for `views` and `view_overrides` tables, fixing upgrade path for existing databases

### Improvements

- Gemini provider now uses native `system_instruction` API field instead of fake user/model exchange
- Extracted `_build_payload()` in Gemini provider, eliminating duplicated payload construction
- Hoisted SQLite authorizer constants to class level for better performance
- Removed tracked backup files (`cli.py.backup`, `cli.py.grouped-backup`)

## v0.4.4 (2025-10-13)

### New Features

- **Anthropic provider**: Claude model support via `ebk/ai/llm_providers/anthropic.py`
- **Gemini provider**: Google Gemini model support via `ebk/ai/llm_providers/gemini.py`
- **Open Library integration**: Metadata lookup via Open Library API
- **Echo export**: New export format in `ebk/exports/echo_export.py`
- **CITATION.cff**: Added citation metadata file

### Improvements

- Code simplification and cleanup across CLI, decorators, and config modules
- LLM provider deduplication and shared base class improvements
- Simplified decorators module
- Documentation cleanup: removed obsolete development docs

## v0.4.3 (2025-01-03)

### New Features

- **Book Merge**: Combine duplicate book entries into one
  - `ebk book merge <primary_id> <secondary_ids>` - Merge multiple books
  - Preserves all metadata, files, covers, tags, and annotations
  - `--dry-run` to preview changes, `--delete-duplicates` to remove duplicate files

- **Bulk Edit**: Edit multiple books at once
  - `ebk book bulk-edit --ids 1,2,3 --language en --add-tag Work`
  - Select books via `--ids`, `--search`, or `--view`
  - Edit language, publisher, series, tags, subjects, rating, status, favorite

- **Goodreads Export**: Export library for Goodreads import
  - `ebk export goodreads ~/library ~/goodreads.csv`
  - Includes ratings, reading status, bookshelves (tags)
  - Import at goodreads.com/review/import

- **Calibre Export**: Export library for Calibre import
  - `ebk export calibre ~/library ~/calibre.csv`
  - Includes author_sort, identifiers, series info

### Documentation

- Complete documentation overhaul
- Removed intermediate/internal docs (phase summaries, design docs)
- Updated index.md with current features and motivation
- Rewrote quickstart guide with current CLI commands
- Comprehensive import/export guide with all formats
- Updated Python API documentation

### Improvements

- Views now support `--view` flag in all export commands
- OPDS export supports file and cover copying

## v0.3.1 (2025-01-14)

### New Features
- 🔍 **Advanced Search**: Field-specific queries with boolean logic
  - Field searches: `title:`, `author:`, `tag:`, `description:`, `text:`
  - Filter fields: `language:`, `format:`, `rating:`, `favorite:`, `status:`
  - Boolean operators: `AND` (implicit), `OR`, `NOT`/`-prefix`
  - Rating comparisons: `rating:>=4`, `rating:3-5`
  - Phrase searches: `"exact phrase"`
- 📄 **HTML Export Pagination**: 50 books per page with navigation controls
  - URL state tracking for bookmarkable pages
  - Page numbers in URL query parameters
  - Previous/Next buttons with page number links
- 📋 **Cover Copying**: `--copy` flag now copies both files AND covers

### Improvements
- Search parser with FTS5 column-specific queries (`title:term`)
- Author and subject filtering via SQL JOINs (not in FTS table)
- HTML export with URL-based state management (filters, search, page)
- Fixed `ExtractedText.content` attribute name (was incorrectly using `full_text`)
- Added missing `Library.add_subject()` method for metadata enrichment

### Bug Fixes
- Fixed `ebk enrich` command attribute error with extracted text
- Fixed HTML export `--copy` not copying cover images
- Fixed field searches not working (FTS5 column prefixes)

### Documentation
- Comprehensive search guide with all syntax and examples
- Updated README with advanced search features
- Import/export guide with pagination documentation
- Clear notes about HTML export limitations (client-side filtering only)

## v0.3.0 (2025-01-XX)

### New Features
- ✨ Configuration system at `~/.config/ebk/config.json`
- 🤖 LLM provider abstraction with Ollama support (local and remote)
- 🏷️ AI-powered metadata enrichment (tags, categories, descriptions, difficulty assessment)
- 🌐 Enhanced web server with config defaults and auto-open browser
- 📚 Complete documentation overhaul with mkdocs

### Configuration System
- Centralized configuration management with `ebk config` command
- Four configuration sections: `llm`, `server`, `cli`, `library`
- Support for default library path
- Server host, port, and auto-open browser settings
- CLI defaults for verbosity and color output

### LLM Integration
- Abstract `BaseLLMProvider` interface in `ebk/ai/llm_providers/`
- `OllamaProvider` with local and remote support
- `MetadataEnrichmentService` for intelligent metadata generation
- `ebk enrich` command with selective enrichment options
- Support for multiple models and temperature control

### Server Updates
- `ebk serve` now uses config defaults for library path, host, and port
- Optional library path argument (uses config if not specified)
- Auto-open browser feature
- REST API improvements

### Documentation
- New user guides: Configuration, LLM Features, Web Server, CLI Reference
- Updated README with quickstart and modern examples
- Deployed to GitHub Pages

### Breaking Changes
- `ebk serve` library path is now optional (uses config default)
- Some CLI options renamed for consistency (e.g., `--llm-*` prefix)

## Earlier Versions

See [GitHub Releases](https://github.com/queelius/book-memex/releases) for information about earlier versions.
