# Library Management

How a library is laid out on disk, how to keep it healthy, and the tools for
organizing books and annotations.

## Library layout

```
my-library/
├── library.db          # SQLite database (metadata, marginalia, sessions, FTS5 indexes)
├── files/              # ebook files, stored by SHA-256 hash prefix
│   └── 13/13778420....epub
└── covers/             # cover images
    └── thumbnails/
```

`library.db` holds the books and their authors, subjects, identifiers, files,
covers, tags, personal metadata (rating, favorite, reading status, progress),
reviews, marginalia, reading sessions, views, and per-segment book content
(`book_content`), plus two FTS5 indexes: `books_fts` (metadata and extracted text)
and `book_content_fts` (segments).

## Lifecycle and maintenance

```bash
book-memex lib init ~/my-library               # create
book-memex lib migrate ~/my-library --check    # list pending schema migrations
book-memex lib migrate ~/my-library            # apply them (also done on open)
book-memex lib check ~/my-library              # missing/orphan files, hash mismatches
book-memex lib check ~/my-library --fix        # remove orphan DB entries
book-memex lib check ~/my-library --identity   # durable-ID drift report
book-memex lib backup ~/my-library -o backup.tar.gz
book-memex lib restore backup.tar.gz ~/restored-library
```

Migrations run automatically whenever a library is opened, so `lib migrate` is
mostly useful for checking the schema version.

### Rebuilding indexes

```bash
book-memex reindex-metadata --all -L ~/my-library   # books_fts (title/description)
book-memex reindex-content --all -L ~/my-library    # book_content segments
book-memex extract 42 -L ~/my-library               # re-run the segment extractor for one book
```

## Durable IDs and URIs

Every book has a stable `unique_id` produced by a canonical generator (check for
drift with `lib check --identity`), and marginalia and reading sessions have UUIDs. These IDs survive re-imports and arkiv round trips, so
references to them stay valid:

```
book-memex://book/<unique_id>
book-memex://marginalia/<uuid>
book-memex://reading/<uuid>
```

Positions inside a book are URI fragments on the book, not separate records:
`#epubcfi(...)` for EPUB locations, `#page=47` for PDF pages.

## Soft delete

Deleting is non-destructive by default. `book-memex book delete 42` sets the
book's `archived_at` timestamp: it disappears from default listings and
searches and is left out of arkiv and HTML-app exports, but its files, reading sessions, ratings, identifiers, and marginalia
are kept, and its URI still resolves (for example through the MCP `get_record`
tool). Physical removal is opt-in:

```bash
book-memex book delete 42                  # archive (soft delete)
book-memex book delete 42 --hard           # remove the row and its children
book-memex book delete 42 --delete-files   # remove the row and unlink files
```

!!! note
    `book delete` only finds active books, so an already-archived book cannot
    currently be hard-deleted with `book delete --hard`. Decide on `--hard` up
    front, or use the REST API (`DELETE /api/books/{id}?hard=true`), which does
    find archived books.

Marginalia and reading sessions follow the same rule through the REST API and
MCP tools (archive by default, `hard=true` to delete, plus `restore`).

`book-memex book purge` is different: it is a bulk, physical delete by filter
criteria, and it is a dry run unless you pass `--execute`.

## Tags

Tags are hierarchical, slash-separated paths, separate from the subjects that come
from book metadata:

```bash
book-memex tag add 42 Work/Projects/2024 ~/my-library -d "2024 project books"
book-memex tag tree ~/my-library
book-memex tag list ~/my-library -t Work -s     # Work and everything under it
book-memex tag rename Work/Old Work/Archive ~/my-library
book-memex tag delete Work/Archive ~/my-library -r
book-memex tag stats ~/my-library
```

`book-memex book tag 42 --tags "to-read,programming"` manages simple personal tags
on a single book.

## Views

Views are named, composable subsets of the library, evaluated live. They can be
defined from simple filters, a read-only SQL query, or a YAML definition using the
views DSL (selectors, set operations, transforms, ordering). Views never modify
books; per-view overrides (`view set`) change only how a book appears inside that
view.

```bash
book-memex view create python -L ~/my-library --subject Python
book-memex view create best -L ~/my-library --rating-gte 4 --description "My best books"
book-memex view create english -L ~/my-library --sql "SELECT id FROM books WHERE language = 'en'"
book-memex view create complex -L ~/my-library --from-file my-view.yaml

book-memex view list -L ~/my-library
book-memex view show python -L ~/my-library --limit 50
book-memex view add python 42 -L ~/my-library
book-memex view set python 42 -L ~/my-library --title "Better Title" --position 1
book-memex view export python -L ~/my-library -o python.yaml
```

Built-in views are always available and their names are reserved: `all`,
`favorites`, `reading`, `completed`, `unread`, `recent`, `top-rated`.
Use `--view NAME` on `query list` and on most `export` commands to work with one
view.

## Personal metadata and the reading queue

```bash
book-memex book rate 42 --rating 4.5
book-memex book favorite 42
book-memex book status 42 --set reading
book-memex book progress 42 --set 60
book-memex book review add 42 -c "Key points: ..." --type summary

book-memex queue add 42 --position 1
book-memex queue list
book-memex queue move 42 3
book-memex queue next
```

## Marginalia

Marginalia are free-form notes and highlights. Each one has a UUID and URI and is
classified by what it is attached to:

| Scope | Attached to |
|-------|-------------|
| `highlight` | one book, with a location (page or position) |
| `book_note` | one book, no location |
| `cross_book_note` | two or more books |
| `collection_note` | no book |

```bash
book-memex note add 42 --content "Great explanation of recursion"
book-memex note add 42 --highlight "To iterate is human" --content "Nice line" --page 12
book-memex note add 0 --content "Find a good intro to category theory" --category wishlist
book-memex note list 42
book-memex note extract 42          # import annotations embedded in the PDF/EPUB
book-memex note export 42 -f json -o notes.json
```

Highlights made in the [browser reader](server.md#browser-reader) are stored as
marginalia too. Cross-book notes, editing, archiving, and restoring are available
through the REST API and the [MCP tools](../integrations/mcp.md).

## See also

- [CLI Reference](cli.md)
- [Import/Export](import-export.md)
- [Batch Operations](../advanced/batch-operations.md)
