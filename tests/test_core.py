"""Smoke tests for the shared console core."""

from __future__ import annotations

import io
import logging
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tarbot_console import ConsoleAwareStreamHandler, ConsoleCore


class DemoConsole(ConsoleCore):
    bot_name = "Demo"
    help_lines = ["=== Demo Commands ===", "  ping"]
    extra_completions = {"ping": None}

    async def dispatch_command(self, cmd: str, args: list[str]) -> bool:
        if cmd == "ping":
            self.write_output("pong")
            return True
        return False


@pytest.fixture
def console():
    db = MagicMock()
    db.is_console_admin = AsyncMock(return_value=True)
    settings = MagicMock(console_session_timeout=300.0)
    return DemoConsole(MagicMock(), db, settings)


async def run(console: DemoConsole, line: str) -> str:
    out = io.StringIO()
    with patch("sys.stdout", out):
        await console.handle_command(line)
    return out.getvalue()


@pytest.mark.asyncio
async def test_locked_console_blocks_bot_commands(console):
    assert "[AUTH REQUIRED]" in await run(console, "ping")


@pytest.mark.asyncio
async def test_authenticated_console_routes_to_subclass(console):
    console.is_authenticated = True
    console.authenticated_user = "root"
    console._last_activity = time.monotonic()
    assert "pong" in await run(console, "ping")
    assert "Unknown command 'nope'" in await run(console, "nope")


@pytest.mark.asyncio
async def test_idle_session_locks(console):
    console.is_authenticated = True
    console.authenticated_user = "root"
    console._last_activity = time.monotonic() - 305
    assert "SESSION TIMEOUT" in await run(console, "ping")
    assert not console.is_authenticated


def test_prompt_and_help_use_bot_name(console):
    assert console._get_prompt() == "demo [LOCKED]> "
    out = io.StringIO()
    with patch("sys.stdout", out):
        console._cmd_help()
    assert "=== Demo Commands ===" in out.getvalue()
    assert "LOCKED" in out.getvalue()


def test_handler_hides_console_cmd_echo():
    handler = ConsoleAwareStreamHandler(io.StringIO())
    ConsoleAwareStreamHandler._log_buffer.clear()
    record = logging.LogRecord("demo.console", logging.INFO, "", 0, "[CMD] Executed: x", None, None)
    handler.emit(record)
    assert ConsoleAwareStreamHandler._log_buffer == []
