# Configuration Guide

book-memex keeps a small set of user defaults (default library path, web server
host/port, CLI output preferences) in a single JSON file. Everything in it can be
overridden on the command line.

## Configuration file location

The path is fixed and kept from the project's `ebk` days for backward
compatibility:

```
~/.config/ebk/config.json
```

If the `~/.config` directory does not exist, book-memex falls back to
`~/.ebk/config.json`. There are no environment variables that change this
location, and `XDG_CONFIG_HOME` is not consulted.

## Configuration structure

The file has three sections. Defaults:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "auto_open_browser": false,
    "page_size": 50
  },
  "cli": {
    "verbose": false,
    "color": true,
    "page_size": 50
  },
  "library": {
    "default_path": null
  }
}
```

- **server.host**: bind address for `book-memex serve`. Loopback by default
  because the REST API is unauthenticated (see [Web Server](../user-guide/server.md)).
- **server.port**: web server port.
- **server.auto_open_browser**: open a browser tab when the server starts.
- **server.page_size**: default number of books per page in the web UI.
- **cli.verbose**, **cli.color**, **cli.page_size**: CLI output defaults.
- **library.default_path**: the library used when a command's library argument
  is omitted (including `book-memex serve` and `book-memex mcp-serve`).

## Managing configuration

`book-memex config` is flag-based: every flag sets one value, and several flags
can be combined in one call.

```bash
# Show the current configuration
book-memex config --show

# Create the config file with defaults (if it does not exist)
book-memex config --init

# Set the default library
book-memex config --library-path ~/my-library

# Server defaults
book-memex config --server-host 127.0.0.1 --server-port 9000
book-memex config --server-auto-open        # or --no-server-auto-open

# CLI defaults
book-memex config --cli-verbose             # or --no-cli-verbose
book-memex config --no-cli-color            # or --cli-color

# Several at once
book-memex config --library-path ~/my-library --server-port 9000
```

There is no flag for the `page_size` values; edit the JSON file directly to
change them.

## Command-line overrides

Command-line options always take precedence over the configuration file:

```bash
book-memex serve ~/other-library --port 9000
book-memex --verbose import add book.pdf ~/my-library
```

## Common scenarios

### Work with one library

```bash
book-memex config --library-path ~/my-library
book-memex query list
book-memex serve
book-memex mcp-serve
```

### Network access to the web server

The server refuses to bind a non-loopback host unless you pass `--allow-remote`,
even if `server.host` is set to `0.0.0.0` in the config file:

```bash
book-memex serve ~/my-library --host 0.0.0.0 --allow-remote
```

Only do this on a trusted network: the REST API has no authentication and
includes destructive routes.

## Troubleshooting

### Configuration not picked up

```bash
book-memex config --show            # prints the values actually loaded
ls -la ~/.config/ebk/config.json
book-memex config --init            # create it if missing
```

### Invalid JSON

If the file cannot be parsed, book-memex prints a warning and falls back to the
defaults. To start over:

```bash
mv ~/.config/ebk/config.json ~/.config/ebk/config.json.bak
book-memex config --init
```

## Next steps

- [Quick Start Guide](quickstart.md)
- [Web Server and Reader](../user-guide/server.md)
- [MCP Server](../integrations/mcp.md)
- [CLI Reference](../user-guide/cli.md)
