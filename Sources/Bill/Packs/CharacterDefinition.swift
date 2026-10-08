import Foundation
import CoreGraphics

/// One playable character, built from the shared-canvas sprite families in
/// `Resources/Packs/<pack>/Sprites/<prefix>_<family>_<NN>.png`.
///
/// Every character maps onto the SAME `BillState` space — that is the whole
/// design: the state machine, the reaction router, roaming physics, weather,
/// the chat bridge and the bark system all keep working untouched, whatever
/// is on screen. A pack only supplies three things: which texture family
/// each state plays (see `CharacterAnimationLibrary`), what size the frames
/// share (`canvasSize`, the anti-snap convention from `BillSpriteCatalog`),
/// and which dialogue file feeds its voice.
struct CharacterDefinition: Identifiable, Sendable, Hashable {
    let id: String
    let displayName: String
    let packID: String
    let packName: String
    /// File-name prefix of the sprite families. `"bill"` routes to the
    /// legacy `BillSpriteCatalog` (380 pre-processed frames) instead.
    let spritePrefix: String
    /// The one canvas size every frame of this character shares.
    let canvasSize: CGSize
    /// Canvas points → screen points. Tuned per character so their on-screen
    /// height feels right next to Bill's 1.9 × 111 ≈ 211pt.
    let displayScale: CGFloat
    /// Bundled dialogue JSON name (without extension). `nil` = the default
    /// `dialogue.json` — Bill's own pools, untouched.
    let dialogueResource: String?
    /// True when the character should stay on the desktop floor — plain
    /// left/right walks, no leaping onto windows, no climbing, no drops.
    /// Undertale/OneShot characters are grounded (their walks are flat,
    /// four-frame cycles; airborne poses read as glitches); the Knight and
    /// Hornet keep full platformer physics, and so does Bill.
    let prefersGroundedRoaming: Bool
    /// The second character that appears alongside this one when the pack
    /// defines a pair (Sans brings Papyrus, the Knight brings Hornet).
    let companionID: String?
    /// Sprite credit line — every pack's art must be attributed.
    let credit: String

    /// Convenience for roster entries — see `prefersGroundedRoaming`.
    init(
        id: String, displayName: String, packID: String, packName: String,
        spritePrefix: String, canvasSize: CGSize, displayScale: CGFloat,
        dialogueResource: String?, companionID: String? = nil,
        prefersGroundedRoaming: Bool = false, credit: String
    ) {
        self.id = id
        self.displayName = displayName
        self.packID = packID
        self.packName = packName
        self.spritePrefix = spritePrefix
        self.canvasSize = canvasSize
        self.displayScale = displayScale
        self.dialogueResource = dialogueResource
        self.companionID = companionID
        self.prefersGroundedRoaming = prefersGroundedRoaming
        self.credit = credit
    }

    func hash(into hasher: inout Hasher) { hasher.combine(id) }
    static func == (lhs: CharacterDefinition, rhs: CharacterDefinition) -> Bool { lhs.id == rhs.id }

    var isBill: Bool { id == "bill" }
}

/// The full playable roster, grouped by pack. The menu bar's Character
/// submenu is generated from this — adding a character is one entry here
/// plus its sprite families and dialogue file.
@MainActor
enum CharacterRoster {
    static let bill = CharacterDefinition(
        id: "bill",
        displayName: "Bill Cipher",
        packID: "bill",
        packName: "Gravity Falls",
        spritePrefix: "bill",
        canvasSize: CGSize(width: 118, height: 111),
        displayScale: 1.9,
        dialogueResource: nil,
        companionID: nil,
        credit: "Bill Cipher artwork by Kelly Nora (@kiernenking); sprite sheet by JayHyperStarX — deviantart.com/jayhyperstarx"
    )

    // MARK: Undertale

    static let sans = CharacterDefinition(
        id: "sans", displayName: "Sans", packID: "undertale", packName: "Undertale",
        spritePrefix: "sans", canvasSize: CGSize(width: 40, height: 37), displayScale: 5.0,
        dialogueResource: "dialogue_sans", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com (The Spriters Resource)"
    )
    static let papyrus = CharacterDefinition(
        id: "papyrus", displayName: "Papyrus", packID: "undertale", packName: "Undertale",
        spritePrefix: "papyrus", canvasSize: CGSize(width: 27, height: 43), displayScale: 4.3,
        dialogueResource: "dialogue_papyrus", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com"
    )
    static let frisk = CharacterDefinition(
        id: "frisk", displayName: "Frisk", packID: "undertale", packName: "Undertale",
        spritePrefix: "frisk", canvasSize: CGSize(width: 29, height: 29), displayScale: 6.4,
        dialogueResource: "dialogue_frisk", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com"
    )
    static let flowey = CharacterDefinition(
        id: "flowey", displayName: "Flowey", packID: "undertale", packName: "Undertale",
        spritePrefix: "flowey", canvasSize: CGSize(width: 25, height: 33), displayScale: 5.6,
        dialogueResource: "dialogue_flowey", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com"
    )
    static let temmie = CharacterDefinition(
        id: "temmie", displayName: "Temmie", packID: "undertale", packName: "Undertale",
        spritePrefix: "temmie", canvasSize: CGSize(width: 35, height: 28), displayScale: 6.6,
        dialogueResource: "dialogue_temmie", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com"
    )
    static let monsterkid = CharacterDefinition(
        id: "monsterkid", displayName: "Monster Kid", packID: "undertale", packName: "Undertale",
        spritePrefix: "monsterkid", canvasSize: CGSize(width: 30, height: 28), displayScale: 6.6,
        dialogueResource: "dialogue_monsterkid", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com"
    )
    static let annoyingdog = CharacterDefinition(
        id: "annoyingdog", displayName: "Annoying Dog", packID: "undertale", packName: "Undertale",
        spritePrefix: "annoyingdog", canvasSize: CGSize(width: 29, height: 33), displayScale: 5.6,
        dialogueResource: "dialogue_annoyingdog", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "Undertale sprites ripped by asym — spriters-resource.com"
    )

