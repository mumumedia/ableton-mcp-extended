"""BPM parsing and one-bar audio slicing for the Phase 7 grid population script.

Slicing is deliberately filename-driven, not content-analyzed: BPM comes from
a "174 bpm"-style token in the source filename (see 07-01's live discovery of
"Break Scatty 174 bpm.wav"), never from audio-content tempo detection.
"""

import os
import re

import soundfile as sf

_BPM_PATTERN = re.compile(r"(\d{2,3})\s*bpm", re.IGNORECASE)


def parse_bpm_from_filename(filename: str) -> float | None:
    """Extract a BPM value like "174" from a filename containing "174 bpm".

    Returns None if no BPM pattern is found - callers must treat this as a
    hard exclusion from slicing, not a default/guess.
    """
    match = _BPM_PATTERN.search(filename)
    if not match:
        return None
    return float(match.group(1))


def slice_to_one_bar_chops(source_path: str, output_dir: str, beats_per_bar: int = 4) -> list[str]:
    """Slice a source audio file into consecutive one-bar chops.

    Reads source_path read-only via soundfile, computes one-bar duration from
    the BPM parsed out of its filename, and writes each full bar as a new
    file into output_dir. Any trailing partial bar shorter than a full bar is
    dropped. Raises ValueError if the source's BPM can't be parsed - this
    function never guesses or defaults a BPM.
    """
    filename = os.path.basename(source_path)
    bpm = parse_bpm_from_filename(filename)
    if bpm is None:
        raise ValueError(f"Cannot parse BPM from filename: {filename!r}")

    data, samplerate = sf.read(source_path)
    bar_seconds = (60.0 / bpm) * beats_per_bar
    bar_frames = int(round(bar_seconds * samplerate))
    if bar_frames <= 0:
        raise ValueError(f"Computed non-positive bar length for {filename!r} at {bpm} BPM")

    os.makedirs(output_dir, exist_ok=True)
    source_stem = os.path.splitext(filename)[0]

    written_paths: list[str] = []
    total_frames = len(data)
    chop_index = 0
    start = 0
    while start + bar_frames <= total_frames:
        end = start + bar_frames
        chop = data[start:end]
        chop_path = os.path.join(output_dir, f"{source_stem}_chop{chop_index}.wav")
        sf.write(chop_path, chop, samplerate)
        written_paths.append(chop_path)
        start = end
        chop_index += 1

    return written_paths
