import AppKit

@MainActor
final class StatusItemController: NSObject {
    private let statusItem: NSStatusItem
    private weak var appDelegate: AppDelegate?
    private let characterEngine: CharacterEngine
    private let characterWindowController: CharacterWindowController
    private let chatPanelController: ChatPanelController
    private let settingsWindowController: SettingsWindowController
    private let dialogueRefreshLogWindowController: DialogueRefreshLogWindowController

    init(
        appDelegate: AppDelegate,
        characterEngine: CharacterEngine,
        characterWindowController: CharacterWindowController,
        chatPanelController: ChatPanelController,
        settingsWindowController: SettingsWindowController,
        dialogueRefreshLogWindowController: DialogueRefreshLogWindowController
    ) {
        self.appDelegate = appDelegate
        self.characterEngine = characterEngine
        self.characterWindowController = characterWindowController
        self.chatPanelController = chatPanelController
        self.settingsWindowController = settingsWindowController
        self.dialogueRefreshLogWindowController = dialogueRefreshLogWindowController
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        super.init()
        configure()
    }

    private var studyModeItem: NSMenuItem!

    private func configure() {
        if let button = statusItem.button {
            button.image = NSImage(systemSymbolName: "eye.fill", accessibilityDescription: "Bill")
        }
        buildMenu()
        refreshStudyModeItem()
    }

