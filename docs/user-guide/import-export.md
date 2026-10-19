# Import/Export

## Importing books

Every import extracts metadata, a cover thumbnail, and the book's text (unless
disabled with `--no-text` / `--no-cover`). Files are stored under `files/` by
SHA-256 hash: importing the same file twice is a no-op, and the same book in a
different format is attached as an additional format.

### Individual files

```bash
book-memex import add book.pdf ~/my-library
book-memex import add ~/Downloads/book.epub ~/my-library \
    --title "My Book" \
    --authors "John Doe, Jane Roe" \
    --subjects "Programming,Python"
```

Supported formats: PDF, EPUB, MOBI/AZW3, and plaintext.

### A whole folder

```bash
book-memex import folder ~/Downloads/ebooks ~/my-library
book-memex import folder ~/Downloads ~/my-library --extensions pdf,epub,mobi
book-memex import folder ~/ebooks ~/my-library --no-recursive
book-memex import folder ~/ebooks ~/my-library --dry-run
book-memex import folder ~/ebooks ~/my-library --log-failures failed.txt
```

Recursion and resume (skip files already in the library by hash) are on by
default.

### Calibre

```bash
book-memex import calibre ~/Calibre/Library ~/my-library
book-memex import calibre ~/Calibre/Library ~/my-library --limit 100
```

### OPDS feeds, URLs, ISBNs

```bash
book-memex import opds "https://standardebooks.org/opds" ~/my-library --limit 50
book-memex import url "https://example.com/book.pdf" ~/my-library
book-memex import isbn 978-0201633610 ~/my-library     # metadata-only entry
```

ISBN lookups query Google Books and Open Library and create a book without a file.

### arkiv bundles

