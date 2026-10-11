import SpriteKit

/// Maps the universal `BillState` space onto one character's sprite
/// families — the pack counterpart of `AnimationClipLibrary`.
///
/// Design rules, mirroring the ones that library learned the hard way:
///
/// 1. A non-continuous state always plays `loop: .once` so the state
///    machine's auto-settle timer arms (see `AnimationClipLibrary`'s
///    rule 1).
/// 2. Continuous loops that pingpong use `pingpongLoop` — never native
///    `.pingpong` — to avoid the turnaround stutter (rule 2).
/// 3. States without dedicated art degrade gracefully: they reuse the
///    character's closest family or fall back to transform-only clips on
///    the idle texture — exactly how Bill's `talking` worked before the
///    sheet audit found its frames. A character with fewer families than
///    Bill's 68 still reacts to EVERY trigger; the emotion just plays on
///    whatever pose fits.
@MainActor
struct CharacterAnimationLibrary {
    let catalog: CharacterSpriteCatalog

    init(catalog: CharacterSpriteCatalog) {
        self.catalog = catalog
    }

    // MARK: - Family resolution

    /// The family a state should play, before existence checks. Specials
    /// are per-character families that exist in some packs; the fallback
    /// ladder keeps every state resolvable.
    /// Resolves a state's intended family to whatever name this character
    /// actually uses. The workbench-labeled characters named their
    /// animations with game-natural names (down/left/right for directions,
    /// battle-idle for combat, etc.) — this maps them back.
    private func resolveFamily(_ requested: String) -> String? {
        // Direct match
        if !catalog.frames(requested).isEmpty { return requested }
        // Alternative names the workbench labels commonly use
        let alternatives: [String: [String]] = [
            "idle": ["down", "default", "defualt", "idle-still", "idle_still",
                     "battle-idle", "defualt", "forward", "forward-walk",
                     "in-battle-light", "defualt"],
            "walking": ["walk-left", "walk-right", "left-walk", "right-walk",
                        "left", "right",
                        "walk-forward", "forward-walk", "walk-back",
                        "walk-backwards", "walk-up", "backwards-walk",
                        "darkw-walk-left", "darkw-walk-right",
                        "darkw-walk-forward", "darkw-walk-back",
                        "white-walk-left", "white-walk-right",
                        "white-walk-forward", "white-walk-back",
                        "redoutline-walk-left", "redoutline-walk-right",
                        "redoutline-walk-forward", "redoutline-walk-back",
                        "light-walk-left", "light-walk-right",
                        "light-walk-down", "light-walk-up",
                        "light-walk-forward",
                        "mask-walk-left", "mask-walk-right",
                        "mask-walk-forward", "mask-walk-backwards",
                        "dark-walk-left", "dark-walk-right",
                        "dark-walk-backwards",
                        "black-left-walk", "black-right-walk",
                        "black-forward-walk",
                        "black-mask-walk-left", "black-mask-walk-right",
                        "dark-mask-walk-right", "dark-mask-walk-backwards",
                        "dark-light-walk-left", "dark-light-walk-right",
                        "dark-light-walk-backwards",
                        "dark-light-mask-walk-left", "dark-light-mask-walk-right",
                        "dark-light-mask-walk-backwards",
                        "black-light-walk-left", "black-light-walk-right",
                        "black-light-walk-backwards",
                        "no-mask-black-light-walk-left", "no-mask-black-light-walk-right",
                        "no-mask-black-light-walk-backwards",
                        "mask-light-walk-left", "mask-light-walk-right",
                        "mask-light-walk-backwards",
                        "confident-walk", "walk", "tail-fire-walk",
                        "butler-walk-left", "butler-wakl-right",
                        "walk-left-dark", "walk-right-dark",
                        "walk-back-dark",
                        "walk-left-dark-face", "walk-right-dark-face",
                        "walk-left-no-face", "walk-right-no-face",
                        "walk-forward-no-face",
                        "walk-backwards-no-face",
                        "blush-walk-left", "blush-walk-right",
                        "walk-left-with-blush", "walk-right-with-blush",
                        "walk-forward-w-blush",
                        "walk"],
            "talking": ["talk", "battle-act", "act", "talk-fast",
                        "point-and-talk", "talk-left", "talk-right"],
            "running": ["run", "dash", "sprint", "tail-fire-walk"],
            "sleeping": ["sleep", "furry-tail-sleep", "sit",
                         "sleep-bark", "sleepy", "sleeep",
                         "tail-fire-sleep", "sit"],
            "happy": ["happy-dog", "happy-2", "happy", "dance", "dance-light",
                      "eat-bone", "eat-candy"],
            "surprised": ["battle-idle-shocked-face-left", "shocked",
                          "surprised", "scared-and-fall", "battle-idle-shocked-face-left"],
            "annoyed": ["stressed", "angry", "grumpEyes"],
            "celebrating": ["dance", "dance-light", "pirroute", "bow",
                            "light-bow", "spin-scarf", "wave-hi"],
            "confused": ["battle-idle-shocked-face-left", "scared-and-fall"],
            "dazed": ["shocked", "downed", "hurt", "hit"],
            "poked": ["shocked", "battle-idle-shocked-face-left", "scared-and-fall"],
        ]
        if let alts = alternatives[requested] {
            for alt in alts {
                if !catalog.frames(alt).isEmpty { return alt }
            }
        }
        return nil
    }

