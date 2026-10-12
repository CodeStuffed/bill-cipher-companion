import SwiftUI
import SpriteKit

/// The Animations tab's centerpiece: every sprite family the active
/// character ships with, live-previewed in one scrolling list, each with
/// an "assign to trigger" menu — the user-facing front door of the
/// full-sheet wiring ("I want ALL animations, selectable").
struct AnimationBrowserView: NSViewRepresentable {
    let characterID: String
    @Binding var customFamilyMap: [String: String]
    @Binding var familyFacingMap: [String: String]
    @Binding var familyWorldMap: [String: String]

    func makeNSView(context: Context) -> NSScrollView {
        let scroll = NSScrollView()
        scroll.hasVerticalScroller = true
        scroll.autohidesScrollers = false
        let list = NSStackView()
        list.orientation = .vertical
        list.alignment = .leading
        list.spacing = 8
        list.edgeInsets = NSEdgeInsets(top: 8, left: 8, bottom: 8, right: 8)
        scroll.documentView = list
        context.coordinator.rebuild(list: list)
        return scroll
    }

    func updateNSView(_ scroll: NSScrollView, context: Context) {
        context.coordinator.characterID = characterID
        if let list = scroll.documentView as? NSStackView {
            context.coordinator.rebuild(list: list)
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(
            characterID: characterID,
            customBinding: $customFamilyMap,
            facingBinding: $familyFacingMap,
            worldBinding: $familyWorldMap
        )
    }

    @MainActor
    final class Coordinator: NSObject {
        var characterID: String
        var customBinding: Binding<[String: String]>
        var facingBinding: Binding<[String: String]>
        var worldBinding: Binding<[String: String]>
        private var builtFor: String = ""

        init(
            characterID: String,
            customBinding: Binding<[String: String]>,
            facingBinding: Binding<[String: String]>,
            worldBinding: Binding<[String: String]>
        ) {
            self.characterID = characterID
            self.customBinding = customBinding
            self.facingBinding = facingBinding
            self.worldBinding = worldBinding
        }

        /// The character's families, read from the shipped manifest.
        private var families: [(name: String, count: Int)] {
            // Bill previews through his own catalog — his families are the
            // sprite-sheet groups, listed by their catalog names.
            if characterID == "bill" {
                return BillFamilyList.all.map { ($0, 1) }
            }
            guard let url = Bundle.module.url(forResource: "packs_manifest", withExtension: "json", subdirectory: "Packs"),
                  let data = try? Data(contentsOf: url),
                  let manifest = try? JSONDecoder().decode([String: ManifestEntry].self, from: data),
                  let entry = manifest[characterID]
            else { return [] }
            return entry.families.sorted { $0.key < $1.key }.map { (name: $0.key, count: $0.value) }
        }

        struct ManifestEntry: Codable {
            let canvas: [Int]
            let families: [String: Int]
        }

        func rebuild(list: NSStackView) {
            guard builtFor != characterID else { return }
            builtFor = characterID
            list.arrangedSubviews.forEach { $0.removeFromSuperview() }
            let fams = families
            for family in fams {
                let row = makeRow(family: family)
                list.addArrangedSubview(row)
                list.addArrangedSubview(makeSeparator())
            }
        }

        private func makeSeparator() -> NSView {
            let line = NSBox()
            line.boxType = .separator
            return line
        }

        private func makeRow(family: (name: String, count: Int)) -> NSView {
            let facing = facingBinding.wrappedValue[family.name] ?? ""
            let container = NSView()
            container.translatesAutoresizingMaskIntoConstraints = false

            // Live preview: a small SKView looping THIS family's frames.
            let preview = SKView()
            preview.translatesAutoresizingMaskIntoConstraints = false
            preview.allowsTransparency = true
            preview.preferredFramesPerSecond = 24
            preview.setContentHuggingPriority(.required, for: .horizontal)
            let scene = FamilyPreviewScene(
                characterID: characterID,
                family: family.name,
                size: CGSize(width: 110, height: 150)
            )
            preview.presentScene(scene)
            container.addSubview(preview)

            let label = NSTextField(labelWithString: family.name + "  (" + String(family.count) + " frames)")
            label.translatesAutoresizingMaskIntoConstraints = false
            label.font = .systemFont(ofSize: NSFont.systemFontSize(for: .small), weight: .medium)
            container.addSubview(label)

            let assign = NSPopUpButton()
            assign.translatesAutoresizingMaskIntoConstraints = false
            assign.menu = makeAssignMenu(family: family.name)
            assign.setContentHuggingPriority(.required, for: .horizontal)
            container.addSubview(assign)

            // Facing label — "which way is this animation facing" so the
            // app can mirror single-sided art correctly.
            let facingMenu = NSMenu()
            facingMenu.autoenablesItems = false
            for (tag, title) in [(0, "Facing: auto"), (1, "Faces left"), (2, "Faces right (mirror)")] {
                let item = NSMenuItem(
                    title: title,
                    action: #selector(setFacing(_:)),
                    keyEquivalent: ""
                )
                item.target = self
                item.tag = tag
                item.representedObject = family.name
                let current = facingBinding.wrappedValue[family.name] ?? ""
                item.state = (tag == 0 && current.isEmpty)
                    || (tag == 1 && current == "left")
                    || (tag == 2 && current == "right") ? .on : .off
                facingMenu.addItem(item)
            }
            let facingButton = NSPopUpButton()
            facingButton.translatesAutoresizingMaskIntoConstraints = false
            facingButton.menu = facingMenu
            facingButton.setContentHuggingPriority(.required, for: .horizontal)
            container.addSubview(facingButton)

            // World label — "which world's art is this row": the explicit
            // dark/light mapping for Deltarune-style sheets. The World-mode
            // segment then switches between them (with the crossfade).
            let worldMenu = NSMenu()
            worldMenu.autoenablesItems = false
            for (tag, title) in [(0, "World: auto"), (1, "Light world"), (2, "Dark world")] {
                let item = NSMenuItem(
                    title: title,
                    action: #selector(setWorld(_:)),
                    keyEquivalent: ""
                )
                item.target = self
                item.tag = tag
                item.representedObject = family.name
                let currentWorld = worldBinding.wrappedValue[family.name] ?? ""
                item.state = (tag == 0 && currentWorld.isEmpty)
                    || (tag == 1 && currentWorld == "light")
                    || (tag == 2 && currentWorld == "dark") ? .on : .off
                worldMenu.addItem(item)
            }
            let worldButton = NSPopUpButton()
            worldButton.translatesAutoresizingMaskIntoConstraints = false
            worldButton.menu = worldMenu
            worldButton.setContentHuggingPriority(.required, for: .horizontal)
            container.addSubview(worldButton)

            NSLayoutConstraint.activate([
                preview.leadingAnchor.constraint(equalTo: container.leadingAnchor),
                preview.topAnchor.constraint(equalTo: container.topAnchor),
                preview.bottomAnchor.constraint(equalTo: container.bottomAnchor),
                preview.widthAnchor.constraint(equalToConstant: 110),
                label.leadingAnchor.constraint(equalTo: preview.trailingAnchor, constant: 12),
                label.centerYAnchor.constraint(equalTo: container.centerYAnchor),
                assign.leadingAnchor.constraint(equalTo: label.trailingAnchor, constant: 12),
                assign.centerYAnchor.constraint(equalTo: container.centerYAnchor),
                facingButton.leadingAnchor.constraint(equalTo: assign.trailingAnchor, constant: 12),
                facingButton.centerYAnchor.constraint(equalTo: container.centerYAnchor),
                worldButton.leadingAnchor.constraint(equalTo: facingButton.trailingAnchor, constant: 12),
                worldButton.centerYAnchor.constraint(equalTo: container.centerYAnchor),
                container.trailingAnchor.constraint(greaterThanOrEqualTo: worldButton.trailingAnchor, constant: 8),
            ])
            return container
        }

        private func makeAssignMenu(family: String) -> NSMenu {
            let menu = NSMenu()
            menu.autoenablesItems = false

            let title = NSMenuItem(title: "Assign to…", action: nil, keyEquivalent: "")
            title.isEnabled = false
            menu.addItem(title)

            // States already assigned to this family show a checkmark.
            let assigned = customBinding.wrappedValue.filter { $0.value == family }.map(\.key)

            for state in BillState.allCases {
                let item = NSMenuItem(
                    title: state.rawValue,
                    action: #selector(assignFamily(_:)),
                    keyEquivalent: ""
                )
                item.target = self
                item.representedObject = ["family": family, "state": state.rawValue]
                item.state = assigned.contains(state.rawValue) ? .on : .off
                item.isEnabled = true
                menu.addItem(item)
            }
            return menu
        }

        @objc private func assignFamily(_ sender: NSMenuItem) {
            guard let info = sender.representedObject as? [String: String],
                  let family = info["family"], let state = info["state"] else { return }
            var map = customBinding.wrappedValue
            if map[state] == family {
                map.removeValue(forKey: state)  // clicking again = unassign
            } else {
                map[state] = family
            }
            customBinding.wrappedValue = map
            // rebuild menus so checkmarks update
            if let window = NSApp.keyWindow {
                (window.contentView as? NSHostingView<AnimationsTabRoot>)?.needsLayout = true
            }
        }

        @objc private func setFacing(_ sender: NSMenuItem) {
            guard let family = sender.representedObject as? String else { return }
            var map = facingBinding.wrappedValue
            switch sender.tag {
            case 1: map[family] = "left"
            case 2: map[family] = "right"
            default: map.removeValue(forKey: family)
            }
            facingBinding.wrappedValue = map
        }

        @objc private func setWorld(_ sender: NSMenuItem) {
            guard let family = sender.representedObject as? String else { return }
            var map = worldBinding.wrappedValue
            switch sender.tag {
            case 1: map[family] = "light"
            case 2: map[family] = "dark"
            default: map.removeValue(forKey: family)
            }
            worldBinding.wrappedValue = map
        }
    }
}

/// A tiny host that lets us force the tab to redraw on assignment changes.
struct AnimationsTabRoot: View {
    var body: some View { EmptyView() }
}

/// One looping family preview. Runs the exact textures the desktop
/// character plays — what you preview is what ships.
@MainActor
final class FamilyPreviewScene: SKScene {
    init(characterID: String, family: String, size: CGSize) {
        super.init(size: size)
        backgroundColor = .clear
        scaleMode = .resizeFill
        let definition = CharacterRoster.character(characterID)
        if definition.isBill {
            // Bill renders straight from his sprite catalog by family name.
            let frames = BillFamilyFrames.frames(family)
            guard !frames.isEmpty else { return }
            let body = SKSpriteNode(texture: frames[0])
            body.setScale(min(100 / frames[0].size().width, 140 / frames[0].size().height))
            body.position = CGPoint(x: size.width / 2, y: size.height / 2)
            addChild(body)
            if frames.count > 1 {
                body.run(SKAction.repeatForever(
                    SKAction.animate(with: frames, timePerFrame: 0.15, resize: false, restore: false)))
            }
            return
        }
        let catalog = CharacterSpriteCatalog(definition: definition)
        let frames = catalog.frames(family)
        guard !frames.isEmpty else { return }
        let scale = min(100 / definition.canvasSize.width, 140 / definition.canvasSize.height)
        let body = SKSpriteNode(texture: frames[0])
        body.setScale(scale)
        // Show the labeled facing — mirrored previews match desktop play.
        if AppPreferences.familyFacingMapShared[family] == "right" {
            body.xScale = -abs(body.xScale)
        }
        body.position = CGPoint(x: size.width / 2, y: size.height / 2)
        addChild(body)
        if frames.count > 1 {
            body.run(
                SKAction.repeatForever(
                    SKAction.animate(with: frames, timePerFrame: 0.15, resize: false, restore: false)
                )
            )
        }
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) not supported") }
}

/// Bill's sprite families (the `BillSpriteCatalog` groups), named.
@MainActor
enum BillFamilyList {
    static let all = [
        "idle", "walk", "annoyed", "happy", "confused", "heating", "charging",
        "surprised", "poked", "dazed", "sleeping", "thinking", "coding", "talking",
        "smug", "snap", "focused", "channeling", "celebrating", "curious", "cane",
        "powersurge", "powersurgeclose", "portalring", "zodiac", "summonritual",
        "zodiacrage", "prismdance", "zodiaccrimson", "summonbuild", "summonhold",
        "ghost", "glitch", "shadowa", "shadowb", "meltdown",
        "trickster", "darkworld", "hollowed", "cultleader", "spooked", "scanning",
        "sneaking", "glitching", "charged", "transferring", "summoning", "sculpting",
        "kinship", "fractaling", "presenting", "guilty", "dreading", "grooving",
        "dispatching", "ambushed", "stressed", "watched", "flinching", "huffy",
        "pushingcode", "browsingstore", "dancing",
        "canetwist", "hookcane", "conjuring", "tumbling", "dashtarget",
        "grumpeyes", "ziparound", "rampaging",
    ]
}


@MainActor
enum BillFamilyFrames {
    private static var cache: [String: [SKTexture]] = [:]

    static func frames(_ family: String) -> [SKTexture] {
        if let cached = cache[family] { return cached }
        var textures: [SKTexture] = []
        var i = 1
        while true {
            let name = String(format: "bill_%@_%02d", family, i)
            guard let url = Bundle.module.url(forResource: name, withExtension: "png", subdirectory: "Sprites"),
                  let image = NSImage(contentsOf: url) else { break }
            let texture = SKTexture(image: image)
            texture.filteringMode = .nearest
            textures.append(texture)
            i += 1
        }
        cache[family] = textures
        return textures
    }
}
