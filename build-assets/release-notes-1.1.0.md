# Bill 1.1.0 — He Learns the Room

Bill Cipher lives on your desktop: a hand-drawn 380-sprite pixel-art companion, native Swift end to end, with desktop physics, app awareness, weather, and a real ChatGPT session behind the chat.

> Unofficial, non-commercial fan project. Bill Cipher and Gravity Falls are © Disney. Not affiliated with or endorsed by Disney.

## New in 1.1.0

- **Settings is a real control surface now** — recolour his speech bubbles, scale the bark text, resize the chat window, dial idle-animation pacing, pin individual reactions to specific animations, choose how many times a day his prompts refresh (spread across the day, 1–6×), and write extra persona instructions that ride along with every prompt. Everything applies live.
- **Minimize-button mischief** — very occasionally, Bill leaps onto a background window's yellow traffic light, plays a satisfied finger-snap, and *actually minimizes it* — then falls through where its top edge used to be. Never the window you're working in. Cooldown-gated, and toggleable in Settings.
- **Bubble polish** — properly rounded pixel corners; the bark bubble shifts left/right toward on-screen room with its tail staying over Bill; long URLs and code tokens wrap instead of clipping at the edge.
- **Anchored blasts** — shooting-style animations no longer shove Bill backward; his body stays planted while the beams fly.
- **No more menu-bar hang** — window "furniture" is clamped to the walkable screen area, killing the grab–clamp–fall loop under the menu bar.
- **First-run personalization** — Bill offers to use his ChatGPT connection to write himself a morning/midday/afternoon/night line for every app on your Mac, plus transition quips for your most-used pairs — generated on your machine, in his voice, live as each batch lands.
- **Weather that keeps up** — keyless Open-Meteo radar nowcast every 5 minutes: rain is announced while it's *starting* to rain, and today's conditions ride into his chat context.
- **Runs on more Macs** — deployment target is now macOS 14 (Sonoma): the chat bridge drives a classic WKWebView on older systems (same scripts, same behaviour) with ultraThinMaterial standing in for Liquid Glass.
- **Bigger app icon**, and the [Windows port plan](https://github.com/Jasonilization/bill-cipher-companion/blob/main/docs/notes/WindowsPortPlan.md) is published — Windows and Linux builds are coming soon.

## Install

1. Download **Bill-macOS.dmg** below (a plain `Bill-macOS.zip` is there too).
2. Open it and drag **Bill** onto the **Applications** shortcut beside him.
3. First launch: **right-click → Open** (ad-hoc signed, not notarized).
4. Check the menu bar. He's already watching — and shortly he'll offer to study your apps.

**Requires** macOS 14 (Sonoma) or newer, and a ChatGPT account signed in once inside Bill's own chat window (he has his own browser; your normal login doesn't carry over).

---

*Reality is an illusion, the universe is a hologram, buy gold, bye!*
