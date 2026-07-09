"""Unit tests for the create_session_audio_clip capability (MCP tool + Remote Script handler)."""

import os
import sys
import types
from unittest.mock import MagicMock, patch

# --- MCP layer setup (mirrors tests/unit/test_arrangement_commands.py) ---
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import create_session_audio_clip  # noqa: E402


class TestCreateSessionAudioClipCommand:
    """MCP layer: verify index conversion and command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_indices(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"name": "break.wav"}
        mock_conn.return_value = mock_ableton

        create_session_audio_clip(
            MagicMock(), track_index=2, clip_index=3, file_path="/break.wav")

        args = mock_ableton.send_command.call_args
        assert args[0][0] == "create_session_audio_clip"
        assert args[0][1]["track_index"] == 1  # 1-based -> 0-based
        assert args[0][1]["clip_index"] == 2  # 1-based -> 0-based
        assert args[0][1]["file_path"] == "/break.wav"


# --- Remote Script layer setup (mirrors tests/unit/test_remote_script_helpers.py) ---
class _StubControlSurface:
    def __init__(self, c_instance):
        pass

    def log_message(self, msg):
        pass


_framework = types.ModuleType("_Framework")
_cs_module = types.ModuleType("_Framework.ControlSurface")
_cs_module.ControlSurface = _StubControlSurface
sys.modules.setdefault("_Framework", _framework)
sys.modules.setdefault("_Framework.ControlSurface", _cs_module)

from AbletonMCP_Remote_Script import AbletonMCP  # noqa: E402


class _StubClipSlot:
    def __init__(self, has_clip=False, fail_with=None):
        self.has_clip = has_clip
        self.clip = None
        self._fail_with = fail_with
        self.create_audio_clip_calls = []

    def create_audio_clip(self, file_path):
        self.create_audio_clip_calls.append(file_path)
        if self._fail_with is not None:
            raise self._fail_with
        self.clip = MagicMock()
        self.clip.name = os.path.basename(file_path)
        self.clip.length = 4.0
        self.has_clip = True


class _StubTrack:
    def __init__(self, clip_slots):
        self.clip_slots = clip_slots


def _make_script(tracks):
    script = AbletonMCP.__new__(AbletonMCP)
    script._song = MagicMock()
    script._song.tracks = list(tracks)
    return script


class TestCreateSessionAudioClipHandler:
    """Remote Script layer: validation order and error paths, via stub objects."""

    def test_creates_clip_in_empty_slot(self):
        slot = _StubClipSlot(has_clip=False)
        script = _make_script([_StubTrack([slot])])

        result = script._create_session_audio_clip(0, 0, "/samples/break.wav")

        assert slot.create_audio_clip_calls == ["/samples/break.wav"]
        assert result["file_path"] == "/samples/break.wav"

    def test_occupied_slot_raises_specific_message(self):
        slot = _StubClipSlot(has_clip=True)
        script = _make_script([_StubTrack([slot])])

        try:
            script._create_session_audio_clip(0, 0, "/samples/break.wav")
            assert False, "expected Exception"
        except Exception as e:
            assert "already has a clip" in str(e)
        assert slot.create_audio_clip_calls == []

    def test_out_of_range_clip_index_raises_index_error(self):
        slot = _StubClipSlot(has_clip=False)
        script = _make_script([_StubTrack([slot])])  # only 1 slot exists

        try:
            script._create_session_audio_clip(0, 5, "/samples/break.wav")
            assert False, "expected IndexError"
        except IndexError:
            pass
        assert slot.create_audio_clip_calls == []

    def test_invalid_file_path_propagates_and_leaves_slot_empty(self):
        slot = _StubClipSlot(has_clip=False, fail_with=RuntimeError("cannot load file"))
        script = _make_script([_StubTrack([slot])])

        try:
            script._create_session_audio_clip(0, 0, "/samples/does-not-exist.wav")
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "cannot load file" in str(e)
        assert slot.has_clip is False

    def test_return_or_master_shaped_track_raises(self):
        # Return/Master tracks have no session clip slots; simulate with an
        # empty clip_slots list, matching the natural IndexError _create_clip
        # already relies on for the same track types.
        script = _make_script([_StubTrack([])])

        try:
            script._create_session_audio_clip(0, 0, "/samples/break.wav")
            assert False, "expected an exception, not a silent success"
        except (IndexError, AttributeError):
            pass