    private func family(for state: BillState) -> String {
        switch state {
        case .idle: return "idle"
        case .walking, .running: return "walking"
        case .talking: return "talking"
        case .sleeping: return "sleeping"
        case .coding, .gaming, .channeling: return "coding"
        case .charging: return "charging"
        case .heatingUp: return "heating"
        case .happy, .celebrating: return "happy"
        case .annoyed, .huffy, .watched, .grumpEyes: return "annoyed"
        case .surprised, .spooked, .ambushed, .flinching: return "surprised"
        case .confused, .dazed, .thinking: return "surprised"
        case .poked: return "idle"
        case .smug, .focused, .caneFlourish: return "happy"
        // Roaming beats ride the locomotion families.
        case .crouching, .launching, .rising, .falling,
             .landingSoft, .landingHard, .ledgeGrabbing,
             .climbingUp, .climbingDown, .hangingIdle, .edgePeek:
            return "walking"
        // Rare Easter eggs / big beats: per-character specials when they
        // exist (knight attack, undyne attack, flowey evil…), otherwise
        // the character's strongest pose.
        case .powerSurge, .zodiacVision, .summonRitual, .ritualBuildup,
             .ghostPale, .glitchForm, .shadowHands, .meltdown,
             .zodiacRage, .prismDance, .zodiacCrimson,
             .rampaging, .zipAround, .dashTarget, .tumbling, .conjuring,
             .caneTwist, .hookCane:
            return "happy"
        case .trickster, .darkWorld, .hollowed, .cultLeader, .scanning,
             .sneaking, .glitching, .charged, .transferring, .summoning,
             .sculpting, .kinship, .fractaling, .presenting, .guilty,
             .dreading, .grooving, .dispatching, .stressed,
             .pushingCode, .browsingStore, .dancing:
            return "annoyed"
        }
    }

