---
name: sprite-asset-mandate
description: Authoritative workflow for integrating user-labeled sprite assets in this repo. Use whenever touching sprite sheets, frame extraction, animation mappings, packs_manifest.json, character rosters, or any sprite-processing script. The user's workbench labels are the single source of truth — never guess frame locations or invent animation mappings.
license: MIT
compatibility: opencode
---

# Sprite Asset Mandate

The user has ALREADY labeled every sprite frame by hand (names + pixel rects)
in `build-assets/workbench_export.json` and pre-organized extracted folders
under `build-assets/extracted/`. That work is authoritative. The recurring
failure mode in this repo has been guessing, misreading, or overriding those
labels. This skill prevents that class of bug permanently.

## Non-negotiable rules

1. **Read the labels first.** `build-assets/workbench_export.json` is the
   source of truth for the 12 workbench characters. Its entries are:
   `{character: {label: {frames: [{x, y, w, h}...], sheet: "<filename>"}}}`
   where `x/y/w/h` are pixel rects (top-left origin) inside
   `~/Downloads/sprite sheets/<filename>`, and frame ORDER inside
   `frames` is the intended playback order (click order = frame order).
2. **Never invent mappings.** If a state needs a family and no label
   matches, leave it empty/fallback — never substitute a visually similar
   family silently.
3. **Apply background removal.** Sheets are NOT transparent: Undertale
   sheets use the magenta/purple chroma convention, others solid
   backgrounds. Port the exact flood-fill logic from
   `Scripts/sprite-labeler/workbench.py` (`flood_bg`) when cropping.
   Cropping without background removal ships broken sprites.
4. **Bottom-anchor every frame.** Content must sit flush against the
   canvas bottom (feet at y=0) or the character floats.
5. **Coordinate traps:** PIL `crop` takes `(left, upper, right, lower)` —
   NOT `(x, y, w, h)`. macOS screen coordinates grow UPWARD (y+ = up).
   Sprite sheets grow DOWNWARD. Walk families: "up" = back view (away),
   "down" = front view (toward), per the user's labels.
6. **Never mirror pack-character art automatically.** Left/right are
   separate sheet rows for most characters. Only the user's Settings
   "Facing: right (mirror)" label may flip a family.
7. **Never overwrite originals.** Never delete/rename files in
   `build-assets/` or `~/Downloads/sprite sheets/`. Processed output goes
   only to `Sources/Bill/Resources/Packs/`.
8. **Regenerate the manifest from disk.** `packs_manifest.json` is
   DERIVED — always rebuild it by scanning the files on disk
   (`Scripts/rebuild_from_workbench.py`), never hand-edit it. Roster
   `canvasSize`/`displayScale` derive from the manifest (target visible
   height ≈185pt: `scale = 185 / idle_h`).

## Workflow (Phases)

1. **Inventory** — list every sheet the export references, its pixel size,
   and every label + rect. Verify every rect lies within sheet bounds.
2. **Extract** — crop each rect (converting to `l, u, r, l+h`), remove the
   background, bottom-anchor into the character's shared canvas.
3. **Verify** — run `swift Scripts/validate_sprite_assets.swift` (exit 0)
   which checks: rects in bounds, manifest==disk, roster==manifest,
   bottom-anchoring, background rings removed, and directional walk
   families existing per character.
4. **Integrate** — resolveFamily maps states to label variants; any new
   label spelling must be added to `CharacterAnimationLibrary`'s
   alternatives, not hardcoded at call sites.

## Red flags

- A character "invisible" → manifest decode mismatch (families are
  `[String: Int]`, NOT nested objects).
- Character floats above the floor → frames not bottom-anchored, or the
  window has headroom (window height = canvas render + 12, bark expands).
- Wrong-direction walking → walkDirection sign or `walkAxis` vertical
  sign inverted; up/down are the user's labeled up/down rows.
- Background boxes around sprites → crop skipped background removal.
