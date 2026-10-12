import SwiftUI
import SpriteKit

/// One animation in the selector grid: a LIVE looping preview of the
/// animation (the actual textures the desktop character plays), the state
/// name, and a visible disabled state — greyed out, struck through, dimmed
/// preview — so "done to them you can see it visually".
struct StateSelectorTile: View {
    let state: BillState
    let isEnabled: Bool
    let onToggle: (Bool) -> Void

    var body: some View {
        Button(action: { onToggle(!isEnabled) }) {
            VStack(spacing: 2) {
                StatePreviewTexture(characterID: AppPreferences.activeCharacterShared, state: state)
                    .frame(width: 96, height: 84)
                    .opacity(isEnabled ? 1 : 0.3)
                    .saturation(isEnabled ? 1 : 0)
                Text(state.rawValue)
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .strikethrough(!isEnabled, color: .red)
                    .foregroundColor(isEnabled ? .primary : .secondary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
            }
            .padding(6)
            .frame(width: 112)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isEnabled
                          ? Color.accentColor.opacity(0.10)
                          : Color(nsColor: .quaternaryLabelColor).opacity(0.4))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(isEnabled ? Color.accentColor.opacity(0.45) : Color(nsColor: .separatorColor),
                                  lineWidth: isEnabled ? 1.5 : 1)
            )
            .overlay(alignment: .topTrailing) {
                Image(systemName: isEnabled ? "checkmark.circle.fill" : "nosign")
                    .font(.system(size: 11))
                    .foregroundColor(isEnabled ? .green : .red)
                    .padding(3)
            }
        }
        .buttonStyle(.plain)
        .help(isEnabled
              ? "\(state.rawValue) plays. Click to disable."
              : "\(state.rawValue) is DISABLED and never plays automatically. Click to enable.")
    }
}

/// The tile's preview: static at rest, LIVE-ANIMATING while hovered —
/// the whole sheet stays light (dozens of tiles) yet every animation
/// can be seen moving ("I want to see the animation move too").
struct StatePreviewTexture: NSViewRepresentable {
    let characterID: String
    let state: BillState

    func makeNSView(context: Context) -> StatePreviewSKView {
        let view = StatePreviewSKView()
        view.configure(characterID: characterID, state: state)
        return view
    }

    func updateNSView(_ view: StatePreviewSKView, context: Context) {
        view.configure(characterID: characterID, state: state)
    }
}

/// NSView-hosted SKView that loops the state's real frame sequence while
/// the cursor is over it (NSTrackingArea, no SwiftUI state needed).
@MainActor
final class StatePreviewSKView: NSView {
    private let skView = SKView()
    private var scene = SKScene()
    private var bodyNode = SKSpriteNode()
    private var frames: [SKTexture] = []
    private var characterID = ""
    private var state: BillState?
    private var isAnimating = false

    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        skView.translatesAutoresizingMaskIntoConstraints = false
        skView.allowsTransparency = true
        skView.preferredFramesPerSecond = 15
        addSubview(skView)
        NSLayoutConstraint.activate([
            skView.leadingAnchor.constraint(equalTo: leadingAnchor),
            skView.trailingAnchor.constraint(equalTo: trailingAnchor),
            skView.topAnchor.constraint(equalTo: topAnchor),
            skView.bottomAnchor.constraint(equalTo: bottomAnchor),
        ])
        scene.backgroundColor = .clear
        scene.scaleMode = .resizeFill
        scene.addChild(bodyNode)
        skView.presentScene(scene)
        updateTrackingAreas()
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) not supported") }

    override func updateTrackingAreas() {
        trackingAreas.forEach { removeTrackingArea($0) }
        addTrackingArea(
            NSTrackingArea(
                rect: bounds,
                options: [.mouseEnteredAndExited, .activeAlways],
                owner: self,
                userInfo: nil
            )
        )
        super.updateTrackingAreas()
    }

    override func mouseEntered(with event: NSEvent) { startAnimation() }
    override func mouseExited(with event: NSEvent) { stopAnimation() }

    func configure(characterID: String, state: BillState) {
        guard characterID != self.characterID || state != self.state else { return }
        self.characterID = characterID
        self.state = state
        reload()
    }

    private func reload() {
        guard let state else { return }
        let definition = CharacterRoster.character(characterID)
        var textures: [SKTexture] = []
        var mirrored = false
        if definition.isBill {
            textures = BillStatePreviewFrames.frames(for: state) ?? []
        } else {
            let catalog = CharacterSpriteCatalog(definition: definition)
            let library = CharacterAnimationLibrary(catalog: catalog)
            let clip = library.clip(for: state)
            textures = clip.textures
            mirrored = clip.mirrored
        }
        frames = textures
        bodyNode.removeAllActions()
        guard let first = textures.first else {
            bodyNode.texture = nil
            return
        }
        let size = bounds.size.width > 0
            ? bounds.size : CGSize(width: 96, height: 84)
        let scale = min((size.width - 10) / first.size().width,
                        (size.height - 10) / first.size().height)
        bodyNode.texture = first
        bodyNode.size = first.size()
        bodyNode.setScale(scale)
        bodyNode.xScale = mirrored ? -abs(bodyNode.xScale) : abs(bodyNode.xScale)
        bodyNode.position = CGPoint(x: size.width / 2, y: size.height / 2)
        isAnimating = false
    }

    private func startAnimation() {
        guard !isAnimating, frames.count > 1 else { return }
        isAnimating = true
        bodyNode.run(
            SKAction.repeatForever(
                SKAction.animate(with: frames, timePerFrame: 0.15, resize: false, restore: false)
            ),
            withKey: "previewLoop"
        )
    }

    private func stopAnimation() {
        isAnimating = false
        bodyNode.removeAction(forKey: "previewLoop")
        if let first = frames.first {
            bodyNode.texture = first
        }
    }
}

/// Bill's per-state first-frame lookup — his textures don't go through
/// `CharacterSpriteCatalog`, so the preview maps states to his catalog
/// families directly (the same mapping the clip library uses).
@MainActor
enum BillStatePreviewFrames {
    private static var cache: [BillState: [SKTexture]] = [:]

    static func frames(for state: BillState) -> [SKTexture]? {
        if let cached = cache[state] { return cached }
        // Reuse the real clip library — one pass builds his mapping for us.
        let clip = AnimationClipLibrary.clip(for: state)
        cache[state] = clip.textures
        return clip.textures
    }
}
