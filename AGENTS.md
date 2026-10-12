# Bill Cipher Companion — Agent Rules

Native macOS desktop companion (SwiftPM, macOS 14+, AppKit + SpriteKit +
WebKit). Multi-character pack system with user-labeled sprite assets.

## Skills (load before acting)

If a task matches a skill, invoke it with the `skill` tool BEFORE writing
code. Skills live in `.opencode/skills/`:

- **Any sprite/animation/asset work** → `sprite-asset-mandate` (MANDATORY —
  the user's workbench labels in `build-assets/workbench_export.json` are
  the source of truth; never guess frames, mappings, or skip background
  removal/bottom-anchoring).
- **Any Swift/build/bundle work** → `swift-appkit-spritekit` (toolchain
  constraints, architecture map, known traps).
- Feature / significant change → `spec-driven-development`, then
  `planning-and-task-breakdown`.
- Implementing → `incremental-implementation` + `test-driven-development`.
- Bug / wrong behavior → `debugging-and-error-recovery` (root cause first:
  reproduce → localize → reduce → fix → guard).
- Before declaring done → `code-review-and-quality`.
- Refactor (no behavior change) → `code-simplification`.
- Framework/API uncertainty → `source-driven-development` (verify against
  official Apple docs; cite; flag unverified).
- Touching input/permissions/WebKit/network → `security-and-hardening`.
- Performance-sensitive paths (timers, texture loading, 24/7 runtime) →
  `performance-optimization`.

## Mandatory quality gates

Never claim a step passed unless it actually ran and passed.

**Before coding:** state the requirement, locate the existing
implementation, list assumptions, identify regression risks, define
observable acceptance criteria.

**During:** smallest complete implementation; follow existing conventions;
no placeholder/mock/TODO deliverables unless explicitly requested; no
unrelated changes; add/update tests for logic you add or fix.

**After (all substantial tasks):**
1. `swift build` — zero errors.
2. `swift Scripts/validate_sprite_assets.swift` — sprite validation must
   exit 0 (rects, manifest↔disk, roster↔manifest, bottom-anchoring,
   backgrounds, directional walks).
3. Independent review of the actual diff (adversarial: correctness,
   edge cases, lifecycle, regression risk).
4. Runtime verification when the environment permits (launch the bundled
   app; state explicitly when visual checks were NOT possible).
5. Fix confirmed defects and re-run affected checks before reporting done.

## Hard project constraints

- Toolchain: **no `@State`/`@Observable` macros** — use `ObservableObject`.
- Bundle assembly is manual (see `swift-appkit-spritekit`); `bundle.sh` is
  broken.
- Sprite pipeline: run `Scripts/rebuild_from_workbench.py` (never
  `process_pack_sprites.py` — its mappings are obsolete and it clobbers
  user labels). The manifest and roster geometry are derived artifacts.
- Never overwrite the user's original assets (`build-assets/`,
  `~/Downloads/sprite sheets/`).
- Commits: only when the user asks; conventional, concise messages.
- Subagent infra may be unavailable ("Cannot connect to API") — if a
  delegate fails, do the work solo rather than skipping the step.

## Definition of done

A task is done when: it builds, tests pass, the change was reviewed, the
feature actually works in the running app (or the inability to verify is
explicitly reported), and no half-finished wiring remains.