    /// Specials that only some characters ship with — checked before the
    /// generic ladder so e.g. the Knight's attack actually plays its
    /// seventeen-frame nail arc.
    private static let specialsByCharacter: [String: [BillState: String]] = [
        "knight": [
            .powerSurge: "attack", .zodiacVision: "attack", .summonRitual: "attack",
            .rampaging: "attack", .zipAround: "attack", .conjuring: "attack",
            .sleeping: "sit", .charging: "sit", .heatingUp: "attack", .dazed: "dazed",
            .thinking: "focus", .caneFlourish: "focus", .focused: "focus",
        ],
        "hornet": [
            .powerSurge: "throw", .zipAround: "jump", .rampaging: "throw",
            .landingHard: "land", .landingSoft: "land", .launching: "jump",
            .rising: "jump", .falling: "jump",
        ],
        "undyne": [
            .powerSurge: "attack", .zodiacVision: "attack", .rampaging: "attack",
            .zipAround: "attack", .conjuring: "attack",
        ],
        "flowey": [
            .powerSurge: "evil", .zodiacVision: "evil", .summonRitual: "evil",
            .meltdown: "laugh", .celebrating: "laugh", .grooving: "laugh",
        ],
        "susie": [
            .celebrating: "laugh", .meltdown: "laugh", .grooving: "laugh",
        ],
        "monsterkid": [
            .powerSurge: "goner", .zodiacVision: "goner", .ghostPale: "goner",
        ],
    ]

    // MARK: - Full-sheet extras

    /// The states that spread across the character's "x" families — every
    /// reaction, flourish and egg gets its OWN sheet animation instead of
    /// piling onto happy/annoyed/surprised. This is the "you never used all
    /// the animations" fix: a character with 48 wired rows plays 48
    /// distinct beats.
    private static let extraStates: [BillState] = [
        .trickster, .darkWorld, .hollowed, .cultLeader, .scanning,
        .sneaking, .glitching, .charged, .transferring, .summoning,
        .sculpting, .kinship, .fractaling, .presenting, .guilty,
        .dreading, .grooving, .dispatching, .ambushed, .stressed,
        .watched, .flinching, .huffy, .pushingCode, .browsingStore, .dancing,
        .caneTwist, .hookCane, .conjuring, .tumbling, .dashTarget,
        .grumpEyes, .zipAround, .celebrating, .confused, .dazed, .smug,
        .focused, .heatingUp, .channeling, .powerSurge, .zodiacVision,
        .summonRitual, .ritualBuildup, .ghostPale, .glitchForm, .prismDance,
        .rampaging,
    ]

    /// How many "x" families this character ships — probed by file
    /// existence, never by loading textures (48 families × 16 frames of
    /// Knight art would be ~100MB if the probe decoded them all).
    static func extraFamilyCount(definition: CharacterDefinition) -> Int {
        var count = 0
        for n in 1...60 {
            let name = String(format: "%@_x%02d_01", definition.spritePrefix, n)
            guard Bundle.module.url(
                forResource: name,
                withExtension: "png",
                subdirectory: "Packs/\(definition.packID)/Sprites"
            ) != nil else { break }
            count = n
        }
        return count
    }

    /// The distinct extra family for `state`, or `nil` when this character
    /// has none (or the family it maps to is empty). Cyclic assignment —
    /// every state in `extraStates` lands on a different row.
    private func extraFamily(for state: BillState) -> String? {
        let count = Self.extraFamilyCount(definition: catalog.definition)
        guard count > 0 else { return nil }
        guard let index = Self.extraStates.firstIndex(of: state) else { return nil }
        for probe in 0..<count {
            let n = (index + probe) % count + 1
            let family = String(format: "x%02d", n)
            if !catalog.frames(family).isEmpty {
                return family
            }
        }
        return nil
    }

    /// True when this state would play one of the auto-wired sheet "x"
    /// rows — outfit variants (Niko's gas mask), dark-world forms
    /// (Ralsei/Susie/Kris), flip rows (Monster Kid). Ambient idle beats
    /// refuse those (`CharacterEngine.isAmbientSafe`): extras fire on real
    /// triggers only, never in the random rotation, so nobody shape-shifts
    /// while just standing around.
    func usesExtraFamily(for state: BillState) -> Bool {
        extraFamily(for: state) != nil
    }

    // MARK: - Clip building

