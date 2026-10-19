# CLI Reference

The CLI is a tree of command groups: `book-memex <group> <command> [ARGS] [OPTIONS]`.
This page summarizes every command; `book-memex <group> <command> --help` is the
authoritative source for options.

!!! note "Library path argument"
    Most commands take the library directory as a positional argument. Where the
    signature shows `[LIBRARY_PATH]` (in brackets) it is optional and falls back
    to `library.default_path` from the [configuration](../getting-started/configuration.md).
    Where it shows `LIBRARY_PATH` without brackets it is required. The `view`
    commands and the content-indexing commands take the library as an option
    (`--library` / `--library-path`, short `-L`) instead.

The legacy `ebk` command forwards to `book-memex` with a deprecation notice.

## Global options

```bash
book-memex --help          # list command groups
book-memex --verbose ...   # (-v) verbose logging for any command
book-memex --install-completion
```

## Top-level commands

| Command | Purpose |
|---------|---------|
| `book-memex about` | Show a summary of features and commands. |
| `book-memex config [OPTIONS]` | View or edit configuration (see [Configuration](../getting-started/configuration.md)). |
| `book-memex serve [LIBRARY_PATH]` | Start the web server and browser reader (see [Web Server](server.md)). |
| `book-memex mcp-serve [LIBRARY_PATH]` | Start the MCP server over stdio (see [MCP Server](../integrations/mcp.md)). |
| `book-memex extract BOOK_ID -L LIB` | Run the per-segment content extractor on one book's primary file. |
| `book-memex reindex-content (--book ID or --all) -L LIB` | Re-extract segment content (`book_content` / `book_content_fts`). |
| `book-memex reindex-metadata (--book ID or --all) -L LIB` | Rebuild the `books_fts` metadata index (title/description). |

`serve` options: `--host`, `--port`, `--reload`, `--no-open`, `--allow-remote`.

## `lib`: library lifecycle

| Command | Purpose |
|---------|---------|
| `lib init LIBRARY_PATH` | Create a new library (`library.db`, `files/`, `covers/`). |
| `lib migrate [LIBRARY_PATH]` | Apply pending schema migrations. `--check` lists pending ones, `--version` shows the schema version. |
| `lib backup [LIBRARY_PATH] -o FILE` | Write a `.tar.gz` or `.zip` backup. `--db-only` skips book files, `--no-covers` skips covers. |
| `lib restore BACKUP_FILE LIBRARY_PATH` | Restore a backup into a (new) library directory. `--force` overwrites. |
| `lib check [LIBRARY_PATH]` | Report missing files, orphan files, books without files, and hash mismatches. `--fix` removes orphan DB entries; `--identity` reports books whose stored `unique_id` no longer matches the canonical generator. |

```bash
book-memex lib init ~/my-library
book-memex lib backup ~/my-library -o ~/backup.tar.gz
book-memex lib check ~/my-library --identity
```

## `import`: bring books in

| Command | Purpose |
|---------|---------|
| `import add FILE_PATH [LIBRARY_PATH]` | Import one ebook. `--title`, `--authors` (comma-separated), `--subjects`, `--language`, `--no-text`, `--no-cover`, `--no-auto-metadata`. |
| `import folder FOLDER_PATH [LIBRARY_PATH]` | Batch import. `--no-recursive`, `--extensions pdf,epub,...`, `--limit`, `--dry-run`, `--no-resume`, `--log-failures FILE`, `--no-text`, `--no-cover`. |
| `import calibre CALIBRE_PATH LIBRARY_PATH` | Import a Calibre library (reads `metadata.opf`). `--limit`. |
| `import opds OPDS_URL [LIBRARY_PATH]` | Import from an OPDS catalog feed. `--limit/-n`. |
| `import url URL [LIBRARY_PATH]` | Download and import an ebook. |
| `import isbn ISBN [LIBRARY_PATH]` | Create a metadata-only entry from Google Books / Open Library. |
| `import arkiv LIBRARY_PATH BUNDLE_PATH` | Import an arkiv bundle (directory, `.zip`, `.tar.gz`, `.tgz`, `.jsonl`, `.jsonl.gz`). Duplicate-safe; `--merge` is accepted for ecosystem parity. |

