# Batch Operations

Tools for working on many books at once. Most of them have a dry-run mode; use
it first.

## Bulk import

```bash
book-memex import folder ~/Books ~/my-library --dry-run
book-memex import folder ~/Books ~/my-library --extensions pdf,epub --limit 500
book-memex import folder ~/Books ~/my-library --log-failures failed.txt
```

Folder imports resume by default: files already in the library (by hash) are
skipped, so an interrupted import can simply be re-run.

## Bulk edit

Select books with `--ids`, `--search` (the [search syntax](../user-guide/search.md)),
or `--view`, then apply changes:

```bash
book-memex book bulk-edit --ids 1,2,3 --language en
book-memex book bulk-edit --search "python" --add-tag "Programming" --dry-run
book-memex book bulk-edit --search "author:Knuth" --add-subject "Computer Science"
book-memex book bulk-edit --view my-view --rating 5 -y
```

Editable fields: `--language`, `--publisher`, `--series`, `--add-tag`,
`--remove-tag`, `--add-subject`, `--rating`, `--status`, `--favorite/--no-favorite`.

## Merging duplicates

```bash
book-memex book merge 42 43 --dry-run          # preview
book-memex book merge 42 43,44,45              # merge 43, 44, 45 into 42
book-memex book merge 42 43 --delete-duplicates -y
```

The primary keeps its scalar fields (filling empty ones from the secondaries),
authors/subjects/tags are combined, files move to the primary (duplicates by hash
are skipped), and the higher rating and more advanced reading status win.

## Purging

`book purge` physically removes every book matching the criteria. It is a dry
run unless you pass `--execute`:

```bash
book-memex book purge ~/my-library --no-files
book-memex book purge ~/my-library --no-supported-formats --execute
book-memex book purge ~/my-library --unread --max-rating 2 --execute --delete-files
```

For reversible removal of individual books use `book delete` (a soft delete).

## Rebuilding indexes

```bash
book-memex reindex-metadata --all -L ~/my-library
book-memex reindex-content --all -L ~/my-library
```

## Batch updates from an LLM client

The MCP `update_books` tool applies a batch of updates in one call, for example
`{"42": {"rating": 5, "add_tags": ["favorites"]}, "99": {"merge_into": 42}}`.
See [MCP Server](../integrations/mcp.md#update_books).

## Scripting with the Python API

```python
from pathlib import Path
from book_memex.library_db import Library
from book_memex.services.tag_service import TagService

lib = Library.open(Path("~/my-library").expanduser())
tags = TagService(lib.session)
for book in lib.query().filter_by_subject("Python").all():
    tags.add_tag_to_book(book, "Programming/Python")   # hierarchical tag
lib.close()
```
