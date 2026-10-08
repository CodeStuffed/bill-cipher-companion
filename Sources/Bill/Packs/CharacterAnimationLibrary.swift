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
        "sans": [
            .grooving: "dining", .ghostPale: "ghost",
        ],
    ]

    // MARK: - Clip building

    func clip(for state: BillState) -> AnimationClip {
        let id = catalog.definition.id

        // Character specials first.
        if let special = Self.specialsByCharacter[id]?[state],
           !catalog.frames(special).isEmpty {
            return clip(for: state, family: special)
        }

        // Generic ladder with per-family fallbacks.
        var family = family(for: state)
        if catalog.frames(family).isEmpty {
            family = fallbackFamily(for: state)
        }
        return clip(for: state, family: family)
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
                return AnimationClip(
                    textures: frames,
                    frameDuration: state == .running ? fast : 0.16,
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
