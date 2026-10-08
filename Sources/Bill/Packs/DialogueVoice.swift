import Foundation

/// A self-contained dialogue voice for one character — the companion's
/// counterpart to `DialogueLibrary`.
///
/// Why this exists: the shared `DialogueLibrary` holds the *primary*
/// character's pools (plus Bill's generated/personalized halves). Before
/// this type, a companion's beats pulled lines from the shared library,
/// so Papyrus-as-companion would speak *Sans's* lines — the voice swap
/// only ever applied to whoever was primary. A `DialogueVoice` loads one
/// character's bundled file and serves no-repeat random lines from it,
/// independent of what the primary is saying.
@MainActor
final class DialogueVoice {
    private var pools: [String: DialoguePool] = [:]
    private var lastLine: [String: String] = [:]

    init(character: CharacterDefinition) {
        guard let resource = character.dialogueResource,
              let url = Bundle.module.url(forResource: resource, withExtension: "json", subdirectory: "Packs/Dialogue")
        else { return }
        do {
            let data = try Data(contentsOf: url)
            pools = try JSONDecoder().decode([String: DialoguePool].self, from: data)
        } catch {
            print("DialogueVoice: \(character.id) decode failed: \(error)")
        }
    }

    func line(_ key: String, substitutions: [String: String] = [:]) -> String? {
        let bucket = TimeOfDayCache.current
        var candidates = pools[key]?.lines(for: bucket) ?? []
        guard !candidates.isEmpty else { return nil }
        if candidates.count > 1, let previous = lastLine[key] {
            candidates.removeAll { $0 == previous }
        }
        guard let chosen = candidates.randomElement() else { return nil }
        lastLine[key] = chosen
        return DialogueLibrary.resolve(chosen, substitutions: substitutions)
    }

    func line(_ key: DialogueKey, substitutions: [String: String] = [:]) -> String? {
        line(key.rawValue, substitutions: substitutions)
    }
}
