# Web Server and Reader

`book-memex serve` starts a FastAPI application that provides:

- a single-page **library UI** at `/` for browsing, filtering, editing, and importing,
- a **browser reader** for EPUB and PDF at `/read/{book_id}`,
- a **REST API** under `/api/...`,
- a live **OPDS 1.2 catalog** under `/opds/` for e-reader apps.

It requires the `server` extra and an ASGI server (`pip install -e ".[server]" uvicorn`).

## Starting the server

```bash
book-memex serve ~/my-library            # http://127.0.0.1:8000
book-memex serve ~/my-library --port 8080
book-memex serve                          # uses library.default_path from the config
book-memex serve --reload                 # auto-reload (development)
book-memex serve ~/my-library --no-open   # never open a browser tab
```

| Option | Meaning |
|--------|---------|
| `--host` | Bind address (default from config: `127.0.0.1`). |
| `--port` | Port (default from config: `8000`). |
| `--reload` | Auto-reload on code changes. |
| `--no-open` | Do not open a browser, even if `server.auto_open_browser` is set. |
| `--allow-remote` | Permit binding a non-loopback host. |

Defaults come from `~/.config/ebk/config.json`; set them with
`book-memex config --server-host ... --server-port ... --server-auto-open`.

## Security: loopback by default

The REST API is **unauthenticated** and includes destructive routes (book
deletion with file unlinking, metadata writes, uploads). The server therefore
refuses to bind anything other than `127.0.0.1`, `localhost`, or `::1` unless you
pass `--allow-remote`, and it prints a warning when you do:

```bash
book-memex serve ~/my-library --host 0.0.0.0 --allow-remote
```

Only do this on a trusted network. For access from elsewhere, keep the server on
loopback and put an authenticating reverse proxy, SSH tunnel, or VPN in front of it.

CORS is restricted to `http://localhost:8000`, `http://127.0.0.1:8000`,
`http://localhost:3000`, and `http://127.0.0.1:3000`.

## Browser reader

Open `http://127.0.0.1:8000/read/{book_id}` (or use "Open in reader" in the book
detail view).

- **Formats**: EPUB (EPUB.js) and PDF (PDF.js). DRM-protected books cannot be rendered.
- **Highlights**: selecting text creates a highlight, stored as
  [marginalia](library-management.md#marginalia) via `POST /api/marginalia`.
- **Progress**: the reading position (CFI or page) and percentage are synced to
  `PATCH /api/reading/progress`, and reading sessions are recorded.
- **Themes**: light, dark, and sepia (remembered per browser).
- **Navigation**: table of contents sidebar, page buttons, keyboard shortcuts,
  and bookmarkable URL fragments.
- **No CDN**: EPUB.js, JSZip, PDF.js, and the PDF.js worker are vendored and
  served from `/static/vendor/`, so the server needs no internet access.

Known limitations: PDF highlights are stored but not yet re-painted as overlays;
mobile touch handling works but is not polished; there is no offline (service
worker) mode, so the browser must reach the running server.

## REST API

FastAPI serves interactive documentation of every endpoint and schema at
`/docs` (Swagger UI) and `/redoc`. The main groups:

### Books

| Method and path | Purpose |
|-----------------|---------|
| `GET /api/books` | Paginated list. Query parameters: `limit`, `offset`, `search`, `author`, `subject`, `language`, `favorite`, `reading_status`, `format_filter`, `sort`, `order`, `rating` (minimum). |
| `GET /api/books/{id}` | One book. |
| `PATCH /api/books/{id}` | Update `title`, `subtitle`, `language`, `publisher`, `publication_date`, `description`, `rating`, `favorite`, `reading_status`, `tags`. |
| `DELETE /api/books/{id}` | Soft delete (archive) by default; `?hard=true` removes the row; `?delete_files=true` also unlinks files. |
| `GET /api/books/{id}/files/{format}` | Download a file. |
| `GET /api/books/{id}/cover` | Cover image. |
| `GET /api/stats` | Library statistics. |
| `GET /api/search?q=...` | Search with the [search syntax](search.md). |

`GET /api/books` returns `{"items": [...], "total": N, "offset": 0, "limit": 50}`.

```bash
curl "http://127.0.0.1:8000/api/books?author=Knuth&language=en&limit=20"
curl -X PATCH http://127.0.0.1:8000/api/books/42 \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "favorite": true, "reading_status": "reading"}'
```

### Imports

`POST /api/books/import` (multipart upload with a `file` field),
`/api/books/import/folder`, `/api/books/import/calibre`,
`/api/books/import/url`, `/api/books/import/opds`, `/api/books/import/isbn`.

```bash
curl -X POST http://127.0.0.1:8000/api/books/import -F "file=@book.pdf"
```

### Content search

| Method and path | Purpose |
|-----------------|---------|
| `GET /api/books/{id}/search?q=...` | FTS5 search inside one book's segments. |
| `GET /api/search/content?q=...` | FTS5 search across all segments. |

Hits include a snippet, the segment anchor, and a URI fragment.

### Marginalia and reading

| Method and path | Purpose |
|-----------------|---------|
| `POST /api/marginalia` | Create a note/highlight (0, 1, or many books). |
| `GET /api/marginalia?book_id=...` | List (archived excluded by default). |
| `GET/PATCH/DELETE /api/marginalia/{uuid}` | Read, edit, archive (`?hard=true` to delete). |
| `POST /api/marginalia/{uuid}/restore` | Un-archive. |
| `POST /api/reading/sessions/start`, `POST /api/reading/sessions/{uuid}/end` | Record a reading session. |
| `GET /api/reading/sessions`, `DELETE /api/reading/sessions/{uuid}`, `POST /api/reading/sessions/{uuid}/restore` | List, archive, restore sessions. |
| `GET/POST/PATCH /api/reading/progress` | Read or set progress. `POST` rejects backward progress with `409 Conflict`; `PATCH` always wins. |

### Views

`GET/POST /api/views`, `GET/PATCH/DELETE /api/views/{name}`,
`GET /api/views/{name}/books`, `POST/DELETE /api/views/{name}/books/{book_id}`,
`PUT/DELETE /api/views/{name}/overrides/{book_id}`, `GET /api/views/{name}/yaml`,
`POST /api/views/import`.

## OPDS catalog

The server publishes a live OPDS 1.2 catalog that e-reader apps (KOReader,
Foliate, Moon+ Reader, ...) can browse: point the app at
`http://<host>:8000/opds/`. Feeds include `/opds/all`, `/opds/recent`,
`/opds/search`, `/opds/authors`, `/opds/subjects`, `/opds/languages`, with
download and cover links. For a static catalog instead, use
`book-memex export opds`.

## Running as a service (systemd)

```ini
# ~/.config/systemd/user/book-memex.service
[Unit]
Description=book-memex web server

[Service]
ExecStart=%h/.local/bin/book-memex serve %h/my-library --no-open
Restart=on-failure

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now book-memex
```

Adjust `ExecStart` to wherever `book-memex` is installed (for example a
virtual environment's `bin/`).

## Troubleshooting

- **Port in use**: `lsof -i :8000`, then `book-memex serve ~/my-library --port 8080`.
- **"Refusing to bind"**: you asked for a non-loopback host without `--allow-remote`.
- **"uvicorn is not installed"**: `pip install uvicorn`.
- **Search misses a book by title**: rebuild the metadata index with
  `book-memex reindex-metadata --all -L ~/my-library` (see [Search](search.md)).

## Next steps

- [Configuration Guide](../getting-started/configuration.md)
- [CLI Reference](cli.md)
- [Python API](api.md)
