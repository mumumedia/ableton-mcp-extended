"""Unit tests for delete_session_clip and fire_scene (MCP tools + Remote Script handlers)."""

import os
import sys
import types
from unittest.mock import MagicMock, patch

# --- MCP layer setup (mirrors tests/unit/test_session_audio_clip.py) ---
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import delete_session_clip, fire_scene  # noqa: E402


class TestDeleteSessionClipCommand:
    """MCP layer: verify index conversion and command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_indices(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"deleted": True}
        mock_conn.return_value = mock_ableton

        delete_session_clip(MagicMock(), track_index=2, clip_index=3)

        args = mock_ableton.send_command.call_args
        assert args[0][0] == "delete_session_clip"
        assert args[0][1]["track_index"] == 1  # 1-based -> 0-based
        assert args[0][1]["clip_index"] == 2  # 1-based -> 0-based


class TestFireSceneCommand:
    """MCP layer: verify index conversion and command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_index(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"fired": True, "was_empty": False}
        mock_conn.return_value = mock_ableton

        fire_scene(MagicMock(), scene_index=3)

        args = mock_ableton.send_command.call_args
        assert args[0][0] == "fire_scene"
        assert args[0][1]["scene_index"] == 2  # 1-based -> 0-based

    @patch('MCP_Server.server.get_ableton_connection')
    def test_reports_was_empty(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"fired": True, "was_empty": True}
        mock_conn.return_value = mock_ableton

        result = fire_scene(MagicMock(), scene_index=1)

        assert "was empty" in result


# --- Remote Script layer setup (mirrors tests/unit/test_session_audio_clip.py) ---
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
    def __init__(self, has_clip=False):
        self.has_clip = has_clip
        self.clip = MagicMock() if has_clip else None
        self.delete_clip_calls = 0

    def delete_clip(self):
        self.delete_clip_calls += 1
        self.has_clip = False
        self.clip = None


class _StubTrack:
    def __init__(self, clip_slots, arm=False, name="Track"):
        self.clip_slots = clip_slots
        self.arm = arm
        self.name = name


class _StubScene:
    def __init__(self, is_empty=False):
        self.is_empty = is_empty
        self.fire_calls = 0

    def fire(self):
        self.fire_calls += 1


def _make_script(tracks=(), scenes=()):
    script = AbletonMCP.__new__(AbletonMCP)
    script._song = MagicMock()
    script._song.tracks = list(tracks)
    script._song.scenes = list(scenes)
    return script


class TestDeleteSessionClipHandler:
    """Remote Script layer: validation order and error paths, via stub objects."""

    def test_deletes_clip_from_occupied_slot(self):
        slot = _StubClipSlot(has_clip=True)
        script = _make_script(tracks=[_StubTrack([slot])])

        script._delete_session_clip(0, 0)

        assert slot.delete_clip_calls == 1
        assert slot.has_clip is False

    def test_refuses_to_delete_slot_with_filled_slot_after_it(self):
        # Live-confirmed during the 07-03 checkpoint: deleting a clip that
        # still has a filled slot after it orphans that later clip from
        # Follow Action "Any" - this must be refused, not allowed (AC-10).
        target_slot = _StubClipSlot(has_clip=True)
        later_slot = _StubClipSlot(has_clip=True)
        script = _make_script(tracks=[_StubTrack([target_slot, later_slot])])

        try:
            script._delete_session_clip(0, 0)
            assert False, "expected Exception"
        except Exception as e:
            assert "would be orphaned" in str(e)
        assert target_slot.delete_clip_calls == 0
        assert later_slot.delete_clip_calls == 0

    def test_allows_deleting_bottom_slot_of_a_filled_run(self):
        # The last (deepest) filled slot in a track has nothing after it,
        # so deletion must still succeed - this is the correct way to
        # refresh a track per grid-conductor's bottom-up rule.
        first_slot = _StubClipSlot(has_clip=True)
        last_slot = _StubClipSlot(has_clip=True)
        script = _make_script(tracks=[_StubTrack([first_slot, last_slot])])

        script._delete_session_clip(0, 1)

        assert last_slot.delete_clip_calls == 1
        assert first_slot.delete_clip_calls == 0  # untouched

    def test_empty_slot_raises_specific_message(self):
        slot = _StubClipSlot(has_clip=False)
        script = _make_script(tracks=[_StubTrack([slot])])

        try:
            script._delete_session_clip(0, 0)
            assert False, "expected Exception"
        except Exception as e:
            assert "slot is empty" in str(e)
        assert slot.delete_clip_calls == 0

    def test_out_of_range_clip_index_raises_index_error(self):
        slot = _StubClipSlot(has_clip=True)
        script = _make_script(tracks=[_StubTrack([slot])])

        try:
            script._delete_session_clip(0, 5)
            assert False, "expected IndexError"
        except IndexError:
            pass


class TestFireSceneHandler:
    """Remote Script layer: armed-track guard and firing, via stub objects."""

    def test_fires_scene_with_no_armed_empty_tracks(self):
        scene = _StubScene(is_empty=False)
        track = _StubTrack([_StubClipSlot(has_clip=True)], arm=False)
        script = _make_script(tracks=[track], scenes=[scene])

        result = script._fire_scene(0)

        assert scene.fire_calls == 1
        assert result["fired"] is True
        assert result["was_empty"] is False

    def test_refuses_to_fire_into_armed_empty_track(self):
        scene = _StubScene(is_empty=False)
        armed_track = _StubTrack([_StubClipSlot(has_clip=False)], arm=True, name="Drums")
        script = _make_script(tracks=[armed_track], scenes=[scene])

        try:
            script._fire_scene(0)
            assert False, "expected Exception"
        except Exception as e:
            assert "Drums" in str(e)
        assert scene.fire_calls == 0

    def test_armed_track_with_clip_in_scene_does_not_block(self):
        # Armed but already has a clip in this scene -> firing won't start a
        # NEW recording, so it should not be blocked.
        scene = _StubScene(is_empty=False)
        armed_track = _StubTrack([_StubClipSlot(has_clip=True)], arm=True, name="Drums")
        script = _make_script(tracks=[armed_track], scenes=[scene])

        script._fire_scene(0)

        assert scene.fire_calls == 1

    def test_was_empty_reflects_pre_fire_state(self):
        scene = _StubScene(is_empty=True)
        script = _make_script(tracks=[], scenes=[scene])

        result = script._fire_scene(0)

        assert result["was_empty"] is True

    def test_out_of_range_scene_index_raises_index_error(self):
        script = _make_script(tracks=[], scenes=[_StubScene()])

        try:
            script._fire_scene(5)
            assert False, "expected IndexError"
        except IndexError:
            pass
