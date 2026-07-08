"""Unit tests for clip_name resolution in _manage_clip_automation and browser metadata tags."""

import sys
import os
import json
import types
import pytest
from unittest.mock import MagicMock, patch

# Mock mcp dependencies before importing server module
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules.setdefault('mcp', _mock_mcp_module)
sys.modules.setdefault('mcp.server', MagicMock())
sys.modules.setdefault('mcp.server.fastmcp', _mock_fastmcp)

# Stub _Framework so the Remote Script can be imported without Ableton
_framework = types.ModuleType("_Framework")
_cs_module = types.ModuleType("_Framework.ControlSurface")

class _StubControlSurface:
    def __init__(self, c_instance):
        pass
    def log_message(self, msg):
        pass

_cs_module.ControlSurface = _StubControlSurface
sys.modules.setdefault("_Framework", _framework)
sys.modules.setdefault("_Framework.ControlSurface", _cs_module)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import (
    get_browser_items_at_path,
    _tags_for_browser_item,
)
from AbletonMCP_Remote_Script import AbletonMCP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_script():
    script = AbletonMCP.__new__(AbletonMCP)
    script._song = MagicMock()
    script.log_message = MagicMock()
    return script


def _make_midi_clip():
    clip = MagicMock()
    clip.is_midi_clip = True
    return clip


# ---------------------------------------------------------------------------
# Remote Script handler: clip_name resolution in _manage_clip_automation
# ---------------------------------------------------------------------------

class TestClipNameResolution:

    def test_clip_name_passed_to_resolve(self):
        """clip_name='Verse' is forwarded to _resolve_session_clip."""
        script = _make_script()
        clip = _make_midi_clip()
        script._resolve_session_clip = MagicMock(return_value=(MagicMock(), clip))

        script._manage_clip_automation(0, 0, "clear_all", "", {}, "Verse")

        script._resolve_session_clip.assert_called_once_with(0, 0, "Verse")

    def test_clip_index_used_when_no_name(self):
        """clip_name=None passes through unchanged to _resolve_session_clip."""
        script = _make_script()
        clip = _make_midi_clip()
        script._resolve_session_clip = MagicMock(return_value=(MagicMock(), clip))

        script._manage_clip_automation(0, 2, "clear_all", "", {}, None)

        script._resolve_session_clip.assert_called_once_with(0, 2, None)

    def test_empty_string_clip_name_uses_index(self):
        """clip_name='' (the default server.py sends) passes through to _resolve_session_clip.
        _resolve_session_clip's own falsy check handles the fallthrough to clip_index."""
        script = _make_script()
        clip = _make_midi_clip()
        script._resolve_session_clip = MagicMock(return_value=(MagicMock(), clip))

        script._manage_clip_automation(0, 3, "clear_all", "", {}, "")

        script._resolve_session_clip.assert_called_once_with(0, 3, "")

    def test_unknown_clip_name_raises(self):
        """ValueError from _resolve_session_clip propagates out of _manage_clip_automation."""
        script = _make_script()
        script._resolve_session_clip = MagicMock(
            side_effect=ValueError("Clip 'Unknown' not found")
        )

        with pytest.raises(ValueError, match="not found"):
            script._manage_clip_automation(0, 0, "clear_all", "", {}, "Unknown")


# ---------------------------------------------------------------------------
# server.py function: _tags_for_browser_item
# ---------------------------------------------------------------------------

class TestBrowserTags:

    def test_bass_path_tags(self):
        """Path containing 'bass' produces bass tags."""
        tags = _tags_for_browser_item("instruments/bass", "Deep Sub")
        assert "bass" in tags

    def test_808_name_tags(self):
        """Item name containing '808' produces 808 and bass tags."""
        tags = _tags_for_browser_item("instruments", "808 Sub Bass")
        assert "808" in tags
        assert "bass" in tags

    def test_no_match_returns_empty(self):
        """Item with no matching keywords returns empty list."""
        tags = _tags_for_browser_item("instruments", "Synth 001")
        assert tags == []

    def test_drum_path_tags(self):
        """Path 'drums/kick' with name 'Kick 909' produces drums and kick tags."""
        tags = _tags_for_browser_item("drums/kick", "Kick 909")
        assert "drums" in tags
        assert "kick" in tags

    def test_tags_are_sorted(self):
        """Tags are returned in alphabetical order (deterministic output)."""
        tags = _tags_for_browser_item("instruments/bass", "808 Sub")
        assert tags == sorted(tags)


# ---------------------------------------------------------------------------
# MCP tool: get_browser_items_at_path
# ---------------------------------------------------------------------------

class TestBrowserItemsAtPath:

    @patch('MCP_Server.server.get_ableton_connection')
    def test_items_augmented_with_tags(self, mock_conn):
        """Items at a bass path get 'bass' in their tags."""
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "path": "instruments/bass",
            "name": "Bass",
            "items": [
                {"name": "808 Sub", "is_folder": False, "is_device": True, "is_loadable": True}
            ]
        }
        mock_conn.return_value = mock_ableton

        result = get_browser_items_at_path(MagicMock(), path="instruments/bass")

        parsed = json.loads(result)
        assert "tags" in parsed["items"][0]
        assert "bass" in parsed["items"][0]["tags"]

    @patch('MCP_Server.server.get_ableton_connection')
    def test_items_without_match_have_no_tags(self, mock_conn):
        """Items with no matching keywords must NOT have a 'tags' key (key absent, not empty list)."""
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "path": "instruments",
            "name": "Instruments",
            "items": [
                {"name": "Patch 001", "is_folder": False, "is_device": True, "is_loadable": True}
            ]
        }
        mock_conn.return_value = mock_ableton

        result = get_browser_items_at_path(MagicMock(), path="instruments")

        parsed = json.loads(result)
        assert "tags" not in parsed["items"][0]