    func clip(for state: BillState) -> AnimationClip {
        let id = catalog.definition.id

        // User assignment from the Settings animations browser wins over
        // everything — "this reaction plays THAT row" is the whole point
        // of the assign-to-trigger UI.
        if let chosen = AppPreferences.customFamilyMapShared[state.rawValue],
           !chosen.isEmpty,
           !catalog.frames(chosen).isEmpty {
            return clip(for: state, family: chosen)
        }

        // Character specials first.
        if let special = Self.specialsByCharacter[id]?[state],
           !catalog.frames(special).isEmpty {
            return clip(for: state, family: special)
        }

        // Full-sheet extras: reaction/egg states each claim their own row
        // before falling back to the shared ladder.
        if let extra = extraFamily(for: state) {
            return clip(for: state, family: extra)
        }

        // Try the standard family name, then workbench-label alternatives,
        // then the generic fallback.
        let standard = family(for: state)
        if let resolved = resolveFamily(standard) {
            return clip(for: state, family: resolved)
        }
        if let fallback = resolveFamily(fallbackFamily(for: state)) {
            return clip(for: state, family: fallback)
        }
        // Last resort: try the literal family name (might be empty → transform-only)
        return clip(for: state, family: standard)
    }

    private func fallbackFamily(for state: BillState) -> String {
        switch state {
        case .idle, .poked: return "idle"
        case .walking, .running: return "idle"   // transform-only glide
        default: return "idle"
        }
    }

    private func clip(for state: BillState, family: String) -> AnimationClip {
        let frames = catalog.frames(family)
        let isContinuous = state.isContinuous
        let fast: TimeInterval = 0.12
        let slow: TimeInterval = 0.22

        // No frames at all: transform-only clips so the beat still reads.
        if frames.isEmpty {
            switch state {
            case .walking, .running:
                return AnimationClip(
                    textures: [catalog.restTexture],
                    frameDuration: 0.2,
                    transform: [.body: [
                        PoseKeyframe(duration: 0.32, offset: CGVector(dx: 0, dy: 3), timing: .easeInEaseOut),
                        PoseKeyframe(duration: 0.32, offset: .zero, timing: .easeInEaseOut),
                    ]],
                    loop: .loop)
            case .sleeping:
                return AnimationClip(
                    textures: [catalog.restTexture],
                    frameDuration: 0.3,
                    transform: [.body: [
                        PoseKeyframe(duration: 1.6, offset: CGVector(dx: 0, dy: -2)),
                        PoseKeyframe(duration: 1.6, offset: .zero),
                    ]],
                    loop: .pingpong)
            case .talking:
                return AnimationClip(
                    textures: [catalog.restTexture],
                    frameDuration: 0.15,
                    transform: [.body: [
                        PoseKeyframe(duration: 0.22, offset: CGVector(dx: 0, dy: 2)),
                        PoseKeyframe(duration: 0.22, offset: .zero),
                    ]],
                    loop: .loop)
            default:
                // A brief life on a one-shot beat: small hop, settle.
                return AnimationClip(
                    textures: [catalog.restTexture],
                    frameDuration: 0.2,
                    transform: [.body: [
                        PoseKeyframe(duration: 0.14, offset: CGVector(dx: 0, dy: 5), timing: .easeOut),
                        PoseKeyframe(duration: 0.2, offset: .zero, timing: .easeIn),
                    ]],
                    loop: .once)
            }
        }

        if isContinuous {
            switch state {
            case .idle:
                // The ambient breath: texture cycle (if the family has more
                // than one frame) plus the same bob Bill's idle uses.
                let textures = frames.count > 1 ? Self.pingpongLoop(frames) : frames
                return AnimationClip(
                    textures: textures,
                    frameDuration: 0.15,
                    transform: [.body: [
                        PoseKeyframe(duration: 1.4, offset: CGVector(dx: 0, dy: -5), timing: .easeInEaseOut),
                        PoseKeyframe(duration: 1.4, offset: .zero, timing: .easeInEaseOut),
                    ]],
                    loop: .loop)
            case .walking, .running:
                // Undertale's walk cycles are 2 unique poses (contact/pass)
                // repeated — at Bill's 0.16s they strobe; at amble pace they
                // read as his unhurried shuffle. Running keeps the urgency.
                let uniqueCount = Set(frames.map { ObjectIdentifier($0) }).count
                let isShuffle = uniqueCount <= 2 && frames.count >= 2
                return AnimationClip(
                    textures: isShuffle ? Array(frames.prefix(2)) : frames,
                    frameDuration: state == .running ? fast : (isShuffle ? 0.22 : 0.16),
                    transform: [.body: [
                        PoseKeyframe(duration: 0.32, offset: CGVector(dx: 0, dy: 3), timing: .easeInEaseOut),
                        PoseKeyframe(duration: 0.32, offset: .zero, timing: .easeInEaseOut),
                    ]],
                    loop: .loop)
            case .talking:
                let textures = frames.count > 1 ? Self.pingpongLoop(frames) : frames
                return AnimationClip(textures: textures, frameDuration: 0.15, loop: .loop)
            case .sleeping:
                return AnimationClip(
                    textures: frames,
                    frameDuration: 0.3,
                    transform: [.body: [
                        PoseKeyframe(duration: 1.6, offset: CGVector(dx: 0, dy: -2)),
                        PoseKeyframe(duration: 1.6, offset: .zero),
                    ]],
                    loop: .loop)
            default:
                let textures = frames.count > 1 ? Self.pingpongLoop(frames) : frames
                return AnimationClip(textures: textures, frameDuration: slow, loop: .loop)
            }
        } else {
            // One-shot beats. Multi-frame families play forward and hold
            // their last frame briefly (see `AnimationClipLibrary`'s
            // directional-motion reasoning); single-frame families get a
            // transform accent.
            if frames.count > 1 {
                let held = frames + Array(repeating: frames[frames.count - 1], count: 2)
                return AnimationClip(textures: held, frameDuration: fast, loop: .once)
            }
            switch state {
            case .surprised, .spooked, .ambushed, .poked, .flinching:
                return AnimationClip(
                    textures: frames,
                    frameDuration: 0.2,
                    transform: [.body: [
                        PoseKeyframe(duration: 0.1, offset: CGVector(dx: 0, dy: 4), timing: .easeOut),
                        PoseKeyframe(duration: 0.18, offset: .zero, timing: .easeIn),
                    ]],
                    loop: .once)
            case .happy, .celebrating, .smug:
                return AnimationClip(
                    textures: frames,
                    frameDuration: 0.3,
                    transform: [.body: [
                        PoseKeyframe(duration: 0.25, offset: CGVector(dx: 0, dy: 7), timing: .easeOut),
                        PoseKeyframe(duration: 0.3, offset: .zero, timing: .easeIn),
                    ]],
                    loop: .once)
            default:
                return AnimationClip(textures: frames, frameDuration: 0.2, loop: .once)
            }
        }
    }