Note the argument order of `import arkiv`: library first, then bundle.

## `export`: write the library out

All export commands take `LIBRARY_PATH OUTPUT` (both required).

| Command | Output |
|---------|--------|
| `export arkiv LIB OUT` | arkiv bundle: a directory, or a single `.zip` / `.tar.gz` / `.tgz` file, containing `records.jsonl`, `schema.yaml`, `README.md`. |
| `export html-app LIB OUT` | Single-file HTML SPA with vendored sql.js, a gzipped database, and hash routing; works offline. |
| `export html LIB OUT` | Self-contained HTML catalog. `--base-url`, `--copy`, `--view`, `--language`, `--author`, `--subject`, `--format`, `--no-files`, `--favorite`, `--min-rating`, `--no-stats`. |
| `export opds LIB OUT` | OPDS 1.2 catalog file. `--title`, `--subtitle`, `--base-url`, `--copy-files`, `--copy-covers`, plus the same filters as `html`. |
| `export json LIB OUT` | JSON metadata. `--no-marginalia`, `--view`. |
| `export csv LIB OUT` | CSV metadata. `--view`. |
| `export goodreads LIB OUT` | Goodreads-importable CSV. `--view`. |
| `export calibre LIB OUT` | Calibre-compatible CSV. `--view`. |
| `export echo LIB OUT_DIR` | ECHO-style durable archive directory. `--view`, `--no-db`, `--owner`. |

See [Import/Export](import-export.md) for details.

## `book`: per-book operations

| Command | Purpose |
|---------|---------|
| `book info BOOK_ID [LIB]` | Show details. `--format table/json`. |
| `book status BOOK_ID [LIB]` | Show, or `--set unread/reading/completed`, the reading status. |
| `book progress BOOK_ID [LIB]` | Show, or `--set 0-100`, reading progress. |
| `book rate BOOK_ID [LIB] --rating N` | Rate 0-5 stars. |
| `book favorite BOOK_ID [LIB]` | Mark as favorite; `--unfavorite` to clear. |
| `book tag BOOK_ID [LIB] --tags a,b` | Add (or `--remove`) personal tags on one book. |
| `book open BOOK_ID [LIB]` | Open the file in the default application. `--format pdf`. |
| `book read BOOK_ID [LIB]` | Open the file, or `--text [--page N]` to page through extracted text in the terminal. |
| `book edit BOOK_ID [LIB]` | Edit metadata: `--title`, `--authors`, `--language`, `--publisher`, `--series`, `--series-index`, `--description`, `--add-subject`, `--remove-subject`. |
| `book delete BOOK_ID [LIB]` | Soft delete (archive) by default. `--hard` removes the row; `--delete-files` also unlinks files; `-y` skips confirmation. |
| `book merge PRIMARY_ID SECONDARY_IDS [LIB]` | Merge duplicates (`43,44,45`) into the primary. `--dry-run`, `--delete-duplicates`, `-y`. |
| `book bulk-edit [LIB]` | Select with `--ids`, `--search`, or `--view`, then set `--language`, `--publisher`, `--series`, `--add-tag`, `--remove-tag`, `--add-subject`, `--rating`, `--status`, `--favorite/--no-favorite`. `--dry-run`, `-y`. |
| `book similar BOOK_ID [LIB]` | Find similar books (needs the `similarity` extra). `--limit`, `--mode auto/balanced/metadata/sparse`, `--format`. |
| `book export BOOK_ID [LIB]` | Export one book: `-f json/bibtex/opds/files`, `-o PATH`, `--include-files`. |
| `book purge LIBRARY_PATH` | Remove books matching criteria (`--no-files`, `--no-supported-formats`, `--language`, `--format`, `--unread`, `--max-rating`, `--author`, `--subject`). Dry run unless `--execute`; `--delete-files` also removes files. |
| `book review add/list/show/edit/delete` | Structured reviews (`--content`, `--title`, `--rating`, `--type personal/summary/critique/notes`). |

```bash
book-memex book status 42 --set reading
book-memex book merge 42 43,44 --dry-run
book-memex book bulk-edit --search "author:Knuth" --add-subject "Computer Science" --dry-run
book-memex book export 42 -f bibtex
book-memex book review add 42 -c "Great book" -t "Recommended" -r 5
```

