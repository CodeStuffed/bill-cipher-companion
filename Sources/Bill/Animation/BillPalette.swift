import SpriteKit

/// Bill's colour palette. This is an original stylised interpretation of his
/// silhouette (triangle, single eye, bow tie, top hat, cane) drawn procedurally
/// in code — no imported artwork.
enum BillPalette {
    static let bodyYellow = SKColor(red: 0.98, green: 0.78, blue: 0.15, alpha: 1)
    static let bodyYellowDark = SKColor(red: 0.72, green: 0.52, blue: 0.04, alpha: 1)
    static let eyeWhite = SKColor(white: 0.98, alpha: 1)
    static let pupilBlack = SKColor(red: 0.08, green: 0.05, blue: 0.02, alpha: 1)
    static let black = SKColor(red: 0.07, green: 0.07, blue: 0.09, alpha: 1)
    static let gloveWhite = SKColor(white: 0.95, alpha: 1)
    static let blush = SKColor(red: 1.0, green: 0.4, blue: 0.35, alpha: 0.55)

    // MARK: - User-tunable bubble accent (Settings → Appearance)

    /// The accent ring colour of every speech bubble (bark, chat messages,
    /// composer) — Bill's canon yellow unless the user recolours it. Set
    /// live by `AppDelegate` from `AppPreferences.bubbleAccentColorHex`;
    /// mutating triggers a bubble redraw on the next draw pass.
    /// `bodyYellow` stays constant: *Bill himself* is not recolourable
    /// from Settings, only his bubbles.
    @MainActor static var bubbleAccent: SKColor = bodyYellow

    /// Parses a 6-digit hex string (no `#`) into a colour, falling back to
    /// canon yellow on anything malformed — a typo in defaults storage
    /// must never turn the bubbles invisible.
    @MainActor static func color(fromHex hex: String) -> SKColor {
        let clean = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        var value: UInt64 = 0
        guard clean.count == 6, Scanner(string: clean).scanHexInt64(&value) else { return bodyYellow }
        let r = CGFloat((value >> 16) & 0xFF) / 255
        let g = CGFloat((value >> 8) & 0xFF) / 255
        let b = CGFloat(value & 0xFF) / 255
        return SKColor(red: r, green: g, blue: b, alpha: 1)
    }

    /// Hex string for the current `bubbleAccent` (round-trips the picker).
    @MainActor static var bubbleAccentHex: String {
        var red: CGFloat = 0, green: CGFloat = 0, blue: CGFloat = 0, alpha: CGFloat = 0
        bubbleAccent.getRed(&red, green: &green, blue: &blue, alpha: &alpha)
        let r = Int((red * 255).rounded()), g = Int((green * 255).rounded()), b = Int((blue * 255).rounded())
        return String(format: "%02x%02x%02x", r, g, b)
    }
}

/// Per-pack speech-bubble chrome. Bill keeps his hand-tuned yellow-accent
/// pixel style; each game pack gets its own *drawing type*, per the games:
/// Undertale's dialogue is the classic white box with a black border,
/// Deltarune's is a dark navy box, Hollow Knight's lore is a deep slate
/// tablet with pale text, OneShot's message boxes are soft blue. One
/// shared struct so bark bubbles, chat bubbles, headers and frames all
/// restyle together — no per-view if-chains.
@MainActor
enum BubbleTheme {
    struct Theme {
        let fill: NSColor
        let border: NSColor
        let accent: NSColor
        let text: NSColor
    }

    /// Bill — the classic look, unchanged: near-white fill, black border,
    /// user-accent stripe, black text.
    static let bill = Theme(
        fill: NSColor(calibratedWhite: 0.98, alpha: 1),
        border: BillPalette.black,
        accent: BillPalette.bubbleAccent,
        text: BillPalette.black
    )
    /// Undertale — the dialogue box every player knows: plain white fill,
    /// black border, no accent stripe, black text.
    static let undertale = Theme(
        fill: NSColor(calibratedWhite: 1.0, alpha: 1),
        border: NSColor.black,
        accent: NSColor.black,
        text: NSColor.black
    )
    /// Deltarune — dark navy battle box, white text, cyan accent.
    static let deltarune = Theme(
        fill: NSColor(calibratedRed: 0.05, green: 0.03, blue: 0.16, alpha: 1),
        border: NSColor.white,
        accent: NSColor(calibratedRed: 0.0, green: 0.85, blue: 1.0, alpha: 1),
        text: NSColor.white
    )
    /// Hollow Knight — the lore tablet: deep slate fill, pale carved
    /// text, pale bone accent.
    static let hollowknight = Theme(
        fill: NSColor(calibratedRed: 0.09, green: 0.09, blue: 0.13, alpha: 1),
        border: NSColor(calibratedWhite: 0.82, alpha: 1),
        accent: NSColor(calibratedWhite: 0.82, alpha: 1),
        text: NSColor(calibratedWhite: 0.92, alpha: 1)
    )
    /// OneShot — soft blue message box, deep blue text.
    static let oneshot = Theme(
        fill: NSColor(calibratedRed: 0.88, green: 0.93, blue: 1.0, alpha: 1),
        border: NSColor(calibratedRed: 0.13, green: 0.25, blue: 0.55, alpha: 1),
        accent: NSColor(calibratedRed: 0.13, green: 0.25, blue: 0.55, alpha: 1),
        text: NSColor(calibratedRed: 0.09, green: 0.15, blue: 0.35, alpha: 1)
    )

    /// The active character's pack — set at launch and on every switch
    /// (`AppDelegate.switchCharacter`). Defaults to Bill.
    static var packID: String = "bill"

    static var current: Theme {
        switch packID {
        case "undertale": return undertale
        case "deltarune": return deltarune
        case "hollowknight": return hollowknight
        case "oneshot": return oneshot
        default: return bill
        }
    }
}
