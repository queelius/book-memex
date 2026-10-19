# Similar Books

book-memex can rank the books in your library by similarity to a given book,
combining text similarity (over extracted text), subject overlap, and author
matching. It requires the `similarity` extra (numpy and scikit-learn):

```bash
pip install -e ".[similarity]"
```

## CLI

```bash
book-memex book similar 42 ~/my-library
book-memex book similar 42 ~/my-library --limit 20
book-memex book similar 42 ~/my-library --mode metadata
book-memex book similar 42 ~/my-library --format json
```

Modes:

| Mode | Uses |
|------|------|
| `auto` (default) | picks a strategy based on the data available |
| `balanced` | content and metadata (needs extracted text) |
| `metadata` | authors, subjects, and other metadata only |
| `sparse` | tuned for books with little metadata or text |

## Python API

```python
from pathlib import Path
from book_memex.library_db import Library

lib = Library.open(Path("~/my-library").expanduser())

for book, score in lib.find_similar(42, top_k=10):
    print(f"{score:.2f}  {book.title}")

lib.close()
```

`Library.compute_similarity_matrix()` returns the books and a pairwise
similarity matrix for a set of book IDs (or the whole library). The building
blocks (feature extractors, metrics, and `BookSimilarity`) live in
`book_memex.similarity`.

## Scope

Similarity here is computed locally from the archive's own text and metadata.
book-memex deliberately does not compute embeddings or semantic search: in the
`*-memex` ecosystem that belongs to the `memex` federation layer, which pulls
segment text from this archive over MCP and maintains one cross-archive vector
index.

## See also

- [CLI Reference](../user-guide/cli.md)
- [Python API](../user-guide/api.md)
