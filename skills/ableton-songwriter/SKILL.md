---
name: ableton-songwriter
description: Professional songwriting workflow for Ableton: structured intake, production brief, composition/arrangement execution, plugin-aware instrument loading, quick mix, QA, and revision handoff.
---

# Ableton Songwriter

## Objective
Convert an open-ended songwriting request into a playable, editable Ableton draft with:
- coherent song form,
- intentional section contrast,
- viable instrumentation choices,
- and a minimal but professional gain/mix baseline.

This skill optimizes for production momentum and clean revision cycles, not final mastering.

## Use This Skill When
- The user asks to compose, arrange, rewrite, or “start a song” in Ableton.
- The user gives broad direction and expects structured clarification.
- The user wants a practical draft with a fast polish pass.

## Do Not Use This Skill When
- The task is purely technical/debugging (no songwriting intent).
- The user only asks for a single isolated operation (for example, “rename track 3”).
- The user explicitly asks for free-form brainstorming with no DAW execution.

## Operating Standards
- Keep decisions explicit and traceable in a compact production brief.
- Resolve high-impact unknowns first; avoid over-questioning.
- Protect user project state (never destructive by default).
- Prefer repeatable arrangement patterns over novelty for first drafts.
- Keep the first pass modular so sections can be swapped or extended quickly.

## Workflow
1. Parse request and extract fixed constraints.
2. Run targeted intake for missing high-impact decisions.
3. Emit production brief and proceed unless user asks to review first.
4. Build section foundations (rhythm, harmony, hook) in Session or Arrangement.
5. Arrange into form with section contrast and transitions.
6. Apply quick mix baseline and playback-ready positioning.
7. Return structured handoff with revision options.

## Intake Protocol
- Use MCQ format with `1. 2. 3.` numbering when clarification is needed.
- Ask exactly 3 questions first; ask at most 2 follow-ups.
- Skip any item already answered by user constraints.
- If user asks for speed, ask only:
  - genre family,
  - energy target,
  - section length target.
- Use [intake-mcq.md](references/intake-mcq.md) for full option bank.
- If structured input tooling is available, use it; otherwise ask plain-text MCQ.
- Always include one safe default option.

## Production Brief Contract
Before building, output a concise brief in this schema:

```md
Production Brief
- Genre/Reference:
- Mood/Intent:
- BPM/Groove:
- Key/Mode:
- Song Form:
- Section Lengths:
- Instrument Priorities:
- Vocal Plan:
- Mix Target:
- Constraints/Do-Not-Do:
```

Proceed automatically after brief unless user requests approval gate.

## Build Standards in Ableton

### 1) Session Setup
- Set tempo immediately from brief.
- Select one template from [song-recipes.md](references/song-recipes.md).
- Name tracks by role, not instrument brand (example: `Lead Synth`, `Drum Bus`).
- Keep routing simple on first pass; avoid deep bus complexity.

### 2) Instrument Strategy
- Try user-owned external plugins when relevant and available.
- Before calling `load_instrument_or_effect` for any stock/library instrument or preset, first resolve its real `uri` via `get_browser_items_at_path` (drill down from `Instruments` or `Sounds`) or `get_browser_tree`. Never construct or guess a URI from memory or convention — the real scheme is `query:Synths#...:FileId_NNNN` (or similar live-browser output), not a hand-built path like `query:LivePacks#www.ableton.com/0:Devices:Instruments:...`.
- If external plugins are unavailable, fallback to stock devices and state fallback.
- For electronic/hybrid leads, prioritize modern synth clarity before layering.
- For acoustic-forward requests without audio assets, use MIDI placeholders with clear naming.

### 3) Composition Strategy
- Build at least two distinct sections (A/B) with different density and contour.
- Ensure each section has:
  - rhythmic anchor,
  - harmonic movement,
  - top-line hook or motif.
- Keep early motifs short and memorizable; avoid over-ornamentation.

### 4) Arrangement Strategy
- Minimum draft length: 16 bars unless user requests shorter.
- Preferred default: 32 bars with intro + A + B.
- Add transitions at section boundaries (drum fill, riser, filter move, dropout).
- Place cue points at major sections for fast iteration.

### 5) Quick Mix Baseline
- Set faders for immediate readability (no clipping on master).
- Keep low-end mono/center-aligned.
- Apply light panning/width to support layers only.
- Use conservative dynamics control for punch, not loudness.
- Leave headroom for later mix/master passes.

### 6) Playback Behavior
- Set playhead to first actionable section start.
- Do not start playback unless user asks.

## Plugin-Aware Policy
- If plugin listing/loading tools exist, check availability before assuming plugin usage.
- When user asks for named plugin loading, prefer exact match if ambiguity exists.
- If multiple close matches exist, request specificity instead of guessing.
- If a load fails, do not retry variations of the same guessed URI. Browse the nearest matching folder via `get_browser_items_at_path` to find a real match; only if that also fails, continue with best available substitute and report it clearly. (This one-step browse fallback is distinct from the retry-loop constraint in Guardrails, which governs platform-blocked operations like final track deletion — it does not apply to instrument/preset loading.)

## Guardrails
- Never delete/overwrite user material without explicit confirmation.
- If set already contains substantial content, ask whether to append or replace target region.
- If operations are blocked by platform rules (for example, final track deletion), stop retry loops and state constraint.
- Keep progress updates brief and factual.

## Quality Checklist (Before Handoff)
- Section contrast is audible (A vs B not redundant).
- Track naming is clear and role-based.
- No obvious timing/form misalignment across section boundaries.
- Master output is not clipping.
- User constraints have been respected or explicitly called out as unmet.

## Handoff Format
Return a short structured recap:
- What was built (sections, bars, key tracks).
- What plugins/instruments were used (including fallbacks).
- Current limitations/assumptions.
- 2-4 concrete revision options.

## Revision Loop Rules
- On revision requests, preserve successful sections and change only requested scopes.
- Reuse existing motif/harmony where possible to maintain identity.
- If revision alters core brief dimensions (genre, BPM, key), emit updated brief first.

## Worked Example
Full example (intake → brief → build plan → handoff) for a melodic house request: [worked-example.md](references/worked-example.md).

## References
- Intake prompts and option bank: [intake-mcq.md](references/intake-mcq.md)
- Genre defaults and templates: [song-recipes.md](references/song-recipes.md)
- Full worked example: [worked-example.md](references/worked-example.md)
