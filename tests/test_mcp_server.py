"""Tests for MCP server setup."""
import json
import subprocess
import sys

import pytest

mcp_mod = pytest.importorskip("mcp")

from book_memex.library_db import Library
from book_memex.mcp.server import create_mcp_server


@pytest.fixture
def mcp_server(tmp_path):
    """Create a library and MCP server for testing."""
    lib = Library.open(tmp_path / "test-lib")
    server = create_mcp_server(lib)
    yield server
    lib.close()


class TestMCPServer:
    def test_server_creates_successfully(self, mcp_server):
        assert mcp_server is not None
        assert mcp_server.name == "book-memex"

    def test_server_has_instructions(self, mcp_server):
        assert mcp_server.instructions is not None
        assert "get_schema" in mcp_server.instructions


class TestStdioTransport:
    """`mcp-serve` speaks JSON-RPC over stdout, so nothing else may write there."""

    def test_stdout_carries_only_jsonrpc(self, tmp_path):
        lib_path = tmp_path / "test-lib"
        Library.open(lib_path).close()

        proc = subprocess.Popen(
            [sys.executable, "-m", "book_memex.cli", "mcp-serve", str(lib_path)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True,
        )

        def send(msg):
            proc.stdin.write(json.dumps(msg) + "\n")
            proc.stdin.flush()

        def reply_to(request_id):
            # Every stdout line must parse: a log line here corrupts the protocol.
            # Like a real client, keep stdin open until the reply arrives.
            for line in proc.stdout:
                msg = json.loads(line)
                if msg.get("id") == request_id:
                    return msg
            raise AssertionError(f"server exited before replying to {request_id}")

        try:
            send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "test", "version": "0"}}})
            reply_to(1)
            send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
            assert reply_to(2)["result"]["tools"]
        finally:
            proc.stdin.close()
            proc.wait(timeout=30)
