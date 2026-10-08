# Bill 1.3.0 — Windows Preview 0.2: The Brain

The Mac app is unchanged since 1.2.0; this release ships the next Windows port milestone (its mac DMG/zip are included for completeness — same build as 1.2.0).

> Unofficial, non-commercial fan project. Bill Cipher and Gravity Falls are © Disney. Not affiliated with or endorsed by Disney.

## Windows Preview 0.2 (Milestone W2 of the port plan)

Preview 0.1 was the shell. **Preview 0.2 has the brain.**

- **All 66 animation families play**, at the exact per-family frame durations the Mac app uses — 380 sprites shipped as resources.
- **He's alive between clicks**: ambient idle-variant rotation every 8–16s, and a 10%-per-beat rare Easter egg roll (power surge, zodiac vision, the ritual, the meltdown…).
- **Pixel speech bubbles**: the layered black/yellow/white border, properly rounded pixel corners, blocky tail and the hand-built 5×7 dot-matrix font — transcribed from the Swift table, not re-imagined — rendered into a click-through layered window above him.
- **He talks from the same dialogue file as the Mac app**: `dialogue.json` is shared verbatim, with time-of-day buckets ("MIDNIGHT IS PRIME SUMMONING HOURS" won't show up at noon), fallback ladders and no-repeat selection.
- **Menu**: "Say something" (time-of-day aware), "Play a random animation", About, Quit.

**Honest labeling, unchanged:** compile-verified (cross-compiled from macOS), **not yet run on a Windows machine** — needs the [.NET 8 Desktop Runtime](https://dotnet.microsoft.com/download/dotnet/8.0). No chat, roaming physics, awareness or settings yet — those are Milestones 3–6 in [`docs/notes/WindowsPortPlan.md`](https://github.com/Jasonilization/bill-cipher-companion/blob/main/docs/notes/WindowsPortPlan.md). Issue reports from any Windows machine are gold.

## Install

- **macOS**: `Bill-macOS.dmg` below — open, drag Bill onto the Applications shortcut, right-click → Open on first launch. macOS 14+.
- **Windows**: `Bill-Windows-Preview.zip` — unzip, run `Bill.exe`. Requires the .NET 8 Desktop Runtime. Drag him around; he walks while you drag.

---

*Reality is an illusion, the universe is a hologram, buy gold, bye!*