## `note`: marginalia

| Command | Purpose |
|---------|---------|
| `note add BOOK_ID [LIB] --content TEXT` | Add a note. `--highlight TEXT` (passage), `--page N`, `--category`. Use `BOOK_ID` 0 for a collection-level note. |
| `note list BOOK_ID [LIB]` | List marginalia for a book. `--category`. |
| `note extract BOOK_ID [LIB]` | Import highlights/notes embedded in the book's PDF/EPUB files. `--format pdf/epub`. |
| `note export BOOK_ID [LIB]` | Export a book's marginalia. `--format markdown/json`, `-o FILE`. |

Editing, archiving, and restoring marginalia, and cross-book notes, are available
through the [REST API](server.md) and the [MCP tools](../integrations/mcp.md).

## `tag`: hierarchical tags

All `tag` commands require the library path.

| Command | Purpose |
|---------|---------|
| `tag list LIB` | List all tags; `-t TAG` lists books with a tag, `-s` includes subtags. |
| `tag tree LIB` | Show the tag tree; `-r ROOT` for a subtree. |
| `tag add BOOK_ID TAG_PATH LIB` | Tag a book, creating the hierarchy as needed. `-d DESCRIPTION`, `-c '#hex'`. |
| `tag remove BOOK_ID TAG_PATH LIB` | Untag a book. |
| `tag rename OLD_PATH NEW_PATH LIB` | Rename a tag and all descendants. |
| `tag delete TAG_PATH LIB` | Delete a tag; `-r` with children, `-f` without confirmation. |
| `tag stats LIB` | Tag statistics; `-t TAG` for one tag. |

## `queue`: reading queue

| Command | Purpose |
|---------|---------|
| `queue list [LIB]` | Show the queue. |
| `queue add BOOK_ID [LIB]` | Append, or insert at `--position N` (1 = top). |
| `queue remove BOOK_ID [LIB]` | Remove from the queue. |
| `queue move BOOK_ID POSITION [LIB]` | Reorder. |
| `queue next [LIB]` | Show the next book. |
| `queue clear [LIB]` | Clear the queue (`-y` skips confirmation). |

## `view`: saved views

Views take the library with `--library` / `-L` (or the configured default).

| Command | Purpose |
|---------|---------|
| `view create NAME` | Create from simple filters (`--subject`, `--author`, `--language`, `--favorite`, `--status`, `--rating-gte`), from `--sql "SELECT id FROM books ..."`, or from `--from-file view.yaml`. `--description`. |
| `view list` | List views, including built-ins (`--no-builtin` to hide them). |
| `view show NAME` | Show books in a view (`--limit`), or `--definition` for its YAML. |
| `view add NAME BOOK_ID` / `view remove NAME BOOK_ID` | Explicitly include a book in, or remove it from, a view. |
| `view set NAME BOOK_ID` | Per-view overrides: `--title`, `--description`, `--position`. |
| `view unset NAME BOOK_ID` | Remove overrides (`--field` for one). |
| `view export NAME` / `view import FILE` | YAML round trip (`-o FILE`, `--overwrite`). |
| `view edit NAME` | Edit the YAML definition in `$EDITOR`. |
| `view delete NAME` | Delete a view (`-f` skips confirmation). |

## `query`: search and discovery

| Command | Purpose |
|---------|---------|
| `query search QUERY [LIB]` | Full-text + field search (see [Search](search.md)). `--limit/-n`, `--offset`. |
| `query list [LIB]` | List books. `--author`, `--subject`, `--language`, `--favorite`, `--status`, `--view`, `--limit`, `--offset`. |
| `query stats [LIB]` | Book, author, language, format, and reading-progress counts. |
| `query sql QUERY [LIB]` | Run a read-only `SELECT`. `--format table/json/csv`, `--limit`. |

```bash
book-memex query search "title:Python rating:>=4" ~/my-library
book-memex query list ~/my-library --view favorites
book-memex query sql "SELECT title, language FROM books WHERE language = 'en'" ~/my-library --format json
```

## See also

- [Configuration Guide](../getting-started/configuration.md)
- [Web Server and Reader](server.md)
- [Python API](api.md)