    /// The menu is rebuilt from scratch whenever the character switches so
    /// titles ("Talk to Sans"), pack checkmarks and the Bill-only items
    /// stay honest without tracking individual items.
    func buildMenu() {
        let menu = NSMenu()
        let character = characterEngine.character

        let talkTitle = character.isBill ? "Talk to Bill" : "Talk to \(character.displayName)"
        let talkItem = NSMenuItem(title: talkTitle, action: #selector(talkToBill), keyEquivalent: "")
        talkItem.target = self
        menu.addItem(talkItem)
        let openChatItem = NSMenuItem(title: "Open Full Chat View…", action: #selector(openChat), keyEquivalent: "")
        openChatItem.target = self
        menu.addItem(openChatItem)

        // The ChatGPT-backed features write Bill's voice and Bill's pools;
        // pack characters speak from their own bundled dialogue instead.
        if character.isBill {
            let refreshContextItem = NSMenuItem(title: "Refresh Bill's Context Now", action: #selector(refreshDialogue), keyEquivalent: "")
            refreshContextItem.target = self
            menu.addItem(refreshContextItem)
            let quotesManagerItem = NSMenuItem(title: "Quotes Manager…", action: #selector(openQuotesManager), keyEquivalent: "")
            quotesManagerItem.target = self
            menu.addItem(quotesManagerItem)
            let personalizeItem = NSMenuItem(title: "Personalize Bill's Commentary…", action: #selector(personalize), keyEquivalent: "")
            personalizeItem.target = self
            menu.addItem(personalizeItem)
        }

        menu.addItem(.separator())

        // Character switching — the pack system's front door. Packs in
        // their display order, each character one click away, the active
        // one checked.
        let characterItem = NSMenuItem(title: "Character", action: nil, keyEquivalent: "")
        characterItem.submenu = makeCharacterSubmenu()
        menu.addItem(characterItem)

        menu.addItem(.separator())

        let weatherTestItem = NSMenuItem(title: "Test Weather Now", action: #selector(testWeather), keyEquivalent: "")
        weatherTestItem.target = self
        menu.addItem(weatherTestItem)
        menu.addItem(.separator())

        // The only checkmark item in this menu. Its title carries the
        // remaining time while a session is running, so the menu bar answers
        // "how long left?" without opening anything.
        studyModeItem = NSMenuItem(title: "Study Mode", action: #selector(toggleStudyMode), keyEquivalent: "")
        studyModeItem.target = self
        menu.addItem(studyModeItem)
        menu.addItem(.separator())
        let settingsItem = NSMenuItem(title: "Settings…", action: #selector(openSettings), keyEquivalent: ",")
        settingsItem.target = self
        menu.addItem(settingsItem)
        menu.addItem(.separator())

        let aboutItem = NSMenuItem(title: "About & Credits", action: #selector(showAbout), keyEquivalent: "")
        aboutItem.target = self
        menu.addItem(aboutItem)
        menu.addItem(.separator())

        // Debug controls are deliberately not part of the normal user
        // experience — enable with
        // `defaults write <bundle-id> billDebugMenu -bool YES`.
        if AppPreferences.isDebugMenuEnabled {
            let debugItem = NSMenuItem(title: "Debug: Force State", action: nil, keyEquivalent: "")
            debugItem.submenu = makeDebugSubmenu()
            menu.addItem(debugItem)

            let dumpItem = NSMenuItem(title: "Debug: Dump State", action: #selector(dumpState), keyEquivalent: "")
            dumpItem.target = self
            menu.addItem(dumpItem)

            let barkItem = NSMenuItem(title: "Debug: Test Bark", action: #selector(testBark), keyEquivalent: "")
            barkItem.target = self
            menu.addItem(barkItem)

            let wanderItem = NSMenuItem(title: "Debug: Trigger Wander Now", action: #selector(triggerWander), keyEquivalent: "")
            wanderItem.target = self
            menu.addItem(wanderItem)

            let chatTestItem = NSMenuItem(title: "Debug: Test Chat Connection", action: #selector(testChat), keyEquivalent: "")
            chatTestItem.target = self
            menu.addItem(chatTestItem)

            let awarenessItem = NSMenuItem(title: "Debug: Test Screen Awareness Now", action: #selector(testAwareness), keyEquivalent: "")
            awarenessItem.target = self
            menu.addItem(awarenessItem)

            let dialogueLogItem = NSMenuItem(title: "Debug: Show Dialogue Refresh Log", action: #selector(showDialogueRefreshLog), keyEquivalent: "")
            dialogueLogItem.target = self
            menu.addItem(dialogueLogItem)
            menu.addItem(.separator())
        }

        let quitTitle = character.isBill ? "Quit Bill" : "Quit Companion"
        let quitItem = NSMenuItem(title: quitTitle, action: #selector(AppDelegate.quit), keyEquivalent: "q")
        quitItem.target = appDelegate
        menu.addItem(quitItem)

        menu.delegate = self
        statusItem.menu = menu
        refreshStudyModeItem()
    }

    /// The pack roster as a submenu: Bill, then every pack with its
    /// characters indented under it. Selecting swaps the on-screen
    /// character live.
    private func makeCharacterSubmenu() -> NSMenu {
        let submenu = NSMenu()

        let billItem = NSMenuItem(
            title: CharacterRoster.bill.displayName,
            action: #selector(switchCharacter(_:)),
            keyEquivalent: ""
        )
        billItem.target = self
        billItem.representedObject = CharacterRoster.bill.id
        billItem.state = characterEngine.character.isBill ? .on : .off
        submenu.addItem(billItem)

        for (packName, characters) in CharacterRoster.packs {
            submenu.addItem(.separator())
            let header = NSMenuItem(title: packName, action: nil, keyEquivalent: "")
            header.isEnabled = false
            submenu.addItem(header)
            for definition in characters {
                let item = NSMenuItem(
                    title: definition.displayName,
                    action: #selector(switchCharacter(_:)),
                    keyEquivalent: ""
                )
                item.target = self
                item.representedObject = definition.id
                item.state = definition.id == characterEngine.character.id ? .on : .off
                submenu.addItem(item)
            }
        }
        return submenu
    }

    @objc private func switchCharacter(_ sender: NSMenuItem) {
        guard let id = sender.representedObject as? String else { return }
        appDelegate?.switchCharacter(to: id)
    }

    /// Sprite credits for every pack — the rippers who made this possible.
    @objc private func showAbout() {
        let credits = ([CharacterRoster.bill] + CharacterRoster.all.filter { !$0.isBill })
            .map { "\($0.displayName) — \($0.credit)" }
            .joined(separator: "\n\n")
        let alert = NSAlert()
        alert.messageText = "Desktop Companion"
        alert.informativeText = """
            Characters: Bill Cipher, Undertale, Deltarune, OneShot & Hollow Knight — all in one desktop pet.

            Sprite credits:
            \(credits)

            This is a non-commercial fan project. All characters belong to their creators.
            """
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }

    /// Keeps the checkmark and the remaining-time title honest. Called when
    /// the session starts/ends and every time the menu is about to open, which
    /// is cheaper and more reliable than a countdown timer just for a label.
    func refreshStudyModeItem() {
        guard let studyModeItem, let studyMode = appDelegate?.studyMode else { return }
        if studyMode.isActive {
            let minutes = Int((studyMode.remaining / 60).rounded(.up))
            studyModeItem.title = "Study Mode — \(minutes) min left"
            studyModeItem.state = .on
        } else {
            studyModeItem.title = "Study Mode (30 min)"
            studyModeItem.state = .off
        }
    }

    /// Reports what Bill's embedded ChatGPT page actually is right now.
    ///
    /// Worth having its own button because the most likely failure is also the
    /// least obvious: this WebView keeps its own cookies, so being signed in to
    /// ChatGPT in your normal browser does nothing for it, and a login wall
    /// looks exactly like a broken bridge from the outside.
    @objc private func testChat() {
        guard let delegate = appDelegate else { return }
        Task { @MainActor in
            let raw = await delegate.chatBridge.diagnose()
            var pretty = raw
            var signedOut = false
            if let data = raw.data(using: .utf8),
               let d = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                signedOut = (d["looksLoggedOut"] as? Bool == true) || (d["hasComposer"] as? Bool == false)
                pretty = d.keys.sorted().map { "\($0): \(d[$0] ?? "")" }.joined(separator: "\n")
            }
            print("=== chat bridge diagnostic ===\n\(pretty)")
            let alert = NSAlert()
            alert.messageText = signedOut ? "Bill is not signed in to ChatGPT" : "Chat connection looks healthy"
            alert.informativeText = (signedOut
                ? "Bill's chat view has its own cookies, separate from Safari or Brave — so signing in there doesn't sign him in. Open the full chat view and log in once.\n\n"
                : "") + pretty
            alert.addButton(withTitle: signedOut ? "Open Chat to Sign In" : "OK")
            alert.addButton(withTitle: "Copy")
            let choice = alert.runModal()
            if choice == .alertFirstButtonReturn, signedOut {
                delegate.showFullChat()
            } else if choice == .alertSecondButtonReturn {
                NSPasteboard.general.clearContents()
                NSPasteboard.general.setString(pretty, forType: .string)
            }
        }
    }

    /// Runs the whole window-awareness pipeline against whatever is frontmost
    /// and shows exactly what each stage produced.
    ///
    /// Every stage of awareness fails silently by design — a missing
    /// permission, an unreadable window and a title that matches no rule all
    /// look the same from outside (Bill just says nothing). This makes the
    /// difference visible.
    @objc private func testAwareness() {
        guard let monitor = appDelegate?.awarenessMonitor else { return }
        Task { @MainActor in
            // Give the user a moment to switch to the app they want tested —
            // otherwise the frontmost app is always Bill's own menu.
            let countdown = NSAlert()
            countdown.messageText = "Test screen awareness"
            countdown.informativeText = "Click Start, then bring the app you want to test to the front. Bill will look at it in 4 seconds."
            countdown.addButton(withTitle: "Start")
            countdown.addButton(withTitle: "Cancel")
            guard countdown.runModal() == .alertFirstButtonReturn else { return }

            try? await Task.sleep(nanoseconds: 4_000_000_000)
            let report = await monitor.diagnose()
            print("=== screen awareness diagnostic ===\n\(report)")

            let result = NSAlert()
            result.messageText = "Screen awareness diagnostic"
            result.informativeText = report
            result.addButton(withTitle: "OK")
            result.addButton(withTitle: "Copy")
            if result.runModal() == .alertSecondButtonReturn {
                NSPasteboard.general.clearContents()
                NSPasteboard.general.setString(report, forType: .string)
            }
        }
    }

    @objc private func toggleStudyMode() {
        guard let studyMode = appDelegate?.studyMode else { return }
        guard studyMode.isActive else {
            studyMode.start()
            return
        }
        // Cancelling costs a confirmation — see `StudyMode.cancel(confirmed:)`
        // for why it is possible at all.
        let minutes = Int((studyMode.remaining / 60).rounded(.up))
        let alert = NSAlert()
        alert.messageText = "End Study Mode early?"
        alert.informativeText = "There are \(minutes) minutes left. Bill will have opinions."
        alert.addButton(withTitle: "Keep Studying")
        alert.addButton(withTitle: "End Session")
        alert.alertStyle = .warning
        let confirmed = alert.runModal() == .alertSecondButtonReturn
        _ = studyMode.cancel(confirmed: confirmed)
    }

    private func makeDebugSubmenu() -> NSMenu {
        let submenu = NSMenu()
        for state in BillState.allCases {
            let item = NSMenuItem(title: state.rawValue.capitalized, action: #selector(forceState(_:)), keyEquivalent: "")
            item.target = self
            item.representedObject = state
            submenu.addItem(item)
        }
        return submenu
    }

    @objc private func talkToBill() {
        characterWindowController.talkToBill()
    }

    @objc private func openChat() {
        chatPanelController.toggle()
    }

    @objc private func refreshDialogue() {
        characterWindowController.refreshDialogueNow()
    }

    /// Opens the first-run/personalization setup window — the flow that
    /// has ChatGPT write Bill's per-app, per-time-of-day commentary for
    /// the apps actually on this Mac.
    @objc private func personalize() {
        appDelegate?.openPersonalizationSetup()
    }

    /// Opens the quotes manager — every pool, every line, sources, the
    /// refresh-everything button and the log strip.
    @objc private func openQuotesManager() {
        appDelegate?.openQuotesManager()
    }

    /// Forces a weather pull and a loud announcement — the on-demand
    /// pipeline check.
    @objc private func testWeather() {
        appDelegate?.testWeatherNow()
    }

    @objc private func openSettings() {
        settingsWindowController.show()
    }

    @objc private func forceState(_ sender: NSMenuItem) {
        guard let state = sender.representedObject as? BillState else { return }
        characterEngine.request(state, force: true)
    }

    @objc private func dumpState() {
        characterEngine.stateMachine.debugDump()
    }

    @objc private func testBark() {
        characterEngine.bark(BarkLines.random(from: BarkLines.coding))
    }

    @objc private func triggerWander() {
        characterWindowController.debugTriggerWander()
    }

    @objc private func showDialogueRefreshLog() {
        dialogueRefreshLogWindowController.show()
    }
}

extension StatusItemController: NSMenuDelegate {
    func menuNeedsUpdate(_ menu: NSMenu) {
        refreshStudyModeItem()
    }
}
