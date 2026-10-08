import SpriteKit
import AppKit

/// Loads one character's pixel-art frame families on demand — the pack
/// counterpart of `BillSpriteCatalog`. Every frame already shares the
/// character's one canvas size and bottom-center alignment (baked by
/// `Scripts/process_pack_sprites.py`), so the anti-snap guarantees of the
/// Bill pipeline carry over unchanged, and nearest-neighbor filtering keeps
/// every pixel crisp at any `displayScale`.
///
/// Textures are cached per family on first use; a family the character
/// simply doesn't have resolves to `[]` and `CharacterAnimationLibrary`
/// falls back gracefully — a missing beat never crashes or stalls.
@MainActor
final class CharacterSpriteCatalog {
    let definition: CharacterDefinition
    private var cache: [String: [SKTexture]] = [:]
    /// Set once at init; every state settles back onto it.
    let restTexture: SKTexture

    init(definition: CharacterDefinition) {
        self.definition = definition
        let idle = Self.load(definition: definition, family: "idle")
        if let first = idle.first {
            restTexture = first
        } else {
            // No idle family at all (shouldn't happen for shipped packs) —
            // a 1×1 transparent stand-in keeps the rig total.
            restTexture = SKTexture(image: NSImage(size: NSSize(width: 1, height: 1)))
        }
        cache["idle"] = idle
    }

    /// The frames of `family`, in order. Empty when the family is absent.
    func frames(_ family: String) -> [SKTexture] {
        if let cached = cache[family] { return cached }
        let loaded = Self.load(definition: definition, family: family)
        cache[family] = loaded
        return loaded
    }

    private static func load(definition: CharacterDefinition, family: String) -> [SKTexture] {
        var textures: [SKTexture] = []
        var index = 1
        while true {
            let name = String(format: "%@_%@_%02d", definition.spritePrefix, family, index)
            guard
                let url = Bundle.module.url(
                    forResource: name,
                    withExtension: "png",
                    subdirectory: "Packs/\(definition.packID)/Sprites"
                ),
                let image = NSImage(contentsOf: url)
            else { break }
            let texture = SKTexture(image: image)
            texture.filteringMode = .nearest
            textures.append(texture)
            index += 1
        }
        return textures
    }
}