[arkiv](#arkiv-the-interchange-format) is the `*-memex` ecosystem's interchange
format. Importing a bundle restores books, marginalia, and reading sessions:

```bash
book-memex import arkiv ~/my-library ~/archive.zip      # note: library first
book-memex import arkiv ~/my-library ~/archive/          # directory form
book-memex import arkiv ~/my-library ~/records.jsonl.gz
```

Books are inserted or skipped by `unique_id` (existing rows are left untouched, so
local tags and personal metadata survive); marginalia and reading sessions are
inserted or skipped by UUID. Reading sessions whose book is not in the library
are reported as orphaned and skipped. Importing the same bundle twice is safe.
`--merge` is accepted for parity with other memex archives but does not change
behavior today.

## Exporting library data

All export commands take `LIBRARY_PATH OUTPUT`. Most accept `--view NAME` to
export only one [view](library-management.md#views), including the built-in
views (`favorites`, `reading`, `completed`, `unread`, `recent`, `top-rated`).

### arkiv: the interchange format

```bash
book-memex export arkiv ~/my-library ~/archive/          # directory
book-memex export arkiv ~/my-library ~/archive.zip       # single zip file
book-memex export arkiv ~/my-library ~/archive.tar.gz    # single tar.gz file
```

The bundle contains:

- `records.jsonl`: one JSON record per book, marginalia, and reading session,
  each carrying its `book-memex://` URI.
- `schema.yaml`: per-kind field documentation and live counts.
- `README.md`: a description of the bundle and the command to import it again.

The directory form is canonical; `.zip` and `.tar.gz` are the same directory
packed for sharing. Soft-deleted (archived) records are not exported.

### Single-file HTML app

```bash
book-memex export html-app ~/my-library ~/library.html
```

One portable `.html` file containing a vendored copy of sql.js, a gzipped copy of
the database (FTS tables stripped), and hash-based routing, so deep links and the
back button work. It makes no network requests and opens in any modern browser.
Archived records are excluded.

### HTML catalog

```bash
book-memex export html ~/my-library ~/catalog.html
book-memex export html ~/my-library ~/favorites.html --view favorites
book-memex export html ~/my-library ~/site/static/library.html --base-url /library --copy
book-memex export html ~/my-library ~/library.html --language en --format pdf --min-rating 4
```

A self-contained, searchable, filterable catalog that works offline. `--base-url`
sets the prefix for file links when deploying to a web server, and `--copy` copies
the referenced book files and covers next to the output. Filters: `--language`,
`--author`, `--subject`, `--format`, `--favorite`, `--min-rating`,
`--has-files/--no-files`. The catalog uses client-side filtering, not the
[search syntax](search.md).

### OPDS catalog file

```bash
book-memex export opds ~/my-library ~/opds/catalog.xml
book-memex export opds ~/my-library ~/opds/catalog.xml \
    --base-url https://example.com/opds --copy-files --copy-covers
```

An OPDS 1.2 Atom feed for e-reader apps (Foliate, KOReader, ...). With
`--copy-files --copy-covers` the output directory is self-contained and can be
served by any static file host. OPDS export currently needs the `server` extra
installed (it shares code with the live catalog served by `book-memex serve`).

### JSON and CSV

```bash
book-memex export json ~/my-library ~/backup.json
book-memex export json ~/my-library ~/backup.json --no-marginalia
book-memex export csv ~/my-library ~/catalog.csv --view favorites
```

### Goodreads and Calibre CSV

```bash
book-memex export goodreads ~/my-library ~/goodreads.csv
book-memex export calibre ~/my-library ~/calibre.csv
```

The Goodreads CSV includes title, authors, ISBN/ISBN13, rating, reading status
shelf, bookshelves (from tags), page count, publisher, and year; import it at
<https://www.goodreads.com/review/import>. The Calibre CSV includes title,
authors, author sort, publisher, date, languages, rating (0-10 scale), tags,
series, identifiers, and comments.

### ECHO archive

```bash
book-memex export echo ~/my-library ~/archive/ --owner "Your Name"
book-memex export echo ~/my-library ~/archive/ --view favorites --no-db
```

A durable, self-describing directory: a `README.md`, `books.jsonl`, an optional
copy of `library.db`, `covers/`, and `by-author/` Markdown indexes.

### A single book

```bash
book-memex book export 42                          # JSON to stdout
book-memex book export 42 -f bibtex                # BibTeX citation
book-memex book export 42 -f files -o ./exports/   # copy the book's files
book-memex note export 42 -o notes.md              # the book's marginalia
```

## Backup and restore

`lib backup` archives the library directory itself (database plus, by default,
book files and covers):

```bash
book-memex lib backup ~/my-library -o ~/backups/library.tar.gz
book-memex lib backup ~/my-library -o ~/backups/db-only.zip --db-only
book-memex lib restore ~/backups/library.tar.gz ~/restored-library
book-memex lib restore ~/backups/library.tar.gz ~/my-library --force
```

Use `lib backup` for a byte-for-byte restore of one library; use `export arkiv`
for a durable, tool-independent record of your books and annotations that other
memex tools can read.

## Use cases

### Migrating from Calibre

```bash
book-memex lib init ~/my-library
book-memex import calibre ~/Calibre/Library ~/my-library
book-memex query stats ~/my-library
book-memex lib check ~/my-library
```

### Publishing a web catalog

```bash
book-memex view create public -L ~/my-library --rating-gte 3
book-memex export html ~/my-library ~/public/catalog.html \
    --view public --base-url /books --copy
rsync -av ~/public/ user@server:/var/www/books/
```

### Data analysis

```bash
book-memex export json ~/my-library ~/data.json
book-memex query sql "SELECT language, COUNT(*) AS n FROM books GROUP BY language" ~/my-library --format csv
```

## Python API

```python
from pathlib import Path
from book_memex.library_db import Library
from book_memex.services import ExportService

lib = Library.open(Path("~/my-library").expanduser())

lib.export_arkiv(Path("archive.zip"))
lib.export_html_app(Path("library.html"))

export_svc = ExportService(lib.session, lib.library_path)
books = lib.query().filter_by_language("en").all()
Path("backup.json").write_text(export_svc.export_json(books, pretty=True))
Path("goodreads.csv").write_text(export_svc.export_goodreads_csv(books))

lib.close()
```

## See also

- [CLI Reference](cli.md)
- [Library Management](library-management.md)
- [Search Syntax](search.md)