    /// `[A,B,C]` → `[A,B,C,B]` — seamless forever-pingpong without the
    /// duplicated turnaround frames (see `AnimationClipLibrary.pingpongLoop`).
    private static func pingpongLoop(_ frames: [SKTexture]) -> [SKTexture] {
        guard frames.count > 2 else { return frames }
        return frames + frames.dropFirst().dropLast().reversed()
    }

    /// Idle variety beats for characters: mapped onto their own families
    /// where possible, otherwise skipped (returning `nil` keeps ambient
    /// idle running — see `BillStateMachine.playIdleVariant`).
    func idleVariant(_ variant: AnimationClipLibrary.IdleVariant) -> AnimationClip? {
        let frames: [SKTexture]
        switch variant {
        case .shiftWeight:
            let idle = catalog.frames("idle")
            guard idle.count > 1 else { return nil }
            return AnimationClip(textures: [idle[idle.count / 2]], frameDuration: 0.9, loop: .once)
        case .stretch, .tiltCheck:
            return nil  // the state machine's transform-only variants cover these
        case .curious:
            frames = catalog.frames("talking")
            guard !frames.isEmpty else { return nil }
            return AnimationClip(textures: Array(frames.prefix(2)), frameDuration: 0.25, loop: .once)
        }
    }
}
