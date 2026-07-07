---
name: genre-edm-production
description: "Genre-aware EDM production guide for Ableton MCP. Covers session setup, drums, bass, pad, and lead/texture layers with tool workflow, drum MIDI map, and mix balance defaults."
genre: edm
bpm_range: 70–145
---

# Genre EDM Production

## 1. Genre Reference

| Style | BPM | Key Modes | Character |
|-------|-----|-----------|-----------|
| Lo-fi Downtempo | 70–95 | Minor, Dorian | Warm, nostalgic, humanized feel |
| Deep House | 118–124 | Minor 7, Dorian | Groove-forward, warm pads |
| House | 124–128 | Minor, Major | Four-on-the-floor, vocal energy |
| Techno | 130–145 | Minor, Phrygian | Dark, industrial, hypnotic |

## 2. Workflow

**Step 1 — Setup**
`get_session_info` to read current state. `set_tempo` to genre BPM. Aim for 4–6 MIDI tracks: Drums, Bass, Pad, Lead/Arp, and optionally Piano/Keys or a Texture layer. Read [../_shared/genre-defaults.md](../_shared/genre-defaults.md) now — Steps 2 and beyond need its MIDI note numbers and velocity values.

**Step 2 — Drums**
`load_drum_kit` (for a kit preset) or `load_instrument_or_effect` with a `uri` from `get_browser_items_at_path` path `Instruments/Drum Rack`. `create_clip` at length 16.0 (4-bar loop). `add_notes_to_clip` using the MIDI Map table below. Use 1 bar = 4.0 beats.

**Step 3 — Bass**
`get_browser_items_at_path` path `Sounds/Bass` — recommended: "Sub Mellow", "808 Pure", "Basic Sub Sine", "Sub Cave Bass". `load_instrument_or_effect` with URI. Write root-note-per-bar pattern: one note per chord, held 3.8 beats, starting at beat 0, 4, 8, 12 of a 4-bar clip. Place bass in 2nd octave (A2=45, etc.).

**Step 4 — Pad/Chord**
`get_browser_items_at_path` path `Sounds/Pad` — recommended: "Daysleeper Swells Pad", "Warm Analog Pad", "Warm Bubbly Pad". `load_instrument_or_effect`. Write open triads in 3rd–4th octave (A3–G4 range), vel 65, duration 3.8–3.9 beats. Keep pad below the lead/piano register to avoid register clash.

**Step 5 — Lead/Texture**
`get_browser_items_at_path` path `Sounds/Synth Rhythmic` — recommended: "Cloud Cover Arp", "Lightest Night Arp", "Shimmer Arp". `load_instrument_or_effect`. Write ascending chord-tone arp, 8th notes (0.5 beat spacing), vel 70–80 on root notes, vel 65 on upper tones.

## 3. Drum MIDI Map

See [../_shared/genre-defaults.md](../_shared/genre-defaults.md) for the standard 909/808 note layout (verify your specific kit's pad assignments before writing notes).

## 4. Pattern Templates

1 bar = 4.0 beats · 4 bars = 16.0 beats · 8th note = 0.5 beats · 16th note = 0.25 beats

**Four-on-floor kick:** positions per bar: 0, 1, 2, 3. For a 4-bar clip write all 16 positions explicitly: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15. vel 110; dur 0.45.

**House clap/snare:** positions 1, 3 per bar (beats 2 and 4). vel 100; dur 0.45.

**8th-note hats:** every 0.5 beats from 0.0 to 15.5 (32 notes in a 4-bar clip). On-beat vel 85, off-beat vel 65; dur 0.2.

**Swing feel:** delay every 2nd 8th note (positions 0.5, 1.5, 2.5…) by +0.04 beats for a loose groove.

**Chord progression positions (4-bar clip):** bar 1 = 0.0 · bar 2 = 4.0 · bar 3 = 8.0 · bar 4 = 12.0.

## 5. Mix Balance Defaults

See [../_shared/genre-defaults.md](../_shared/genre-defaults.md) for velocity values by role (kick as loudest anchor, working downward).

## 6. Tool Notes

- Use `load_instrument_or_effect` with the `uri` field from `get_browser_items_at_path` to load any instrument or preset
- Run `get_browser_items_at_path` first to get a URI; copy the `uri` field from the result before calling load
- Audio tracks must be created manually in Ableton — Claude cannot create audio tracks via this MCP server
- Track colors must be set manually in Ableton
- For clip revision, create a new clip in the next available slot — existing clip notes cannot be deleted via MCP

## 7. Don'ts

- Don't stack pads in the same register as piano/keys — move one up or down an octave to avoid unison doubling (bass in 2nd octave, pad in 3rd–4th, piano in 4th–5th)
- Don't use velocity 100–127 on all elements — it kills dynamics and makes the mix flat
- Don't skip `get_session_info` at the start — you may have existing tracks that need renaming, not new ones
- Don't add notes to a clip slot that already has a clip — Ableton appends, it doesn't replace; use a new slot
