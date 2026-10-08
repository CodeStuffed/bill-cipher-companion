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

/// A static snapshot of the state's first frame — cheap enough to tile
/// dozens of times (one live SKView per tile would be heavy).
struct StatePreviewTexture: NSViewRepresentable {
    let characterID: String
    let state: BillState

    func makeNSView(context: Context) -> NSImageView {
        let view = NSImageView()
        view.imageScaling = .scaleProportionallyUpOrDown
        view.image = renderFrame()
        return view
    }

    func updateNSView(_ view: NSImageView, context: Context) {
        view.image = renderFrame()
    }

    private func renderFrame() -> NSImage? {
        let definition = CharacterRoster.character(characterID)
        if definition.isBill {
            // Bill: render through his catalog — pick the state's first frame.
            guard let frames = BillStatePreviewFrames.frames(for: state), let first = frames.first else {
                return placeholderGlyph
            }
            return Self.image(from: first)
        }
        let catalog = CharacterSpriteCatalog(definition: definition)
        let library = CharacterAnimationLibrary(catalog: catalog)
        let clip = library.clip(for: state)
        guard let texture = clip.textures.first else { return placeholderGlyph }
        return Self.image(from: texture)
    }

    /// SKTexture → NSImage via the texture's underlying CGImage.
    private static func image(from texture: SKTexture) -> NSImage? {
        let cg = texture.cgImage()
        return NSImage(cgImage: cg, size: NSSize(width: cg.width, height: cg.height))
    }

    private var placeholderGlyph: NSImage {
        NSImage(systemSymbolName: "questionmark.square.dashed", accessibilityDescription: nil)
            ?? NSImage()
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
