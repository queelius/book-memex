# Python API

book-memex is a regular Python package (`book_memex`). The CLI, the web server, and
the MCP server are all thin layers over the same `Library` class and services
described here.

## Overview

- **`Library`** (`book_memex.library_db`): open a library, add books, search,
  query, and common personal-metadata operations.
- **`QueryBuilder`**: a fluent, chainable query interface returned by `lib.query()`.
- **ORM models** (`book_memex.db.models`): SQLAlchemy models such as `Book`,
  `Author`, `Subject`, `Tag`, `File`, `PersonalMetadata`, `Marginalia`,
  `ReadingSession`, `BookContent`, `View`.
- **Services** (`book_memex.services`): `PersonalMetadataService`,
  `MarginaliaService`, `ExportService`, `ImportService`, `ViewService`,
  `ReadingQueueService`, `TextExtractionService`.
- **URIs** (`book_memex.core.uri`): build and parse `book-memex://` URIs.

## Quick start

```python
from pathlib import Path
from book_memex.library_db import Library

# Library.open() creates the library if it does not exist and runs any
# pending migrations. It does not expand "~", so do that yourself.
lib = Library.open(Path("~/my-library").expanduser())

book = lib.add_book(
    Path("book.epub"),
    metadata={
        "title": "Python Programming",
        "creators": ["John Doe"],
        "subjects": ["Programming", "Python"],
        "language": "en",
    },
)
print(book.id, book.unique_id, book.uri)   # book.uri -> "book-memex://book/<unique_id>"

results = lib.search("python")

python_books = (lib.query()
    .filter_by_subject("Python")
    .filter_by_language("en")
    .order_by("title")
    .limit(10)
    .all())

stats = lib.stats()
print(f"Total books: {stats['total_books']}")

lib.close()
```

## `Library`

```python
from book_memex.library_db import Library

lib = Library.open(Path("/path/to/library"))

lib.get_book(book_id)                      # Book or None (archived books hidden unless include_archived=True)
lib.get_book_by_unique_id(unique_id)
lib.get_all_books(limit=None, offset=0)
lib.get_books_by_author("Knuth")
lib.get_books_by_subject("Algorithms")
lib.search("title:Python rating:>=4", limit=50, offset=0)
lib.stats()                                # {'total_books', 'total_authors', 'languages', 'formats', ...}

# Adding books
lib.add_book(file_path, metadata={...}, extract_text=True, extract_cover=True)
lib.add_calibre_book(Path("/calibre/Author/Book (1)/metadata.opf"))
lib.batch_import([(Path("a.pdf"), {"title": "A", "creators": ["X"]}),
                  (Path("b.epub"), {"title": "B", "creators": ["Y"]})])

# Editing and personal data
lib.add_tags(book_id, ["to-read"])        # personal tags (see TagService for hierarchical tags)
lib.remove_tags(book_id, ["to-read"])
lib.add_subject(book_id, "Algorithms")
lib.set_favorite(book_id, True)
lib.update_reading_status(book_id, "reading", progress=30)

# Reading queue
lib.add_to_queue(book_id, position=1)
lib.get_reading_queue()
lib.reorder_queue(book_id, new_position=3)
lib.remove_from_queue(book_id)

# Reviews and marginalia
lib.add_review(book_id, "Great book", title="Recommended", rating=5)
lib.get_reviews(book_id)
lib.add_marginalia(book_ids=[book_id], content="Note", highlighted_text="...", page_number=12)
lib.get_marginalia(book_id)

# Deleting (soft by default)
lib.delete_book(book_id)                   # archive: sets archived_at, URI keeps resolving
lib.delete_book(book_id, hard=True)        # remove the row (cascades children)
lib.delete_book(book_id, hard=True, delete_files=True)

# Merging and similarity
merged, deleted_ids = lib.merge_books(primary_id=1, secondary_ids=[2, 3])
lib.find_similar(book_id, top_k=10)        # needs the "similarity" extra

# arkiv round trip and the single-file HTML app
lib.export_arkiv(Path("archive.zip"))      # directory, .zip, or .tar.gz
lib.import_arkiv(Path("archive.zip"))
lib.export_html_app(Path("library.html"))

lib.close()
```

`lib.session` is the underlying SQLAlchemy session and `lib.library_path` the
library directory; services take them as constructor arguments.

## `QueryBuilder`

```python
books = (lib.query()
    .filter_by_title("Algorithms")          # substring; exact=True for exact match
    .filter_by_author("Knuth")
    .filter_by_subject("Algorithms")
    .filter_by_language("en")
    .filter_by_publisher("Addison-Wesley")
    .filter_by_format("pdf")
    .filter_by_year(1997)
    .filter_by_rating(4)                     # min_rating, optional max_rating (default 5)
    .filter_by_favorite(True)
    .filter_by_reading_status("reading")
    .filter_by_text("recursion")
    .order_by("title")                       # order_by("created_at", desc=True)
    .limit(20)
    .offset(40)
    .all())

lib.query().filter_by_language("en").count()
lib.query().filter_by_author("Knuth").first()
```

## ORM models

