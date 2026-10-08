import SwiftUI
import SpriteKit

/// A live SpriteKit preview of one character's animations, embedded in the
/// Settings Characters section. Runs the *actual* `CharacterAnimationLibrary`
/// clips — what you preview is exactly what plays on the desktop.
///
/// Bill previews through his legacy catalog (the same `AnimationClipLibrary`
/// clips), so the picker covers the whole roster with no special cases.
struct CharacterPreviewView: NSViewRepresentable {
    let characterID: String

    func makeNSView(context: Context) -> SKView {
        let view = SKView()
        view.allowsTransparency = true
        view.preferredFramesPerSecond = 30
        context.coordinator.attach(to: view)
        return view
    }

    func updateNSView(_ view: SKView, context: Context) {
        context.coordinator.characterID = characterID
        context.coordinator.attach(to: view)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(characterID: characterID)
    }

    @MainActor
    final class Coordinator: NSObject {
        var characterID: String
        private var scene: SKScene?
        private var body: SKSpriteNode?
        private var catalog: CharacterSpriteCatalog?
        private var animationLibrary: CharacterAnimationLibrary?
        private var playWork: DispatchWorkItem?
        private var loopIndex = 0

        init(characterID: String) {
            self.characterID = characterID
        }

        func attach(to view: SKView) {
            if scene == nil {
                let newScene = SKScene(size: CGSize(width: 320, height: 260))
                newScene.backgroundColor = .clear
                newScene.scaleMode = .resizeFill
                scene = newScene
                view.presentScene(newScene)
            }
            rebuild()
        }

        func rebuild() {
            playWork?.cancel()
            body?.removeFromParent()
            body = nil
            catalog = nil
            animationLibrary = nil
            guard let scene else { return }

            let definition = CharacterRoster.character(characterID)
            let bodyNode: SKSpriteNode
            var families: [String] = []
            if definition.isBill {
                // Bill previews a curated sample of his sheet groups through
                // raw textures — his clips live in `AnimationClipLibrary`
                // which the desktop state machine already exercises.
                bodyNode = SKSpriteNode(texture: BillSpriteCatalog.restTexture)
                bodyNode.setScale(1.4)
                families = ["idle", "walk", "talk", "happy", "annoyed"]
            } else {
                let packCatalog = CharacterSpriteCatalog(definition: definition)
                catalog = packCatalog
                animationLibrary = CharacterAnimationLibrary(catalog: packCatalog)
                bodyNode = SKSpriteNode(texture: packCatalog.restTexture)
                bodyNode.setScale(definition.displayScale)
                // Only families that actually exist for this character.
                for family in ["idle", "walking", "talking", "happy", "annoyed", "surprised", "sleeping", "attack"] {
                    if !packCatalog.frames(family).isEmpty { families.append(family) }
                }
            }
            bodyNode.anchorPoint = CGPoint(x: 0.5, y: 0.35)
            bodyNode.position = CGPoint(x: 160, y: 95)
            scene.addChild(bodyNode)
            body = bodyNode

            guard !families.isEmpty else { return }

            // Cycle each family ~2.4s in sequence — a rotating showcase.
            func playNext() {
                guard let body = self.body else { return }
                let family = families[self.loopIndex % families.count]
                self.loopIndex += 1
                let textures: [SKTexture]
                let scale: CGFloat
                if definition.isBill {
                    // Pull Bill's real frames by family name mapping.
                    let billMap = ["idle": BillSpriteCatalog.idle, "walk": BillSpriteCatalog.walk,
                                   "talk": BillSpriteCatalog.talking, "happy": BillSpriteCatalog.happy,
                                   "annoyed": BillSpriteCatalog.annoyed]
                    textures = billMap[family] ?? BillSpriteCatalog.idle
                    scale = 1.4
                } else {
                    textures = self.catalog?.frames(family) ?? []
                    scale = definition.displayScale
                }
                guard !textures.isEmpty else { schedule(0.6); return }
                body.setScale(scale)
                if textures.count > 1 {
                    body.run(
                        SKAction.repeat(
                            SKAction.animate(with: textures, timePerFrame: 0.15, resize: false, restore: false),
                            count: 3
                        )
                    )
                } else {
                    body.texture = textures[0]
                }
                schedule(2.4)
            }
            func schedule(_ interval: TimeInterval) {
                let work = DispatchWorkItem { playNext() }
                playWork = work
                DispatchQueue.main.asyncAfter(deadline: .now() + interval, execute: work)
            }
            playNext()
        }
    }
}
