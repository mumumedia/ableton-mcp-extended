#!/usr/bin/env python3
"""Grid population orchestrator for Phase 7's grid automation proof-of-concept.

Sources loops from Ableton's libraries, slices them into one-bar chops, and
populates a Session View grid on real audio tracks with density-weighted
placement (denser early scenes, sparser late scenes).

Talks to Ableton directly over the existing socket protocol via
MCP_Server.server.AbletonConnection - not through the FastMCP tool layer -
since this makes many sequential calls in a tight loop and going through
individual chat-driven tool calls would be needlessly slow (see 07-01's
SUMMARY for why this needs to be a script). Calls are made strictly
sequentially: this project's Ableton socket connection is single/synchronous
(see 07-01's checkpoint finding) - concurrent calls cross responses.
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from audio_slicer import parse_bpm_from_filename, slice_to_one_bar_chops  # noqa: E402
from loop_selector import discover_loops  # noqa: E402
from placement import plan_placements, select_loops  # noqa: E402

from MCP_Server.server import AbletonConnection  # noqa: E402

_DEFAULT_CORE_LIBRARY = (
    "/Applications/Ableton Live 12 Lite.app/Contents/App-Resources/Core Library/Samples"
)
_DEFAULT_USER_LIBRARY = os.path.expanduser("~/Music/Ableton/User Library/Samples")

# Confirmed live (07-02 checkpoint): "no filter, walk the entire library"
# pulled ~40-50% non-drum content. Default to drum/breakbeat-scoped content
# instead - pass --genre explicitly to widen or change scope.
_DEFAULT_GENRE_FILTER = ["drums", "breakbeat"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--library-root", action="append", dest="library_roots",
        default=None,
        help="Sample library root to search (repeatable). Defaults to Core + User Library.",
    )
    parser.add_argument(
        "--genre", action="append", dest="genre_filter", default=None,
        help="Genre tag to filter loops by (repeatable, any-match). "
             f"Default: {_DEFAULT_GENRE_FILTER}.",
    )
    parser.add_argument("--target-loops", type=int, default=25)
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "grid-chops"))
    parser.add_argument("--max-scenes", type=int, default=8)
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducible runs - useful for debugging a bad/failed run.",
    )
    return parser.parse_args()


def _discover_audio_tracks_and_scenes(connection: AbletonConnection, max_scenes: int):
    """Query the live session for audio tracks, their occupied slots, and scene count."""
    session_info = connection.send_command("get_session_info")
    project_bpm = session_info["tempo"]
    track_count = session_info["track_count"]

    audio_tracks = []
    total_scenes = 0
    for track_index in range(track_count):
        track_info = connection.send_command("get_track_info", {"track_index": track_index})
        if not track_info.get("is_audio_track"):
            continue
        clip_slots = track_info.get("clip_slots", [])
        total_scenes = max(total_scenes, min(len(clip_slots), max_scenes))
        audio_tracks.append({"track_index": track_index, "clip_slots": clip_slots})

    return project_bpm, audio_tracks, total_scenes


def _eligible_slots(audio_tracks: list[dict], total_scenes: int) -> list[tuple]:
    slots = []
    for track in audio_tracks:
        for scene_index, clip_slot in enumerate(track["clip_slots"][:total_scenes]):
            if clip_slot.get("has_clip"):
                continue  # AC-4: skip already-occupied slots, never overwrite
            slots.append((track["track_index"], scene_index, scene_index))
    return slots


def main() -> None:
    args = _parse_args()
    rng = random.Random(args.seed)
    library_roots = args.library_roots or [_DEFAULT_CORE_LIBRARY, _DEFAULT_USER_LIBRARY]
    genre_filter = args.genre_filter if args.genre_filter is not None else _DEFAULT_GENRE_FILTER

    connection = AbletonConnection(host="localhost", port=9877)
    if not connection.connect():
        print("Error: could not connect to Ableton. Is the Remote Script loaded?")
        return

    project_bpm, audio_tracks, total_scenes = _discover_audio_tracks_and_scenes(
        connection, args.max_scenes
    )
    print(f"Project tempo: {project_bpm} BPM. {len(audio_tracks)} audio track(s), "
          f"{total_scenes} scene(s) considered.")

    candidates = discover_loops(library_roots, genre_filter=genre_filter)
    bpm_eligible = [c for c in candidates if c["bpm"] is not None]  # AC-2 gate
    print(f"Found {len(candidates)} candidate loop(s), {len(bpm_eligible)} with parseable BPM.")

    selected_loops = select_loops(bpm_eligible, project_bpm, args.target_loops, rng)
    if len(selected_loops) < args.target_loops:
        print(f"Warning: only {len(selected_loops)} BPM-parseable loop(s) available "
              f"(requested {args.target_loops}); continuing with what's available.")

    available_chops: list[str] = []
    for loop in selected_loops:
        try:
            chops = slice_to_one_bar_chops(loop["path"], args.output_dir)
            available_chops.extend(chops)
        except ValueError as e:
            print(f"Skipping {loop['name']!r}: {e}")
    print(f"Sliced {len(selected_loops)} loop(s) into {len(available_chops)} one-bar chop(s).")

    eligible_slots = _eligible_slots(audio_tracks, total_scenes)
    placements = plan_placements(eligible_slots, available_chops, total_scenes, rng)
    print(f"Planned {len(placements)} placement(s) across {len(eligible_slots)} eligible slot(s).")

    filled = 0
    errors = 0
    for placement in placements:
        try:
            connection.send_command("create_session_audio_clip", {
                "track_index": placement["track_index"],
                "clip_index": placement["clip_index"],
                "file_path": placement["file_path"],
            })
            filled += 1
        except Exception as e:
            errors += 1
            print(f"Error placing clip at track {placement['track_index']}, "
                  f"slot {placement['clip_index']}: {e}")

    print(f"\nSummary: {len(selected_loops)} loops sourced, {len(available_chops)} chops created, "
          f"{filled} slot(s) filled, {errors} error(s), seed={args.seed}")


if __name__ == "__main__":
    main()
