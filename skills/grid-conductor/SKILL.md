---
name: grid-conductor
description: "Conversational control for a populated Session View grid (built by the Phase 7 grid-population pipeline): trigger build/drop/breakdown structural moments and refresh content on demand, layered on top of native Ableton Follow Actions. Does not configure Follow Actions itself — that stays a manual, one-time GUI step (not scriptable via the Live API)."
genre: techno, house, breakbeat, edm
---

# Grid Conductor

## 1. When to Use This Skill

Trigger phrases: "build the energy", "trigger a build", "fire the drop", "trigger a breakdown", "refresh the grid", "add variation", "mutate the grid".

This skill assumes a grid already exists (populated via `scripts/populate_grid.py`, Phase 7) with Follow Actions already set on the tracks (a one-time manual GUI step — "Follow - Any" via Shift+Select All in Ableton; this is not scriptable via the Live API and this skill never attempts to set it). Follow Actions already handle random inter-clip variety within each track on their own. This skill adds what Follow Actions can't do: intentional structural shape (build/drop/breakdown) and content mutation, driven by natural language.

## 2. State-First Requirement

Before doing anything, read the grid as it actually exists right now — never assume a fixed scene layout or fixed track count:

1. `get_session_info` — confirms tempo and overall track count.
2. `get_track_info` for each track, filtered to `is_audio_track: true` (same filtering `scripts/populate_grid.py` uses) — for each audio track, note its `clip_slots` and which are filled (`has_clip: true`).

Because 07-02's population script fills each track **contiguously from scene 0 downward** (no gaps, by design), the state you read back tells you exactly how deep each track's content goes. Different tracks can have different depths — always compute from what you just read, never hardcode a scene number.

## 3. Density Mapping

Since every track's filled content starts at scene 0 and is denser near the top:
- **Scene 0 (or the shallowest filled scene across tracks)** = the grid's fullest, most-energetic moment — most or all tracks have content there.
- **The deepest scene that is still filled on at least one track** = the sparsest moment — few tracks reach that far.

For the general energy/content vocabulary behind "build", "drop", "breakdown" (what should be playing, roughly, at each kind of moment), reuse [arrangement-coach's Section Templates](../arrangement-coach/SKILL.md#2-section-templates) rather than re-deriving genre-specific energy curves from scratch — that table already encodes this project's genre knowledge. This skill's own job is narrower: translate that vocabulary into *which scene to fire on this specific, currently-existing grid*.

## 4. Trigger Behaviors

**"fire the drop" / "build the energy":**
```
fire_scene(scene_index=<shallowest filled scene, usually 1>)
```
Fires the grid's fullest moment.

**"trigger a breakdown":**
```
fire_scene(scene_index=<deepest scene still filled on at least one track>)
```
Fires the sparsest moment — expect several tracks to go silent since they have no content that deep.

**"build" / "buildup" (a short progression, not an instant jump):**
Fire a sparser scene first, briefly narrate what's happening, then fire a denser scene moments later — e.g. fire a mid-depth scene, then fire scene 0/1 shortly after. This is two sequential `fire_scene` calls, not a single call.

**"refresh the grid" / "mutate the grid" / "add variation":**
For a **small subset** of already-filled slots (not all of them — refreshing everything defeats the point of a persistent grid), per selected slot:
```
delete_session_clip(track_index, clip_index)
create_session_audio_clip(track_index, clip_index, file_path=<a freshly selected chop>)
```
New chops can come from existing files already in `scripts/grid-chops/` that aren't currently placed anywhere, or by calling `scripts/loop_selector.py`'s `discover_loops` / `scripts/audio_slicer.py`'s `slice_to_one_bar_chops` directly if that pool is exhausted.

**Critical constraint on which slots to refresh:** only refresh from the **bottom** of each track's contiguous fill **upward** — i.e. the deepest (last-filled) slot in a track first, then work upward if refreshing more than one slot per track. Never refresh a slot in the *middle* of a track's filled block. Removing a middle slot orphans every clip below it from Follow Action — confirmed live (not just theorized) during 07-03's checkpoint: `delete_session_clip` now refuses this automatically and returns a clear error if any slot after the target still has a clip, as a backstop, but the deletion order above should still be followed deliberately rather than relying on the guard to catch mistakes. Always re-check `get_track_info` after a refresh to confirm the track's filled scenes are still an unbroken, contiguous run starting from its shallowest scene.

<!-- checkpoint-fix-added: real permanent capability boundary discovered live during 07-03's checkpoint -->
**Follow Action must be manually reapplied after every refresh.** A newly created clip from `create_session_audio_clip` has no Follow Action set — this is not scriptable via the Live API (confirmed: neither `Clip` nor `ClipSlot` exposes any follow-action property), so there is no way to carry it over programmatically. After any refresh, always tell the user explicitly which track(s)/slot(s) need Follow Action reapplied manually (select the new clip(s), reapply "Follow - Any" the same way as the original one-time setup) — do not silently leave a refreshed slot without Follow Action, since it would sit inert once Follow Action reaches it from elsewhere in the track.

## 5. Don'ts

- Don't call `fire_scene` without checking the response's `was_empty` field first (or reading current state before firing) — if the target scene is empty, warn the user that the requested drop/breakdown would be silent rather than firing it anyway.
- Don't refresh a slot from the middle of a track's contiguous fill — always the deepest (bottom) filled slot first, to preserve the no-gap guarantee. `delete_session_clip` now enforces this automatically, but don't rely on the guard instead of following the rule deliberately.
- Don't forget to tell the user a refreshed clip needs Follow Action manually reapplied — it can never carry over automatically (not scriptable via the Live API), and this is easy to silently forget.
- Don't assume scene numbering is fixed across different grid populations — always read current state (`get_track_info`) before computing "dense" vs. "sparse", since a fresh `populate_grid.py` run can produce a different shape.
- Don't attempt to configure Follow Actions programmatically — confirmed not exposed by the Live API (neither `Clip` nor `ClipSlot` has any follow-action property); it stays a manual GUI step the user does once.
- Don't refresh or fire scenes on MIDI tracks — this skill, like the rest of Phase 7, only targets audio tracks (`is_audio_track: true`).
