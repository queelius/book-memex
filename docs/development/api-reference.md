# API Reference

The main modules of the `book_memex` package. See the
[Python API guide](../user-guide/api.md) for usage examples.

## `book_memex.library_db`

`Library` (the entry point: `Library.open(path)`) and `QueryBuilder` (returned by
`lib.query()`).

```python
from book_memex.library_db import Library
```

## `book_memex.db.models`

SQLAlchemy ORM models: `Book`, `Author`, `Subject`, `Contributor`, `Identifier`,
`File`, `Cover`, `Tag`, `PersonalMetadata`, `Review`, `Marginalia`,
`ReadingSession`, `BookContent` (per-segment text), `ExtractedText`, `View`,
`ViewOverride`. Record models expose a `uri` property and an `archived_at` column.

## `book_memex.services`

- `ImportService`: book import and metadata extraction
- `ExportService`: JSON, CSV, Goodreads CSV, Calibre CSV, HTML, OPDS
- `PersonalMetadataService`: ratings, favorites, reading status and progress
- `MarginaliaService`: notes and highlights (create, list, archive, restore)
- `ReadingQueueService`: the reading queue
- `ViewService`: saved views
- `TextExtractionService`: full-text extraction

Further modules: `services.reading_session_service.ReadingSessionService`,
`services.tag_service.TagService`, `services.content_indexer`,
`services.arkiv_import`, `services.annotation_extraction`.

## `book_memex.core`

- `core.uri`: `build_book_uri`, `build_marginalia_uri`, `build_reading_uri`,
  `build_book_fragment_uri`, `parse_uri` (returns `ParsedUri(scheme, kind, id, fragment)`).
- `core.soft_delete`: `filter_active`, `archive`, `restore`, `hard_delete`.
- `core.fts`: `safe_fts_query` (always route user FTS5 input through it).

## `book_memex.views`

`ViewService`, `ViewEvaluator`, `TransformedBook`; the DSL grammar is documented
in `book_memex/views/dsl.py`.

## `book_memex.mcp`

`create_mcp_server(library)` and `run_server(library_path)` in `mcp.server`;
tool implementations in `mcp.tools`; `ReadOnlySQLExecutor` in `mcp.sql_executor`.
See [MCP Server](../integrations/mcp.md).

## `book_memex.similarity`

`BookSimilarity` plus feature extractors and metrics (requires the `similarity`
extra). `Library.find_similar()` is the convenient entry point.

## See also

- [Python API Guide](../user-guide/api.md)
- [Architecture](architecture.md)
