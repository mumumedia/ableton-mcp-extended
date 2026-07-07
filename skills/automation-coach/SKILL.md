---
name: automation-coach
description: "Guides parameter automation in Ableton — when to automate, which parameters, and how to use manage_clip_automation with envelope shapes for filter sweeps, volume rides, effect throws, and evolving textures."
---

# Automation Coach

## 1. When to Automate

| Moment | Target Parameter | Shape | Effect |
|--------|-----------------|-------|--------|
| Buildup (4–16 bars) | Filter cutoff | Linear ramp up | Rising tension |
| Drop arrival | Reverb wet | Step down to 0 | Snaps mix dry |
| Breakdown | Track volume | Linear ramp down | Space, intimacy |
| Fill (1–2 bars) | Delay feedback | Linear ramp up | Echo buildup |
| Long evolve | LFO rate or depth | Linear ramp | Continuous motion |

## 2. Tool Workflow

1. `get_device_parameters` on the target device/track — note the `parameter_name` and current value for the parameter you want to automate
2. `create_clip` in the target track + slot at the required length (e.g., 16.0 for a 4-bar automation clip, 64.0 for 16 bars)
3. `manage_clip_automation` with action `add_point` for each envelope breakpoint:
   ```
   track_index: <1-based track number>
   clip_index: <1-based slot number>
   action: "add_point"
   parameter_name: <exact name from get_device_parameters>
   time_in_beats: <position in clip, float>
   value: <normalized 0.0–1.0>
   ```
4. Repeat `add_point` calls to build the full envelope shape — two points for a ramp, three for hold-then-release, etc.

## 3. Envelope Shapes

| Shape | Points | Typical Use |
|-------|--------|-------------|
| Linear ramp up | (0.0, 0.05) → (end, 1.0) | Filter sweep, reverb build |
| Linear ramp down | (0.0, 1.0) → (end, 0.0) | Volume fade, filter close |
| Step change | (beat, low) immediately followed by (beat+0.01, high) | Effect throw, snap open |
| Hold then release | (0.0, high) → (end−0.5, high) → (end, low) | Reverb tail, decay |
| Single-point set | (0.0, value) | Lock a parameter for the clip duration |

## 4. Genre-Specific Patterns

**House/Techno buildup (16 bars = 64 beats):**
- Filter cutoff: add_point at time 0.0, value 0.05; add_point at time 64.0, value 1.0
- Result: full filter sweep from nearly-closed to wide-open over 16 bars

**Drop (first beat after the buildup):**
- Reverb wet: add_point at time 0.0, value 0.75; add_point at time 0.1, value 0.05
- Filter cutoff: add_point at time 0.0, value 1.0 (reset to open at drop)

**Breakdown (8 bars = 32 beats):**
- Pad volume: add_point at time 0.0, value 0.85; add_point at time 32.0, value 0.3
- Delay feedback: add_point at time 0.0, value 0.2; add_point at time 16.0, value 0.65

## 5. Value Notes

- All values are normalized 0.0–1.0 regardless of what the parameter displays in Ableton (e.g., a filter showing 20Hz–20kHz still uses 0.0–1.0 in the API)
- Ableton clamps values at [0.0, 1.0] — any value outside this range is rejected
- `time_in_beats` must be ≥ 0 — negative positions are rejected
- `manage_clip_automation` operates on Session View clip automation envelopes; arrangement automation lanes require manual editing in Ableton's Arrangement View

## 6. Don'ts

- Don't automate more than 1–2 parameters at a time — stacked automation across many parameters muddies the arrangement and makes mix decisions harder to undo
- Don't use step changes for volume fades — abrupt volume jumps sound robotic; use linear ramps (minimum 2–4 beats)
- Don't start writing add_point calls without first running `get_device_parameters` — parameter IDs are device-specific and change when you load a different preset
- Don't forget that automation in a Session clip only plays when that clip is playing — it won't drive arrangement transitions automatically
