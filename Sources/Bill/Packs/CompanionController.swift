import SpriteKit
import Foundation

/// A second character living in the primary character's window — Sans
/// brings Papyrus, the Knight brings Hornet. Multi-character support
/// without a second window, second render loop, or second roaming sim:
/// the companion is a full rig + state machine (so it benefits from the
/// exact same clip/texture system), but it stays parked at its side of
/// the window while the primary character roams and reacts.
///
/// Its behavior is deliberately simpler than the primary's:
/// - Ambient beats: occasionally plays one of its own families.
/// - Reactions: fires on a *fraction* of the primary's app reactions, so
///   it feels like it's paying attention without doubling the chatter.
/// - Banter: sometimes *responds* to what the primary just said, drawn
///   from its own dialogue pools ("banter.respond"), which is what makes
///   a pair read as a pair rather than two pets in a trench coat.
@MainActor
final class CompanionController {
    let definition: CharacterDefinition
    let rig: BillRigNode
    let stateMachine: BillStateMachine
    private let catalog: CharacterSpriteCatalog
    private let library: CharacterAnimationLibrary
    /// This companion's OWN voice — never the primary's. The shared
    /// `DialogueLibrary` only ever holds the primary character's pools,
    /// so a companion speaking through it would talk in the primary's
    /// voice (Papyrus saying Sans's lines).
    private let voice: DialogueVoice
    /// Where companion bark text goes — routed through the primary's bark
    /// queue so the shared bark panel serializes both voices (the panel
    /// is positioned over the shared window).
    private let barkSink: (String) -> Void

    private var beatTimer: Timer?
    private weak var scene: SKScene?
    private var lastBeat: BillState?
    private var lastPrimaryBarkAt: Date?
    private var respondedToBarkAt: Date?

    /// The states a companion cycles through when it fancies a move — all
    /// safe anywhere, at any time. No roaming beats, no rare eggs: the
    /// companion's drama budget is small on purpose; the window is a stage,
    /// not a battlefield.
    private static let beatStates: [BillState] = [
        .idle, .talking, .happy, .annoyed, .surprised, .smug, .confused, .dazed,
    ]

    init(definition: CharacterDefinition, barkSink: @escaping (String) -> Void) {
        self.definition = definition
        self.barkSink = barkSink
        voice = DialogueVoice(character: definition)
        let packCatalog = CharacterSpriteCatalog(definition: definition)
        catalog = packCatalog
        library = CharacterAnimationLibrary(catalog: packCatalog)
        rig = BillRigNode.build(catalog: packCatalog, displayScale: definition.displayScale)
        let library = self.library
        stateMachine = BillStateMachine(
            rig: rig,
            clipProvider: { library.clip(for: $0) },
            restTexture: packCatalog.restTexture,
            idleVariants: { library.idleVariant($0) }
        )
        rig.root.name = "companionRoot"
    }

    // MARK: - Scene lifecycle

    func attach(to scene: SKScene?) {
        guard let scene else { return }
        self.scene = scene
        rig.root.removeFromParent()
        scene.addChild(rig.root)
        stateMachine.request(.idle)
        startBeats()
    }

    func detach() {
        stopBeats()
        stateMachine.clearBarkQueue()
        rig.root.removeFromParent()
    }

    // MARK: - Ambient beats

    private func startBeats() {
        beatTimer?.invalidate()
        scheduleNextBeat()
    }

    private func stopBeats() {
        beatTimer?.invalidate()
        beatTimer = nil
    }

    private func scheduleNextBeat() {
        // 14–40s: present enough to be company, sparse enough that it never
        // competes with the primary's reactions.
        let delay = Double.random(in: 14...40)
        beatTimer = Timer.scheduledTimer(withTimeInterval: delay, repeats: false) { [weak self] _ in
            Task { @MainActor in self?.fireBeat() }
        }
    }

    private func fireBeat() {
        defer { scheduleNextBeat() }
        guard stateMachine.currentState == .idle else { return }
        let candidates = Self.beatStates.filter { $0 != lastBeat }
        guard let state = candidates.randomElement() else { return }
        lastBeat = state
        stateMachine.request(state, force: true)

        // A move is sometimes worth a word — its own voice, from its own
        // pools, through the shared bark panel.
        if Double.random(in: 0..<1) < 0.35,
           let key = DialogueKey(rawValue: state.rawValue),
           let line = voice.line(key) {
            barkSink(line)
        }
    }

    // MARK: - Banter

    /// Called by the window controller whenever the *primary* character
    /// barks. Most of the time the companion stays quiet (sidekicks know
    /// when not to steal a line); occasionally it quips back, which is
    /// the whole reason to ship characters in pairs.
    func primaryBarked() {
        lastPrimaryBarkAt = Date()
        // Never twice in a row, never within 8s of its own last response,
        // and only ~22% of the time.
        guard let last = respondedToBarkAt,
              Date().timeIntervalSince(last) > 8 else {
            respondedToBarkAt = respondedToBarkAt ?? Date()
            return
        }
        guard Double.random(in: 0..<1) < 0.22 else { return }
        guard let line = voice.line("banter.respond") else { return }
        respondedToBarkAt = Date()
        // Face its partner: a small reaction beat, then the quip.
        stateMachine.request(.talking, force: true)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) { [weak self] in
            self?.barkSink(line)
        }
    }
}