    static let sansdt = CharacterDefinition(
        id: "sansdt", displayName: "Sans (Battle)", packID: "undertale", packName: "Undertale",
        spritePrefix: "sansdt", canvasSize: CGSize(width: 29, height: 30), displayScale: 6.2,
        dialogueResource: "dialogue_sans", companionID: nil, prefersGroundedRoaming: true,
        credit: "Custom Deltarune battle-style Sans by askywalker — spriters-resource.com"
    )

    // MARK: OneShot

    static let niko = CharacterDefinition(
        id: "niko", displayName: "Niko", packID: "oneshot", packName: "OneShot",
        spritePrefix: "niko", canvasSize: CGSize(width: 23, height: 31), displayScale: 6.0,
        dialogueResource: "dialogue_niko", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "OneShot sprites ripped by accuratejaney — spriters-resource.com"
    )
    static let nikodt = CharacterDefinition(
        id: "nikodt", displayName: "Niko (Battle)", packID: "oneshot", packName: "OneShot",
        spritePrefix: "nikodt", canvasSize: CGSize(width: 21, height: 29), displayScale: 6.4,
        dialogueResource: "dialogue_niko", companionID: nil,
        prefersGroundedRoaming: true,
        credit: "OneShot custom sprites (Deltarune-style) — spriters-resource.com"
    )

    // MARK: Hollow Knight

    static let knight = CharacterDefinition(
        id: "knight", displayName: "The Knight", packID: "hollowknight", packName: "Hollow Knight",
        spritePrefix: "knight", canvasSize: CGSize(width: 179, height: 199), displayScale: 0.9,
        dialogueResource: "dialogue_knight", companionID: nil,
        credit: "Hollow Knight sprites from the community atlas rips — spriters-resource.com"
    )
    static let hornet = CharacterDefinition(
        id: "hornet", displayName: "Hornet", packID: "hollowknight", packName: "Hollow Knight",
        spritePrefix: "hornet", canvasSize: CGSize(width: 221, height: 215), displayScale: 0.9,
        dialogueResource: "dialogue_hornet", companionID: nil,
        credit: "Hollow Knight sprites from the community atlas rips — spriters-resource.com"
    )

    // MARK: Deltarune

    static let kris = CharacterDefinition(
        id: "kris", displayName: "Kris", packID: "deltarune", packName: "Deltarune",
        spritePrefix: "kris", canvasSize: CGSize(width: 73, height: 62), displayScale: 3.0,
        dialogueResource: "dialogue_kris", companionID: nil,
        credit: "Deltarune sprites ripped by asym, Eli101gamer, KoolTimYT, MrDoubleA, Sissel, Yuti, Bubbled — spriters-resource.com"
    )
    static let ralsei = CharacterDefinition(
        id: "ralsei", displayName: "Ralsei", packID: "deltarune", packName: "Deltarune",
        spritePrefix: "ralsei", canvasSize: CGSize(width: 57, height: 53), displayScale: 3.5,
        dialogueResource: "dialogue_ralsei", companionID: nil,
        credit: "Deltarune sprites ripped by asym, Luxandre, Sissel, TattleameliaMLG — spriters-resource.com"
    )
    static let susie = CharacterDefinition(
        id: "susie", displayName: "Susie", packID: "deltarune", packName: "Deltarune",
        spritePrefix: "susie", canvasSize: CGSize(width: 57, height: 62), displayScale: 3.0,
        dialogueResource: "dialogue_susie", companionID: nil,
        credit: "Deltarune sprites ripped by asym, Sissel, TattleameliaMLG — spriters-resource.com"
    )

    /// Menu/display order.
    static let all: [CharacterDefinition] = [
        bill,
        sans, sansdt, papyrus, frisk, flowey, temmie, monsterkid, annoyingdog,
        niko, nikodt,
        knight, hornet,
        kris, ralsei, susie,
    ]

    static func character(_ id: String) -> CharacterDefinition {
        all.first { $0.id == id } ?? bill
    }

    /// Pack groupings for the menu, in display order.
    static var packs: [(name: String, characters: [CharacterDefinition])] {
        var order: [String] = []
        var groups: [String: [CharacterDefinition]] = [:]
        for c in all where !c.isBill {
            if groups[c.packID] == nil { order.append(c.packID) }
            groups[c.packID, default: []].append(c)
        }
        return order.map { ($0, groups[$0]!) }
    }
}
