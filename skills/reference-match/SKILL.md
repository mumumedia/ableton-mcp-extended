---
name: reference-match
description: Use when the user references another track they want to emulate the vibe/sound of. Examples - "make this sound like Ólafur Arnalds", "I want a Tame Impala vibe", "match the mix of Kendrick's Money Trees". Translates artist/track references into actionable production decisions.
---

# Reference Match

Translate a reference track or artist into concrete production choices. We do **not** download or analyze copyrighted audio. We use known sonic signatures and the user's own ears.

## Workflow

### 1. Identify the reference

Ask if not given: "Which track or artist? And which aspect — the arrangement, the mix, the sound design, or the overall vibe?"

### 2. Pull the sonic signature from common knowledge

Map the reference to its known characteristics. Examples:

| Reference | Signature |
| --- | --- |
| **Ólafur Arnalds** | Felt piano, string ensemble (often Spitfire), tape saturation, slow tempo (60-80), minor key, sparse arrangement, long reverb tails, microphone proximity sound |
| **Tame Impala (Currents-era)** | LinnDrum patterns, OP-1 synths, heavy chorus on guitar, vocoded vocals, sidechained bass, 60-90 BPM, vintage drum saturation |
| **Bonobo** | Live percussion + electronic drums, jazz harmony, vinyl crackle textures, mid-tempo (90-110), wide stereo, heavy use of sample chops |
| **Burial** | Vinyl/cassette texture, rain/atmosphere, pitched-up vocal samples, sub bass, garage-2step rhythm, lo-fi hihats, minor 7 chords |
| **Kendrick (DAMN era)** | 808 sub, trap hi-hats, jazz samples, vocal layering, heavy compression, mid-side EQ for vocal width |
| **Billie Eilish (early)** | Whisper vocal up close, sparse 808, finger snaps, sub-heavy mix, heavy automation, breath sounds intentionally left in |
| **Skrillex** | Heavy modulation on bass (vocal-formant LFOs), drops with stutter edits, 14k+ shimmer on leads, super-wide stereo, side-chained pump |
| **Hans Zimmer** | Massive low brass (often layered with synth), Trinity choir (low + bright), pulsing ostinatos, slow chord swells, 1-second+ reverb tails |
| **Fred again..** | Vocal samples from voice notes/social media (heavy reverb, long decay, 35–45% wet); sparse piano melody (2–3 notes/bar, mid-register C4–G4, varying velocity 55–90, never block chords); half-time snare, syncopated kick, 8th-note hats with strong velocity variation (alternating ~75/38); sidechain kick→pad is the defining texture; warm bass boosted ~110–120Hz; 108–130 BPM; Am/minor keys; long sparse intro (texture/arp only); emotional breakdown = piano + vocal only, no drums; no hard EDM drops |
| **Lo-fi hip hop (Lofigirl-style)** | Wurlitzer/Rhodes, jazz chords, vinyl crackle, tape saturation, 70-90 BPM, 50% wet drums, swung 16ths |
| **Sam Barker** | Eurorack modular synthesis, found-object/everyday-item percussion, old step sequencers (ARP, Roland), Berlin industrial grey aesthetic, cold mechanical textures that evolve slowly, polyrhythmic patterns, modal/atonal harmony, 120–135 BPM (or half-time feel at 60–70), minimal arrangement with long patient builds |

### 3. Translate to action

For each aspect the user cares about, propose moves:

#### Arrangement
- Match section structure (Bonobo = long intros; Skrillex = constant motion)
- Match density (Billie = sparse, Skrillex = dense)

#### Mix
- LUFS target (lo-fi/Bonobo: -10 to -8 LUFS, modern pop: -8 to -6, cinematic: -16 to -14)
- Stereo width (cinematic: narrow; EDM: very wide)
- Frequency balance (trap: heavy 50-80Hz; folk/acoustic: balanced midrange)

#### Sound design
- Pick instruments matching the era/style
- Use the right synth patches (vintage analog vs modern digital)
- Match drum kit character (vinyl sample vs modern punchy)

#### Effects
- Reverb type (Hall for cinematic; Plate for vocals; Spring for surf-rock; Room for tight modern pop)
- Tape/vinyl saturation (essential for Bonobo, lo-fi, Tame Impala)
- Chorus (Tame Impala, dream pop, '80s)

### 3b. Hybrid references — tempo negotiation

When two references imply conflicting tempos (e.g. Zimmer = 60–80 BPM cinematic vs. Barker techno = 120–135 BPM industrial), don't commit to a tempo upfront. Instead:

1. Propose a midpoint and flag the tension: *"These references live at very different tempos — suggest starting at X, but let the rhythm element set it once you hear it."*
2. Build the harmonic/textural layers first at the midpoint.
3. Once the drum/rhythm element is in, let the user react to tempo feel and adjust from there.

If the user introduces a new genre or reference mid-session (e.g. "can we add a DnB beat?"), restart the top-3 process for that new element rather than shoehorning it into the original brief.

### 3c. Lead sound design sub-loop

The lead carries the most emotional weight in a hybrid track and typically takes more iteration than any other element. Treat it as a distinct three-pass problem — don't try to resolve all at once:

1. **Character/timbre** — what kind of sound (aggressive, sparkly, textural, melodic)?
2. **Register** — where does it sit relative to the pad and bass?
3. **Articulation** — short stabs, flowing long notes, or something in between?

Each pass should be a single listening decision. If the user says "not working" after a pass, ask which of the three dimensions is the problem before rebuilding.

### 4. Ask the user to listen and direct

Don't apply everything blindly. Pick the **3 most distinctive** elements of the reference and propose them first:

> *"Top 3 Ólafur signatures I'd start with: (1) felt piano via Spitfire Originals or stock Grand Piano with the lid closed setting + tape sat; (2) slow swelling string pad with 2-second attack + reverb send 40%; (3) tempo 70 BPM, minor key, 4/4 but with rubato feel via velocity-driven micro-timing. Apply these first, listen, then iterate?"*

### 5. Iterate

After the user listens, refine based on what's still wrong. References are inherently approximate — embrace the iteration loop.

## Don'ts

- Don't claim to "exactly clone" anyone's sound. We approximate the recipe.
- Don't download or process copyrighted audio.
- Don't recommend specific sample packs unless they're public (Splice, Output) and the user has them.
- Don't apply more than 3 reference moves before letting the user listen.
- Don't guess or hand-construct a browser URI for a named preset — resolve it via `get_browser_items_at_path` first (stock device URIs like `query:Synths#Wavetable` or `query:Audio Effects#EQ Eight` are static and safe to use directly).

## When the reference is unfamiliar to you

If you don't know the reference: ask the user to describe what they like about it. ("Is it the drums? The vocal effect? The arrangement?") Then apply the technique that matches their description — you don't need to know the artist to translate "warm, lo-fi, jazzy chords" into action.
