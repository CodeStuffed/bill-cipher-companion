import SwiftUI
import SpriteKit

/// The Animations tab's centerpiece: every sprite family the active
/// character ships with, live-previewed in one scrolling list, each with
/// an "assign to trigger" menu — the user-facing front door of the
/// full-sheet wiring ("I want ALL animations, selectable").
struct AnimationBrowserView: NSViewRepresentable {
    let characterID: String
    @Binding var customFamilyMap: [String: String]

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
        Coordinator(characterID: characterID, binding: $customFamilyMap)
    }

    @MainActor
    final class Coordinator: NSObject {
        var characterID: String
        var binding: Binding<[String: String]>
        private var builtFor: String = ""

        init(characterID: String, binding: Binding<[String: String]>) {
            self.characterID = characterID
            self.binding = binding
        }

        /// The character's families, read from the shipped manifest.
        private var families: [(name: String, count: Int)] {
            guard let url = Bundle.module.url(forResource: "packs_manifest", withExtension: "json", subdirectory: "Packs"),
                  let data = try? Data(contentsOf: url),
                  let manifest = try? JSONDecoder().decode([String: ManifestEntry].self, from: data),
                  let entry = manifest[characterID]
            else { return [] }
            return entry.families.sorted { $0.key < $1.key }.map { (name: $0.key, count: $0.value.count) }
        }

        struct ManifestEntry: Codable {
            struct FamiliesValue: Codable { let count: Int }
            let canvas: [Int]
            let families: [String: FamiliesValue]
        }

        func rebuild(list: NSStackView) {
            guard builtFor != characterID else { return }
            builtFor = characterID
            list.arrangedSubviews.forEach { $0.removeFromSuperview() }
            let fams = families
            if fams.isEmpty {
                let label = NSTextField(labelWithString: "Bill's classic 68 animations are managed in the Test Triggers tab.")
                label.font = .systemFont(ofSize: NSFont.smallSystemFontSize)
                label.textColor = .secondaryLabelColor
                list.addArrangedSubview(label)
                return
            }
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

            NSLayoutConstraint.activate([
                preview.leadingAnchor.constraint(equalTo: container.leadingAnchor),
                preview.topAnchor.constraint(equalTo: container.topAnchor),
                preview.bottomAnchor.constraint(equalTo: container.bottomAnchor),
                preview.widthAnchor.constraint(equalToConstant: 110),
                label.leadingAnchor.constraint(equalTo: preview.trailingAnchor, constant: 12),
                label.centerYAnchor.constraint(equalTo: container.centerYAnchor),
                assign.leadingAnchor.constraint(equalTo: label.trailingAnchor, constant: 12),
                assign.centerYAnchor.constraint(equalTo: container.centerYAnchor),
                container.trailingAnchor.constraint(greaterThanOrEqualTo: assign.trailingAnchor, constant: 8),
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
            let assigned = binding.wrappedValue.filter { $0.value == family }.map(\.key)

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
            var map = binding.wrappedValue
            if map[state] == family {
                map.removeValue(forKey: state)  // clicking again = unassign
            } else {
                map[state] = family
            }
            binding.wrappedValue = map
            // rebuild menus so checkmarks update
            if let window = NSApp.keyWindow {
                (window.contentView as? NSHostingView<AnimationsTabRoot>)?.needsLayout = true
            }
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
        guard !definition.isBill else {
            let label = SKLabelNode(text: "Bill: use Test Triggers")
            label.fontSize = 9
            label.fontName = "Menlo-Bold"
            label.fontColor = NSColor.secondaryLabelColor
            label.position = CGPoint(x: size.width / 2, y: size.height / 2)
            addChild(label)
            return
        }
        let catalog = CharacterSpriteCatalog(definition: definition)
        let frames = catalog.frames(family)
        guard !frames.isEmpty else { return }
        let scale = min(100 / definition.canvasSize.width, 140 / definition.canvasSize.height)
        let body = SKSpriteNode(texture: frames[0])
        body.setScale(scale)
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
