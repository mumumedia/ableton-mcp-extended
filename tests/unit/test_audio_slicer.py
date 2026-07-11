"""Unit tests for scripts/audio_slicer.py."""

import os
import sys

import numpy as np
import pytest
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from audio_slicer import parse_bpm_from_filename, slice_to_one_bar_chops  # noqa: E402


class TestParseBpmFromFilename:
    def test_extracts_bpm_from_realistic_filename(self):
        assert parse_bpm_from_filename("Break Scatty 174 bpm.wav") == 174.0

    def test_extracts_bpm_case_insensitive_and_no_space(self):
        assert parse_bpm_from_filename("groove_128BPM.wav") == 128.0

    def test_extracts_bpm_with_surrounding_text(self):
        assert parse_bpm_from_filename("Deep House Loop 122 bpm (mixed).wav") == 122.0

    def test_returns_none_when_no_bpm_present(self):
        assert parse_bpm_from_filename("fd_125_scattywoman.wav") is None
        assert parse_bpm_from_filename("Ambient Pad.wav") is None


class TestSliceToOneBarChops:
    @staticmethod
    def _bar_frames(bpm, samplerate=44100, beats_per_bar=4):
        # Mirrors slice_to_one_bar_chops's own rounding exactly, so test
        # fixtures contain precise integer multiples of a bar - avoids
        # float-precision drift between a test's duration-in-seconds and
        # the slicer's duration-in-frames.
        bar_seconds = (60.0 / bpm) * beats_per_bar
        return int(round(bar_seconds * samplerate))

    def _write_synthetic_wav_frames(self, tmp_path, filename, num_frames, samplerate=44100):
        path = os.path.join(tmp_path, filename)
        data = np.random.uniform(-0.5, 0.5, size=num_frames).astype(np.float32)
        sf.write(path, data, samplerate)
        return path

    def test_produces_expected_chop_count(self, tmp_path):
        bar_frames = self._bar_frames(174.0)
        source = self._write_synthetic_wav_frames(
            tmp_path, "Break Scatty 174 bpm.wav", num_frames=bar_frames * 8
        )
        output_dir = os.path.join(tmp_path, "chops")

        chops = slice_to_one_bar_chops(source, output_dir)

        assert len(chops) == 8
        for chop_path in chops:
            assert os.path.exists(chop_path)

    def test_drops_trailing_partial_bar(self, tmp_path):
        bar_frames = self._bar_frames(120.0)
        # 3 full bars plus half a bar -> 3 full chops, partial bar dropped
        source = self._write_synthetic_wav_frames(
            tmp_path, "Groove 120 bpm.wav", num_frames=bar_frames * 3 + bar_frames // 2
        )
        output_dir = os.path.join(tmp_path, "chops")

        chops = slice_to_one_bar_chops(source, output_dir)

        assert len(chops) == 3

    def test_source_file_unchanged_after_slicing(self, tmp_path):
        bar_frames = self._bar_frames(100.0)
        source = self._write_synthetic_wav_frames(
            tmp_path, "Break 100 bpm.wav", num_frames=bar_frames * 4
        )
        original_mtime = os.path.getmtime(source)
        with open(source, "rb") as f:
            original_bytes = f.read()

        slice_to_one_bar_chops(source, os.path.join(tmp_path, "chops"))

        assert os.path.getmtime(source) == original_mtime
        with open(source, "rb") as f:
            assert f.read() == original_bytes

    def test_raises_value_error_on_unparseable_bpm(self, tmp_path):
        source = self._write_synthetic_wav_frames(tmp_path, "no_tempo_info.wav", num_frames=44100 * 4)

        with pytest.raises(ValueError):
            slice_to_one_bar_chops(source, os.path.join(tmp_path, "chops"))