```python
from book_memex.db.models import Book, PersonalMetadata, Marginalia

book = lib.get_book(1)

# Scalars
book.id, book.unique_id, book.title, book.subtitle, book.language
book.publisher, book.publication_date, book.series, book.series_index
book.description, book.page_count, book.created_at, book.updated_at
book.archived_at        # None unless soft-deleted
book.uri                # "book-memex://book/<unique_id>"

# Relationships
book.authors, book.subjects, book.tags, book.files, book.covers
book.identifiers, book.contributors, book.reviews
book.marginalia, book.sessions          # Marginalia and ReadingSession rows
book.personal                           # PersonalMetadata or None

pm = book.personal
pm.rating, pm.favorite, pm.reading_status, pm.reading_progress
pm.date_started, pm.date_finished, pm.queue_position, pm.progress_anchor
```

Hierarchical tags are managed with `book_memex.services.tag_service.TagService`
(`add_tag_to_book(book, "Work/Projects")`, `get_books_with_tag(path, include_subtags=True)`,
`rename_tag`, `delete_tag`). `Tag` rows are hierarchical (`tag.name`, `tag.path` such as `Work/Projects`,
`tag.parent`, `tag.children`). `File` rows carry `path` (relative to the library),
`format`, `size_bytes`, and `file_hash` (SHA-256).

## Services

### PersonalMetadataService

```python
from book_memex.services import PersonalMetadataService

pm = PersonalMetadataService(lib.session)
pm.set_rating(book_id, 4.5)
pm.set_favorite(book_id, True)
pm.set_reading_status(book_id, "reading")      # unread, reading, read, abandoned
pm.update_progress(book_id, 45)
pm.get_favorites()
pm.get_by_status("reading")
pm.get_by_rating(4.0)
```

### MarginaliaService

```python
from book_memex.services import MarginaliaService

ms = MarginaliaService(lib.session, lib.library_path)
note = ms.create(content="Key insight", highlighted_text="...",
                 book_ids=[book_id], page_number=12)
note.uri      # "book-memex://marginalia/<uuid>"
note.scope    # "highlight" (one book + location); also book_note,
              # collection_note (no books), cross_book_note (2+ books)

ms.list_for_book(book_id, scope="highlight")
ms.get_by_uuid(note.uuid)
ms.archive(note)        # soft delete
ms.restore(note)
```

### ExportService

```python
from book_memex.services import ExportService

export_svc = ExportService(lib.session, lib.library_path)
books = lib.query().filter_by_language("en").all()

json_str = export_svc.export_json(books, pretty=True)
csv_str = export_svc.export_csv(books)
goodreads_csv = export_svc.export_goodreads_csv(books)
calibre_csv = export_svc.export_calibre_csv(books)
export_svc.export_html(books, Path("catalog.html"))
export_svc.export_opds(books, Path("catalog.xml"))
```

OPDS export currently imports FastAPI (it shares code with the server's live
OPDS catalog), so it needs the `server` extra installed.

### ViewService

Views are named, composable, non-destructive lenses over the library.

```python
from book_memex.views import ViewService

view_svc = ViewService(lib.session)

view_svc.create(
    name="loved",
    definition={
        "select": {"filter": {"favorite": True}},
        "order": {"by": "title"},
    },
    description="Books I marked as favorites",
)

view_svc.create(
    name="english-favorites",
    definition={
        "select": {
            "intersect": [
                {"view": "loved"},
                {"filter": {"language": "en"}},
            ]
        }
    },
)

view_svc.list()                         # includes built-in views
books = view_svc.evaluate("loved")      # list of TransformedBook
view_svc.count("loved")
view_svc.export_yaml("loved")
view_svc.delete("english-favorites")
```

Built-in views (`all`, `favorites`, `reading`, `completed`, `unread`, `recent`,
`top-rated`) are always available and their names are reserved, so
`create()` refuses them.

Selectors include `all`, `none`, `filter`, `ids`, `view`, `union`, `intersect`,
`difference`, and `sql`; see the docstring of `book_memex/views/dsl.py` for the
full grammar.

## URIs

```python
from book_memex.core.uri import build_book_uri, parse_uri

uri = build_book_uri(book.unique_id)       # "book-memex://book/<unique_id>"
parsed = parse_uri("book-memex://book/abc#page=47")
parsed.kind, parsed.id, parsed.fragment    # ("book", "abc", "page=47")
```

## Search

`Library.search()` accepts the same syntax as `book-memex query search`
(field searches, `OR`, `NOT`, phrases, and `rating:` comparisons); see
[Search & Query](search.md).

```python
for book in lib.search('author:Knuth rating:>=4'):
    print(book.title, ", ".join(a.name for a in book.authors))
```

## Example: a reading dashboard

```python
from pathlib import Path
from book_memex.library_db import Library
from book_memex.services import PersonalMetadataService

lib = Library.open(Path("~/library").expanduser())
pm = PersonalMetadataService(lib.session)

print("Currently reading:", len(pm.get_by_status("reading")))
print("Finished:", lib.query().filter_by_reading_status("read").count())
print("Favorites:", len(pm.get_favorites()))

lib.close()
```

## Best practices

1. Always `lib.close()` when done to release the database connection.
2. Expand `~` yourself: `Path("~/library").expanduser()`.
3. Prefer `QueryBuilder` or the services over raw SQL for writes.
4. Many fields are optional; handle `None`.

## Further reading

- [CLI Reference](cli.md)
- [Search & Query](search.md)
- [Import/Export](import-export.md)
- [API Reference](../development/api-reference.md)
