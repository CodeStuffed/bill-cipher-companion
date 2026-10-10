import SpriteKit
import Foundation

/// Spawns Hollow Knight enemies as free-roaming companions that fly,
/// collide with the main character, and have their own short quips.
///
/// The "add every enemy" toggle in Settings → Characters enables a batch
/// of enemies from the extracted pool. Each enemy is a full CompanionController
/// (its own rig, state machine, dialogue voice) but with:
/// - Flying movement (they hover and drift rather than walking)
/// - Collision detection against the main character (they bump, react, quip)
/// - Short enemy-appropriate dialogue (one or two lines each)
@MainActor
final class EnemySpawnController: NSObject {
    private var enemies: [CompanionController] = []
    private var spawnTimers: [DispatchWorkItem] = []
    private let characterEngine: CharacterEngine
    private let preferences: AppPreferences

    /// Maximum simultaneous enemies — more than this would be chaos.
    static let maxEnemies = 6
    /// How often a new enemy spawns (if below the cap and the toggle is on).
    static let spawnInterval: TimeInterval = 45
    /// How long an enemy stays before despawning.
    static let enemyLifetime: TimeInterval = 300

    init(characterEngine: CharacterEngine, preferences: AppPreferences) {
        self.characterEngine = characterEngine
        self.preferences = preferences
        super.init()
    }

    /// Enemy IDs from the extraction that are most visually distinct
    /// and fun to have on screen. Each has a one-line quip.
    static let enemyPool: [(id: String, quip: String)] = [
        ("enemy_crawlid", "* skitter skitter *"),
        ("enemy_tiktik", "* tick tick tick *"),
        ("enemy_vengefly", "* BZZZZ *"),
        ("enemy_aspidhunter", "* hiss *"),
        ("enemy_huskwarrior", "..."),
        ("enemy_mantiswarrior", "* clicks mandibles *"),
        ("enemy_mossknight", "* rustle *"),
        ("enemy_glimback", "* hums softly *"),
        ("enemy_lifeseed", "* pulses gently *"),
        ("enemy_chargedlumafly", "* zap *"),
        ("enemy_sibling", "..."),
        ("enemy_shade", "..."),
        ("enemy_lessermawlek", "* screech *"),
        ("enemy_maggot", "* wiggle *"),
        ("enemy_grubmimic", "* pretends to be a grub *"),
        ("enemy_baldur", "* roll roll roll *"),
        ("enemy_hopper", "* boing *"),
        ("enemy_wanderinghusk", "..."),
        ("enemy_cowardlyhusk", "* backs away *"),
        ("enemy_mosscreep", "* creeps *"),
        ("enemy_voidtendrils", "* reaches *"),
        ("enemy_mistake", "* writhes *"),
        ("enemy_kingsmould", "* stands guard *"),
        ("enemy_soulwisp", "* flickers *"),
    ]

    func startSpawningIfEnabled() {
        stopSpawning()
        guard preferences.isEnemySpawningEnabled else { return }
        scheduleNextSpawn()
    }

    func stopSpawning() {
        spawnTimers.forEach { $0.cancel() }
        spawnTimers.removeAll()
        enemies.forEach { $0.detach() }
        enemies.removeAll()
    }

    private func scheduleNextSpawn() {
        let work = DispatchWorkItem { [weak self] in
            self?.spawnEnemy()
            self?.scheduleNextSpawn()
        }
        spawnTimers.append(work)
        DispatchQueue.main.asyncAfter(deadline: .now() + Self.spawnInterval, execute: work)
    }

    private func spawnEnemy() {
        guard preferences.isEnemySpawningEnabled,
              enemies.count < Self.maxEnemies else { return }

        // Pick a random enemy from the pool
        guard let (enemyId, quip) = Self.enemyPool.randomElement() else { return }

        // Verify the enemy has sprites
        let definition = CharacterDefinition.enemy(id: enemyId, quip: quip)
        let catalog = CharacterSpriteCatalog(definition: definition)
        guard !catalog.frames("idle").isEmpty else { return }

        let enemy = CompanionController(
            definition: definition,
            barkSink: { [weak self] text in
                self?.characterEngine.bark(text, importance: .always)
            }
        )
        enemies.append(enemy)
        NotificationCenter.default.post(
            name: .enemySpawned,
            object: nil,
            userInfo: ["id": enemyId, "controller": enemy]
        )

        // Auto-despawn after the lifetime
        let despawn = DispatchWorkItem { [weak self, weak enemy] in
            guard let self, let enemy else { return }
            enemy.detach()
            self.enemies.removeAll { $0 === enemy }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + Self.enemyLifetime, execute: despawn)
    }

    var activeEnemyCount: Int { enemies.count }
    var activeEnemies: [CompanionController] { enemies }
}

extension Notification.Name {
    static let enemySpawned = Notification.Name("enemySpawned")
}

extension CharacterDefinition {
    /// Factory for enemy definitions — enemies are lightweight,
    /// auto-spawned, and have single-quip dialogue.
    static func enemy(id: String, quip: String) -> CharacterDefinition {
        CharacterDefinition(
            id: id,
            displayName: id.replacingOccurrences(of: "enemy_", with: "")
                .replacingOccurrences(of: "_", with: " ").capitalized,
            packID: "hollowknight",
            packName: "Hollow Knight",
            spritePrefix: id,
            canvasSize: CGSize(width: 100, height: 100), // placeholder — updated at spawn
            displayScale: 1.0,
            dialogueResource: nil,
            companionID: nil,
            prefersGroundedRoaming: false,
            prefersStationary: false,
            credit: "Hollow Knight enemy sprites from community rips"
        )
    }
}
