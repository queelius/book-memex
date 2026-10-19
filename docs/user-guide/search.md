# Search & Query

book-memex provides powerful search capabilities with field-specific queries, boolean logic, and full-text search powered by SQLite FTS5.

## Quick Start

```bash
# Simple full-text search
book-memex query search "machine learning" ~/my-library

# Field-specific search
book-memex query search "title:Python rating:>=4" ~/my-library

# Multiple criteria
book-memex query search "author:Knuth format:pdf" ~/my-library
```

## Advanced Search Syntax

### Field-Specific Searches

Search within specific fields using `field:value` syntax:

| Field | Description | Example |
|-------|-------------|---------|
| `title:` | Search in book titles | `title:Python` |
| `author:` | Search by author name | `author:Knuth` |
| `tag:` or `subject:` | Search subjects/tags | `tag:programming` |
| `description:` | Search in book descriptions | `description:algorithms` |
| `text:` | Search in extracted text | `text:recursion` |

**Examples:**

```bash
# Books with "intelligence" in the title
book-memex query search "title:intelligence" ~/my-library

# Books by Donald Knuth
book-memex query search "author:Knuth" ~/my-library

# Books tagged with "programming"
book-memex query search "tag:programming" ~/my-library

# Search book descriptions for "algorithm"
book-memex query search "description:algorithm" ~/my-library
```

### Filter Fields

Apply exact filters using the same syntax:

| Filter | Description | Example |
|--------|-------------|---------|
| `language:` | Filter by language code | `language:en` |
| `format:` | Filter by file format | `format:pdf` |
| `rating:` | Filter by rating (with operators) | `rating:>=4` |
| `favorite:` | Filter favorites only | `favorite:true` |
| `status:` | Filter by reading status | `status:reading` |
| `series:` | Exact series name | `series:TAOCP` |
| `publisher:` | Exact publisher | `publisher:"MIT Press"` |

Aliases: `tag:`/`tags:`/`subjects:` mean `subject:`, `lang:` means `language:`,
and `fmt:`/`type:` mean `format:`.

**Examples:**

```bash
# English books only
book-memex query search "python language:en" ~/my-library

# PDF files only
book-memex query search "algorithms format:pdf" ~/my-library

# Books rated 4 stars or higher
book-memex query search "title:learning rating:>=4" ~/my-library

# Favorite books
book-memex query search "programming favorite:true" ~/my-library
```

### Rating Comparisons

The `rating:` filter supports comparison operators:

```bash
rating:5           # Exactly 5 stars
rating:>=4         # 4 stars or higher
rating:>3          # Greater than 3 stars
rating:<4          # Less than 4 stars
rating:3-5         # Between 3 and 5 stars (range)
```

**Examples:**

```bash
# Highly rated Python books
book-memex query search "title:Python rating:>=4" ~/my-library

# Books rated between 3 and 4 stars
book-memex query search "rating:3-4" ~/my-library
```

### Boolean Operators

Combine search terms with boolean logic:

| Operator | Behavior | Example |
|----------|----------|---------|
| (space) | Implicit AND | `python programming` |
| `OR` | Explicit OR | `python OR java` |
| `NOT` | Exclude term | `programming NOT java` |
| `-` prefix | Exclude (shorthand) | `programming -java` |

**Examples:**

```bash
# Books about both Python AND machine learning
book-memex query search "python machine learning" ~/my-library

# Books about Python OR JavaScript
book-memex query search "python OR javascript" ~/my-library

# Programming books excluding Java
book-memex query search "programming NOT java" ~/my-library

# Same as above, using shorthand
book-memex query search "programming -java" ~/my-library
```

### Phrase Searches

Use quotes for exact phrase matching:

```bash
# Exact phrase
book-memex query search '"machine learning"' ~/my-library

# Phrase in specific field
book-memex query search 'title:"deep learning"' ~/my-library

# Phrase with filters
book-memex query search '"artificial intelligence" language:en format:pdf' ~/my-library
```

### Combined Queries

Mix field searches, filters, and boolean logic:

