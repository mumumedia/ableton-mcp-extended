"""Pure, live-Ableton-independent placement planning for grid population.

Kept separate from populate_grid.py's live socket-calling loop so the
weighting and density logic can be unit tested against synthetic input
without a real Ableton connection.
"""

import random

# Weight floor for candidates with no plausible tempo relationship to the
# project - never zero, since AC-1b requires weighting, not hard exclusion.
_MIN_PROXIMITY_WEIGHT = 0.1
_PROXIMITY_TOLERANCE_RATIO = 0.06  # ~6% BPM difference still counts as "close"


def bpm_proximity_weight(candidate_bpm: float, project_bpm: float) -> float:
    """Weight a candidate BPM by proximity to the project tempo.

    Treats half-time and double-time relationships as equally valid
    proximity checks (e.g. 87 BPM is proximate to a 174 BPM project).
    Never returns zero - a tempo-unrelated candidate is deprioritized, not
    excluded.
    """
    if candidate_bpm <= 0 or project_bpm <= 0:
        return _MIN_PROXIMITY_WEIGHT

    best_ratio_diff = min(
        abs(candidate_bpm - project_bpm) / project_bpm,
        abs(candidate_bpm * 2 - project_bpm) / project_bpm,
        abs(candidate_bpm / 2 - project_bpm) / project_bpm,
    )

    if best_ratio_diff <= _PROXIMITY_TOLERANCE_RATIO:
        return 1.0
    # Decay smoothly from 1.0 toward the floor as the mismatch grows.
    weight = 1.0 / (1.0 + (best_ratio_diff / _PROXIMITY_TOLERANCE_RATIO))
    return max(weight, _MIN_PROXIMITY_WEIGHT)


def select_loops(
    candidates: list[dict],
    project_bpm: float,
    target_count: int,
    rng: random.Random,
) -> list[dict]:
    """Weight-select up to target_count loops from candidates.

    If fewer candidates exist than target_count, returns all of them
    without raising (AC-7) - this is a realistic outcome, not an error.
    """
    if not candidates:
        return []
    if len(candidates) <= target_count:
        return list(candidates)

    weights = [
        bpm_proximity_weight(c["bpm"], project_bpm) if c.get("bpm") else _MIN_PROXIMITY_WEIGHT
        for c in candidates
    ]

    pool = list(candidates)
    pool_weights = list(weights)
    selected: list[dict] = []
    while pool and len(selected) < target_count:
        chosen = rng.choices(pool, weights=pool_weights, k=1)[0]
        idx = pool.index(chosen)
        selected.append(pool.pop(idx))
        pool_weights.pop(idx)

    return selected


def scene_fill_probability(scene_index: int, total_scenes: int) -> float:
    """Monotonically decreasing fill probability by scene index.

    Scene 0 has the highest probability, the last scene the lowest -
    matches the "denser early, sparser late" pattern discussed for the
    reference producer's grid.
    """
    if total_scenes <= 1:
        return 1.0
    progress = scene_index / (total_scenes - 1)  # 0.0 .. 1.0
    return max(0.05, 1.0 - progress) ** 1.5


def plan_placements(
    eligible_slots: list[tuple],
    available_chops: list[str],
    total_scenes: int,
    rng: random.Random,
) -> list[dict]:
    """Decide which eligible (track_index, clip_index, scene_index) slots to fill.

    Fills each track contiguously from its first eligible scene: the first
    time a scene's density roll loses (or chops run out), that track's
    remaining scenes are skipped entirely - it never fills a deeper scene
    after skipping a shallower one. This guarantees no mid-track gaps (a
    real playback-safety requirement found live during the 07-02 checkpoint:
    a future sequential-triggering mechanism hitting an empty slot mid-track
    would produce unwanted silence), while still preserving the aggregate
    "denser early, sparser late" pattern via scene_fill_probability's decay.

    Stops assigning once available_chops is exhausted rather than raising
    (AC-7) - the returned plan simply has fewer placements than "winning"
    slots in that case. No socket calls, no Ableton connection - purely a
    planning function.
    """
    chops = list(available_chops)
    chops.reverse()
    placements: list[dict] = []

    tracks: dict[int, list[tuple]] = {}
    for track_index, clip_index, scene_index in eligible_slots:
        tracks.setdefault(track_index, []).append((clip_index, scene_index))

    for track_index, slots in tracks.items():
        slots.sort(key=lambda s: s[1])  # ascending by scene_index
        for clip_index, scene_index in slots:
            if not chops:
                break
            probability = scene_fill_probability(scene_index, total_scenes)
            if rng.random() >= probability:
                break  # stop this track's remaining (deeper) scenes - no gaps
            file_path = chops.pop()
            placements.append({
                "track_index": track_index,
                "clip_index": clip_index,
                "file_path": file_path,
            })
        if not chops:
            break

    return placements
