# Bill 1.1.1 — The Never-Stuck Patch

A focused bug-fix release for the two things 1.1.0 still got wrong.

## Fixed

- **Never stuck at the menu bar again.** Three layered fixes:
  - A beat that ended while Bill was mid-climb on a window's side left him *hanging in mid-air between beats* — nothing ticked there, so nothing ever freed him. Every beat boundary now releases any lingering grab.
  - A new watchdog in the physics sim: six seconds of clinging-without-climbing or floating-with-zero-velocity force-drops him. No geometry edge case can hold him anywhere anymore.
  - Windows whose tops sit flush with the working area's ceiling are no longer "furniture" at all — every path that let him linger in the menu-bar zone started with one.
- **Bark bubble clipping with large text.** The speech-text-size setting multiplies the whole bubble bitmap, which could grow it past the character window's headroom. Bubbles now measure the vertical room they actually have and wrap to it.
- **Demo GIFs** on the site and README loop pingpong and render Bill at his original colours (the old encoder made his yellow body transparent on dark backgrounds — that's what looked "inverted").

> Unofficial, non-commercial fan project. Bill Cipher and Gravity Falls are © Disney. Not affiliated with or endorsed by Disney.

## Install

Download **Bill-macOS.dmg** below, open it, drag **Bill** onto the **Applications** shortcut, and right-click → Open on first launch (ad-hoc signed, not notarized).

**Requires** macOS 14 (Sonoma) or newer, and a ChatGPT account signed in once inside Bill's own chat window.

---

*Reality is an illusion, the universe is a hologram, buy gold, bye!*
