"""Filesystem-walk-based loop discovery with token-boundary genre/BPM tagging.

Deliberately does not use Ableton's browser MCP tools: get_browser_items_at_path
only returns Live's internal browser `uri` scheme, never a real filesystem path
(confirmed during 07-02 planning), so loop discovery has to walk real files.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from audio_slicer import parse_bpm_from_filename  # noqa: E402

_AUDIO_EXTENSIONS = (".wav", ".aif", ".aiff")

# Genre/loop-relevant terms only - deliberately excludes generic terms like
# "loop" or "beat" that would match most of any sample library and defeat
# the point of token-based filtering.
#
# Includes instrument-category keywords (drum/perc/kit) alongside genre
# words: content living under a "Drums"-style folder path often has no
# genre word in its filename at all, and matching only genre words was
# confirmed live to under-match real drum content (07-02 checkpoint).
_GENRE_KEYWORD_TAGS: dict[str, list[str]] = {
    "break": ["breakbeat"],
    "breakbeat": ["breakbeat"],
    "techno": ["techno"],
    "house": ["house"],
    "jungle": ["jungle", "breakbeat"],
    "dnb": ["dnb", "breakbeat"],
    "garage": ["garage"],
    "electro": ["electro"],
    "drum": ["drums"],
    "perc": ["drums", "percussion"],
    "kit": ["drums"],
}


def tags_for_loop(path: str, name: str) -> list[str]:
    """Token-boundary genre tags for a loop file, given its path and name.

    Mirrors the token-boundary matching pattern used by
    MCP_Server.server._tags_for_browser_item (tokenize, match via
    token.startswith(keyword)) to avoid substring false positives like
    "breakfast" matching "break" - reimplemented locally rather than
    imported, so this module has no dependency on MCP_Server.server.
    """
    combined = (path + " " + name).lower()
    tokens = re.findall(r"[a-z0-9]+", combined)
    tags: set[str] = set()
    for keyword, kw_tags in _GENRE_KEYWORD_TAGS.items():
        if any(token.startswith(keyword) for token in tokens):
            tags.update(kw_tags)
    return sorted(tags)


def discover_loops(library_roots: list[str], genre_filter: list[str] | None = None) -> list[dict]:
    """Walk library_roots for audio loop files, tagging and BPM-parsing each.

    Missing/inaccessible roots are skipped, not fatal - different OSes and
    Ableton editions may not have both Core Library and User Library present
    at the expected default paths.
    """
    candidates: list[dict] = []

    for root in library_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for filename in filenames:
                if not filename.lower().endswith(_AUDIO_EXTENSIONS):
                    continue
                full_path = os.path.join(dirpath, filename)
                tags = tags_for_loop(full_path, filename)
                if genre_filter and not (set(tags) & set(genre_filter)):
                    continue
                candidates.append({
                    "path": full_path,
                    "name": filename,
                    "tags": tags,
                    "bpm": parse_bpm_from_filename(filename),
                })

    return candidates
