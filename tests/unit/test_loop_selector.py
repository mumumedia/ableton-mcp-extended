"""Unit tests for scripts/loop_selector.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from loop_selector import discover_loops, tags_for_loop  # noqa: E402


def _touch(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb"):
        pass


class TestTagsForLoop:
    def test_matches_genre_keyword(self):
        tags = tags_for_loop("/Library/Drums/Full", "Break Scatty 174 bpm.wav")
        assert "breakbeat" in tags

    def test_token_boundary_avoids_false_positive(self):
        # "outbreak" must NOT match "break" - "break" appears mid-token, not
        # as a prefix, mirroring the exact 03-03 bug class (warp -> arp,
        # shatter -> hat: keyword as a substring, not a token prefix).
        # Note: token.startswith(keyword) intentionally DOES match a keyword
        # appearing as a genuine prefix (e.g. "breakfast" legitimately
        # starts with "break") - that's correct, not a false positive.
        tags = tags_for_loop("/Library/Misc", "outbreak_sample.wav")
        assert "breakbeat" not in tags

    def test_no_match_returns_empty(self):
        tags = tags_for_loop("/Library/Ambient", "Soft Pad.wav")
        assert tags == []

    def test_matches_drum_folder_path_with_no_genre_word_in_filename(self):
        # Confirmed live (07-02 checkpoint): content living under a
        # Drums-style folder path with no genre word in its filename was
        # previously untagged entirely (AC-1c fix).
        tags = tags_for_loop(
            "/Applications/Ableton Live 12 Lite.app/Contents/App-Resources/"
            "Core Library/Samples/Loops/Drums/Full",
            "909 Groove 120.wav",
        )
        assert "drums" in tags


class TestDiscoverLoops:
    def test_finds_audio_files_and_attaches_bpm(self, tmp_path):
        root = str(tmp_path / "Core Library" / "Samples" / "Loops" / "Drums" / "Full")
        _touch(os.path.join(root, "Break Scatty 174 bpm.wav"))
        _touch(os.path.join(root, "Ambient Pad.wav"))
        _touch(os.path.join(root, "notes.txt"))  # non-audio, must be ignored

        results = discover_loops([str(tmp_path / "Core Library")])

        names = {item["name"] for item in results}
        assert names == {"Break Scatty 174 bpm.wav", "Ambient Pad.wav"}
        by_name = {item["name"]: item for item in results}
        assert by_name["Break Scatty 174 bpm.wav"]["bpm"] == 174.0
        assert by_name["Ambient Pad.wav"]["bpm"] is None

    def test_genre_filter_narrows_results(self, tmp_path):
        root = str(tmp_path / "Samples")
        _touch(os.path.join(root, "Break Scatty 174 bpm.wav"))
        _touch(os.path.join(root, "House Groove 124 bpm.wav"))
        _touch(os.path.join(root, "Ambient Pad.wav"))

        results = discover_loops([str(tmp_path)], genre_filter=["breakbeat"])

        names = {item["name"] for item in results}
        assert names == {"Break Scatty 174 bpm.wav"}

    def test_missing_library_root_is_skipped_not_fatal(self, tmp_path):
        existing_root = str(tmp_path / "Samples")
        _touch(os.path.join(existing_root, "Break 174 bpm.wav"))
        missing_root = str(tmp_path / "does-not-exist")

        results = discover_loops([missing_root, existing_root])

        assert len(results) == 1
        assert results[0]["name"] == "Break 174 bpm.wav"
