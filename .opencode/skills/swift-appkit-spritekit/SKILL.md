---
name: swift-appkit-spritekit
description: Repository-specific Swift/macOS conventions for this app (SwiftPM, AppKit, SpriteKit, WebKit). Use when writing or reviewing any Swift code, building, bundling, or debugging this desktop companion app.
license: MIT
compatibility: opencode
---

# Swift / AppKit / SpriteKit Conventions (this repo)

A native macOS desktop companion: SpriteKit rendering inside borderless
AppKit panels, menu-bar extra, WebKit-based chat, SwiftPM packaging.

## Toolchain constraints (hard rules)

- **No `@State`/`@Observable` macros** — the Command Line Tools toolchain
  cannot resolve SwiftUIMacros. Use classic `ObservableObject` + `@Published`
  + `@ObservedObject` (see `AppPreferences`).
- Use `rtk` as the shell wrapper for repo commands (`rtk swift build`,
  `rtk git add`).
- Build: `swift build` (debug). There is NO working `Scripts/bundle.sh` —
  assemble `Bill.app` manually:
  `.build/debug/Bill` → `Contents/MacOS/Bill`, `Resources/Info.plist`,
  `Resources/AppIcon.icns`, every `.build/debug/*.bundle` →
  `Contents/Resources/`, then `codesign --force --sign -`.
- Ad-hoc signing invalidates Accessibility / Screen Recording permissions
  on every rebuild — reactions relying on them silently stop working until
  re-granted.
- Run the app from `/tmp/bill-app/Bill.app` (copy the assembled bundle
  there; do not run the raw executable).

## Architecture map

- `Animation/` — `BillState` (state space), `AnimationClip` (texture track
  + transform track), `BillStateMachine` (play/settle lifecycle),
  `AnimationClipLibrary` (Bill's clip table), `BillRigNode`, palette.
- `Packs/` — `CharacterDefinition` + `CharacterRoster` (+`GeneratedRoster`),
  `CharacterSpriteCatalog` (lazy per-family texture loading; manifest:
  `{canvas: [w,h], idle_h: Int, families: {name: count}}`),
  `CharacterAnimationLibrary` (state→family resolution, workbench-label
  alternatives, per-family facing/world labels), `CompanionController`,
  `EnemySpawnController`, `DialogueVoice`.
- `CharacterEngine/` — ambient beats, rare events, showcase rotation,
  `ReactionRouter` (event→state+line), dialogue contextualization.
- `Roaming/` — `GravitySimulator` (full platformer physics; scale field
  converts body-units→points), `RoamingController` (goals/steps/top-down
  mode), `WindowTopology`.
- `UI/CharacterWindow/` — the panel, shared-canvas geometry
  (`geometry(for:companions:)`), per-character sizing, companion layout.
- `Settings/` — `AppPreferences` (UserDefaults-backed), `SettingsView`
  (sidebar pattern), animation browser/selector.

## Sprite/animation rules

- Every character renders at ≈185pt visible height:
  `displayScale = 185 / idle_h`; windows are sized from
  `canvasSize * displayScale` (+12pt headroom; bark panel expands to 700).
- Shared-canvas frames: `resize: false` in every `SKAction.setTexture/
  animate` — `resize: true` stomps horizontal flips every frame (known
  shipped bug, see `AnimationClip.textureAction`).
- Never wrap a single-frame/zero-duration action in `repeatForever`
  (hard hang — see `buildActions`).
- Pixel art: textures use `.nearest` filtering everywhere.

## Behavior rules

- Bill mirrors via `xScale` sign (his art is authored left-facing).
  Pack characters never auto-mirror — sheets carry real directional rows.
- Grounded characters (UT/DR/OneShot) never experience gravity; 4-direction
  sheets roam top-down. Knight/Hornet keep full physics.
- Red-chaos families (rampaging etc.) stay out of ambient rotations; the
  Settings deselector (`disabledStateIDs`) must gate EVERY automatic path
  including roaming `.running`.

## Verification

- `swift build` must pass with zero new errors.
- `swift Scripts/validate_sprite_assets.swift` must exit 0 (the sprite
  validation gate — no XCTest in this toolchain).
- Verify runtime only via an actually-running app instance; never claim
  visual behavior was verified from code reading alone. Screenshot checks
  require Screen Recording permission (revoked per rebuild).
