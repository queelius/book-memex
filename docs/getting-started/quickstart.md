# Quick Start Guide

Get a library running in a few minutes. Every command below takes the library
path explicitly; once you set a default library (step 9) most commands let you
omit it.

## 1. Create a library

```bash
book-memex lib init ~/my-library
```

This creates:

- `library.db`: the SQLite database (with FTS5 full-text indexes)
- `files/`: hash-prefixed ebook storage
- `covers/`: cover images and thumbnails

## 2. Import books

### Single file

```bash
book-memex import add book.pdf ~/my-library
book-memex import add ~/Downloads/book.epub ~/my-library --title "My Book" --authors "Some Author"
```

### A whole folder

```bash
book-memex import folder ~/Downloads/ebooks ~/my-library
book-memex import folder ~/Downloads ~/my-library --extensions pdf,epub
book-memex import folder ~/Downloads ~/my-library --dry-run      # preview only
```

### From Calibre, OPDS, a URL, or an ISBN

```bash
book-memex import calibre ~/Calibre/Library ~/my-library
book-memex import opds "https://example.com/opds/catalog.xml" ~/my-library
book-memex import url "https://example.com/book.epub" ~/my-library
book-memex import isbn 978-0201633610 ~/my-library
```

Imports extract metadata, a cover, and the book's text automatically. The text
is split into per-chapter / per-page segments and indexed for content search.

## 3. Browse your library

```bash
# List books (paginated, with filters)
book-memex query list ~/my-library
book-memex query list ~/my-library --author "Knuth" --language en
book-memex query list ~/my-library --limit 20 --offset 40

# Search (full-text plus field syntax; see the Search guide)
book-memex query search "machine learning" ~/my-library
book-memex query search "author:Knuth" ~/my-library
book-memex query search "title:Python language:en rating:>=4" ~/my-library

# Details and statistics
book-memex book info 42 ~/my-library
book-memex query stats ~/my-library
```

## 4. Organize

### Hierarchical tags

```bash
book-memex tag add 42 Work/Projects ~/my-library
book-memex tag list ~/my-library
book-memex tag tree ~/my-library
book-memex tag list ~/my-library -t Work -s     # books tagged Work or Work/*
```

### Views

Views are named, composable subsets of the library. View commands take the
library with `--library` / `-L` (or use the configured default):

```bash
book-memex view create python-favorites -L ~/my-library --subject Python --favorite
book-memex view list -L ~/my-library
book-memex view show python-favorites -L ~/my-library
```

### Reading queue

```bash
book-memex queue add 42 ~/my-library
book-memex queue list ~/my-library
book-memex queue next ~/my-library
```

## 5. Track your reading

```bash
book-memex book rate 42 ~/my-library --rating 5
book-memex book favorite 42 ~/my-library
book-memex book status 42 ~/my-library --set reading
book-memex book progress 42 ~/my-library --set 45
```

## 6. Take notes

Marginalia are notes and highlights attached to zero, one, or many books:

```bash
book-memex note add 42 ~/my-library --content "Great explanation of recursion"
book-memex note add 42 ~/my-library --highlight "To iterate is human" --content "Nice line" --page 12
book-memex note list 42 ~/my-library
book-memex note extract 42 ~/my-library      # import highlights embedded in the PDF/EPUB
```

## 7. Read in the browser

```bash
book-memex serve ~/my-library
# Library UI: http://127.0.0.1:8000
# Reader:     http://127.0.0.1:8000/read/42
```

The reader supports EPUB and PDF, captures highlights as marginalia, and syncs
reading progress back to the library. See [Web Server and Reader](../user-guide/server.md).

## 8. Export

```bash
book-memex export arkiv ~/my-library ~/archive.zip          # ecosystem interchange format
book-memex export html-app ~/my-library ~/library.html      # single-file offline app
book-memex export html ~/my-library ~/catalog.html          # static HTML catalog
book-memex export json ~/my-library ~/backup.json
book-memex export goodreads ~/my-library ~/goodreads.csv
book-memex export opds ~/my-library ~/opds/catalog.xml
```

For a full backup of the library directory (database, files, covers) use
`book-memex lib backup`:

```bash
book-memex lib backup ~/my-library -o ~/library-backup.tar.gz
```

## 9. Set a default library (optional)

```bash
book-memex config --library-path ~/my-library

# Commands whose library argument is optional now use the default:
book-memex query list
book-memex query search "Python"
book-memex query stats
```

Some commands (for example `tag`, `export`, `book purge`, `import calibre`,
`import arkiv`) always require the library path. Check `--help` for each command.

## 10. Connect an LLM client (optional)

```bash
book-memex mcp-serve ~/my-library
```

See [MCP Server](../integrations/mcp.md) for client configuration and the tool list.

## Python API

```python
from pathlib import Path
from book_memex.library_db import Library
from book_memex.services import PersonalMetadataService

lib = Library.open(Path("~/my-library").expanduser())

results = lib.search("title:Python rating:>=4")

books = (lib.query()
    .filter_by_author("Knuth")
    .filter_by_language("en")
    .order_by("title")
    .limit(10)
    .all())

pm = PersonalMetadataService(lib.session)
pm.set_rating(42, 5.0)
pm.set_reading_status(42, "reading")

lib.close()
```

## Quick reference

| Task | Command |
|------|---------|
| Create library | `book-memex lib init ~/library` |
| Import file | `book-memex import add book.pdf ~/library` |
| Import folder | `book-memex import folder ~/books ~/library` |
| List books | `book-memex query list ~/library` |
| Search | `book-memex query search "query" ~/library` |
| Book info | `book-memex book info 42 ~/library` |
| Rate book | `book-memex book rate 42 ~/library --rating 5` |
| Set status | `book-memex book status 42 ~/library --set reading` |
| Add a note | `book-memex note add 42 ~/library --content "..."` |
| Export (arkiv) | `book-memex export arkiv ~/library ~/archive.zip` |
| Web UI + reader | `book-memex serve ~/library` |
| MCP server | `book-memex mcp-serve ~/library` |

## Next steps

- [Configuration](configuration.md): customize defaults
- [CLI Reference](../user-guide/cli.md): complete command documentation
- [Python API](../user-guide/api.md): programmatic access
- [Search Syntax](../user-guide/search.md): advanced queries
- [Import/Export](../user-guide/import-export.md): data formats
