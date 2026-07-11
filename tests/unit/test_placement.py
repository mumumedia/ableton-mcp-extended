"""Unit tests for scripts/placement.py."""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from placement import (  # noqa: E402
    bpm_proximity_weight,
    plan_placements,
    scene_fill_probability,
    select_loops,
)


class TestBpmProximityWeight:
    def test_exact_match_scores_highest(self):
        assert bpm_proximity_weight(174.0, 174.0) == 1.0

    def test_half_time_relationship_scores_highest(self):
        # 87 BPM is half-time of a 174 BPM project - should score as well
        # as an exact match, not as a mismatch.
        assert bpm_proximity_weight(87.0, 174.0) == 1.0

    def test_double_time_relationship_scores_highest(self):
        assert bpm_proximity_weight(348.0, 174.0) == 1.0

    def test_unrelated_bpm_scores_lower_but_never_zero(self):
        weight = bpm_proximity_weight(93.0, 174.0)  # no clean relationship
        assert 0.0 < weight < 1.0

    def test_never_returns_zero(self):
        assert bpm_proximity_weight(1.0, 500.0) > 0.0


class TestSelectLoops:
    def test_returns_all_candidates_when_fewer_than_target(self):
        candidates = [{"bpm": 174.0}, {"bpm": 87.0}]
        rng = random.Random(42)

        result = select_loops(candidates, project_bpm=174.0, target_count=10, rng=rng)

        assert result == candidates

    def test_selects_exactly_target_count_when_enough_candidates(self):
        candidates = [{"bpm": float(120 + i)} for i in range(20)]
        rng = random.Random(42)

        result = select_loops(candidates, project_bpm=174.0, target_count=5, rng=rng)

        assert len(result) == 5

    def test_empty_candidates_returns_empty(self):
        rng = random.Random(42)
        assert select_loops([], project_bpm=174.0, target_count=5, rng=rng) == []


class TestSceneFillProbability:
    def test_monotonically_decreasing(self):
        total_scenes = 8
        probabilities = [scene_fill_probability(i, total_scenes) for i in range(total_scenes)]
        assert probabilities == sorted(probabilities, reverse=True)

    def test_first_scene_higher_than_last(self):
        assert scene_fill_probability(0, 8) > scene_fill_probability(7, 8)


class TestPlanPlacements:
    def test_early_scenes_fill_more_than_late_scenes(self):
        # 6 tracks x 8 scenes, all eligible, plenty of chops available.
        total_scenes = 8
        eligible_slots = [
            (track, clip, scene)
            for track in range(6)
            for scene in range(total_scenes)
            for clip in [scene]  # clip_index mirrors scene_index for this synthetic grid
        ]
        available_chops = [f"/chops/chop{i}.wav" for i in range(200)]
        rng = random.Random(7)

        placements = plan_placements(eligible_slots, available_chops, total_scenes, rng)

        early_count = sum(1 for p in placements if p["clip_index"] < total_scenes // 2)
        late_count = sum(1 for p in placements if p["clip_index"] >= total_scenes // 2)
        assert early_count > late_count

    def test_stops_gracefully_when_chops_exhausted(self):
        eligible_slots = [(0, i, 0) for i in range(50)]  # all scene 0 -> ~100% fill probability
        available_chops = ["/chops/only_one.wav"]
        rng = random.Random(1)

        placements = plan_placements(eligible_slots, available_chops, total_scenes=1, rng=rng)

        assert len(placements) <= 1

    def test_no_eligible_slots_returns_empty(self):
        rng = random.Random(1)
        assert plan_placements([], ["/chops/a.wav"], total_scenes=8, rng=rng) == []

    def test_no_track_has_a_gap(self):
        # Every track's placed clip_index values must be an exact contiguous
        # run starting from that track's lowest eligible scene - never a
        # filled slot below an empty one in the same track (AC-5c).
        total_scenes = 8
        eligible_slots = [
            (track, clip, scene)
            for track in range(6)
            for scene in range(total_scenes)
            for clip in [scene]
        ]
        available_chops = [f"/chops/chop{i}.wav" for i in range(200)]
        rng = random.Random(99)

        placements = plan_placements(eligible_slots, available_chops, total_scenes, rng)

        by_track: dict[int, list[int]] = {}
        for p in placements:
            by_track.setdefault(p["track_index"], []).append(p["clip_index"])

        for track_index, clip_indices in by_track.items():
            clip_indices.sort()
            expected = list(range(clip_indices[0], clip_indices[0] + len(clip_indices)))
            assert clip_indices == expected, (
                f"track {track_index} has a gap: {clip_indices}"
            )

    def test_deliberate_early_loss_stops_track_immediately(self):
        # scene_fill_probability(0, total_scenes) is always exactly 1.0
        # (progress=0 -> 1.0**1.5), so scene 0 can never lose - start this
        # track's eligible scenes at index 5/8 instead, where the
        # probability has decayed enough that a loss is achievable, and
        # confirm the very first losing roll stops that track immediately
        # (no deeper scene filled after it).
        total_scenes = 8
        start_scene = 5
        eligible_slots = [(0, scene, scene) for scene in range(start_scene, total_scenes)]
        available_chops = [f"/chops/chop{i}.wav" for i in range(200)]

        for seed in range(500):
            rng = random.Random(seed)
            if rng.random() >= scene_fill_probability(start_scene, total_scenes):
                losing_seed = seed
                break
        else:
            raise AssertionError("no losing seed found in range - adjust test")

        rng = random.Random(losing_seed)
        placements = plan_placements(eligible_slots, available_chops, total_scenes, rng)

        assert placements == []
