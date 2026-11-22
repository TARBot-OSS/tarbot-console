"""Smoke tests for the shared console core."""

from __future__ import annotations

import io
import logging
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from prompt_toolkit.data_structures import Point
from prompt_toolkit.mouse_events import MouseButton, MouseEvent, MouseEventType
from prompt_toolkit.widgets import TextArea

from tarbot_console import ConsoleAwareStreamHandler, ConsoleCore
from tarbot_console.core import (
    WHEEL_STEP,
    _append_to_pane,
    _clear_pane,
    _install_wheel_scroll,
    _is_following,
    _scroll_pane,
)


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


def _pane(lines: int = 200) -> TextArea:
    area = TextArea(text="".join(f"line {i}\n" for i in range(lines)), read_only=True)
    area.buffer.cursor_position = len(area.text)
    return area


def test_append_keeps_scrolled_up_reader_in_place():
    area = _pane()
    _scroll_pane(area, -50)
    saved = area.buffer.cursor_position

    _append_to_pane(area, "NEW LINE")

    assert area.text.endswith("NEW LINE\n")
    assert area.buffer.cursor_position == saved


def test_small_scroll_is_not_snapped_back_by_streaming_logs():
    # The old rule treated "within 2 lines of the end" as following, so one wheel tick up
    # was undone by the next log line.
    area = _pane()
    _scroll_pane(area, -1)
    for i in range(5):
        _append_to_pane(area, f"burst {i}")
    assert area.buffer.cursor_position < len(area.text)
    assert not _is_following(area)


def test_append_follows_tail_when_reader_is_at_bottom():
    area = _pane()

    _append_to_pane(area, "NEW LINE")

    assert area.buffer.cursor_position == len(area.text)


def test_scrolling_back_to_the_bottom_resumes_following():
    area = _pane()
    _scroll_pane(area, -30)
    _scroll_pane(area, 1000)
    assert _is_following(area)
    _append_to_pane(area, "NEW LINE")
    assert area.buffer.cursor_position == len(area.text)


def test_pane_is_capped_and_scrolled_position_shifts_with_trim(monkeypatch):
    monkeypatch.setattr("tarbot_console.core.MAX_PANE_LINES", 100)
    area = _pane(100)
    _scroll_pane(area, -20)
    row_text = area.document.current_line

    _append_to_pane(area, "NEW LINE")

    assert area.text.count("\n") == 100
    assert area.text.startswith("line 1\n")
    assert area.document.current_line == row_text


def test_wheel_ticks_scroll_the_pane_and_stop_following():
    area = _pane()
    _install_wheel_scroll(area)
    event = MouseEvent(
        position=Point(0, 0), event_type=MouseEventType.SCROLL_UP, button=MouseButton.NONE, modifiers=frozenset()
    )

    assert area.window._mouse_handler(event) is None
    assert not _is_following(area)
    assert area.document.cursor_position_row == area.document.line_count - 1 - WHEEL_STEP


def test_clear_makes_pane_follow_again():
    area = _pane()
    _scroll_pane(area, -10)
    _clear_pane(area)
    assert _is_following(area)


def _completion_texts(console, text: str) -> list[str]:
    from prompt_toolkit.document import Document

    completer = console._get_completer()
    return [c.text for c in completer.get_completions(Document(text), None)]


def test_default_argument_options_leave_nested_completions_unchanged(console):
    console.is_authenticated = False
    assert _completion_texts(console, "clear ") == ["output", "logs", "all"]


def test_argument_options_hook_fills_slot_and_defers_otherwise(console):
    console.is_authenticated = True
    console.argument_options = lambda head: ["AAA", "BBB"] if head == ["ping", "x"] else None

    assert _completion_texts(console, "ping x ") == ["AAA", "BBB"]
    assert _completion_texts(console, "ping x b") == ["BBB"]
    assert _completion_texts(console, "clear ") == ["output", "logs", "all"]


def test_password_mode_offers_no_completions(console):
    console._is_password_mode = True
    assert console._get_completer() is None