```bash
# Python books, 4+ stars, PDF format
book-memex query search "title:Python rating:>=4 format:pdf" ~/my-library

# Books by Knuth in his TAOCP series
book-memex query search "author:Knuth series:TAOCP" ~/my-library

# Favorite programming books (not Java)
book-memex query search "tag:programming favorite:true NOT java" ~/my-library

# Machine learning books in English, highly rated
book-memex query search '"machine learning" language:en rating:>=4' ~/my-library
```

## Full-Text Search (FTS5)

book-memex uses SQLite FTS5 for fast full-text indexing across:

- **Book titles**
- **Descriptions**
- **Extracted text** from PDFs, EPUBs, and plaintext files

The FTS5 engine provides:

- **Porter stemming**: Searches for "running" also match "run", "runs", etc.
- **Unicode support**: Full support for international characters
- **Ranking**: Results ordered by relevance
- **Fast performance**: Indexed searches even on large libraries

`author:` and `subject:` are matched with SQL joins rather than FTS (authors and
subjects are not in the FTS table), and the filter fields become SQL conditions.

!!! note "Keeping `books_fts` current"
    The metadata index (`books_fts`) is filled when a book's text is extracted at
    import time. A book imported with `--no-text`, or one whose text extraction
    produced nothing, has no `books_fts` row, so plain-text and `title:` searches
    will not find it (filter-only queries such as `author:` still do). Run
    `book-memex reindex-metadata --all -L ~/my-library` to rebuild the index.

## Content search (per segment)

Separately from `books_fts`, every imported book's text is split into
segments (EPUB chapters, PDF pages, or a whole plaintext file) stored in
`book_content` and indexed in `book_content_fts`. Content search returns ranked
snippets with an anchor (EPUB CFI, PDF page, or text offset) and a ready-made URI
fragment such as `book-memex://book/<unique_id>#page=47`.

- REST: `GET /api/books/{book_id}/search?q=...` (one book) and
  `GET /api/search/content?q=...` (whole library).
- MCP: `search_book_content`, `search_library_content`, `get_segment`, and
  `get_segments` (see [MCP Server](../integrations/mcp.md)).
- Rebuild with `book-memex reindex-content --all -L ~/my-library`, or for one
  book with `--book ID`.

## Raw SQL

For anything the search syntax cannot express, `query sql` runs a read-only
`SELECT` against the database:

```bash
book-memex query sql "SELECT title, language FROM books WHERE language = 'en'" ~/my-library
book-memex query sql "SELECT COUNT(*) AS n FROM books" ~/my-library --format json
```

## Search in Different Contexts

### CLI Search

```bash
# Basic search
book-memex query search "query" ~/my-library

# Limit results
book-memex query search "query" ~/my-library --limit 20

# Next page
book-memex query search "query" ~/my-library --limit 20 --offset 20
```

### Web Server Search

The web server (`book-memex serve`) exposes the same parser over REST:

```bash
# Start server
book-memex serve ~/my-library

# Search via API
curl -G "http://127.0.0.1:8000/api/search" --data-urlencode "q=title:Python rating:>=4"
```

The library UI's search box uses the same syntax.

### Python API

```python
from pathlib import Path
from book_memex.library_db import Library

lib = Library.open(Path("~/my-library").expanduser())

# Simple search
results = lib.search("machine learning", limit=50)

# Advanced search
results = lib.search("title:Python rating:>=4 format:pdf", limit=50)

for book in results:
    print(f"{book.title} by {', '.join(a.name for a in book.authors)}")

lib.close()
```

## Search Limitations

**HTML Export**: The exported HTML files use **client-side JavaScript filtering**, not the advanced search parser. For advanced search features, use:

- CLI: `book-memex query search`
- Web server: `book-memex serve`
- Python API: `Library.search()`

## Tips and Best Practices

1. **Start broad, refine**: Begin with simple queries, then add filters
2. **Use field searches**: More precise than full-text when you know what field to search
3. **Combine filters**: Multiple filters are ANDed together by default
4. **Quote phrases**: Always quote multi-word phrases for exact matching
5. **Test queries**: Use `--limit 5` when testing complex queries

## See Also

- [CLI Reference](cli.md) - Full command documentation
- [Web Server and Reader](server.md) - REST search endpoints
- [MCP Server](../integrations/mcp.md) - content search tools
