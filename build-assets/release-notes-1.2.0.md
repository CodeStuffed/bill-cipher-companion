# Bill 1.2.0 — The Windows Rewrite Begins

The biggest release yet: the weather pipeline is finally visible and controllable, a full Quotes Manager opens the entire dialogue library, the app-study setup is guided and transparent — and the Windows port starts here.

> Unofficial, non-commercial fan project. Bill Cipher and Gravity Falls are © Disney. Not affiliated with or endorsed by Disney.

## New in 1.2.0

### Weather you can actually see (and control)
The #1 report was *"I never saw him say anything about the weather."* Fair — the old logic only spoke on condition **changes**, so steady weather meant silence. Now:
- **The first successful pull of every session always announces, loudly.**
- **A "mention the current weather every N minutes" setting** (off / 15–240 min) covers steady days.
- **Settings → Weather**: the enable toggle, the interval stepper, and a **Test Weather Now** button that force-pulls and announces on the spot (also in the menu bar) — so you can verify the pipeline in one click instead of trusting it.
- Condition changes (rain starting, skies clearing) still announce within minutes via the radar nowcast.

### The Quotes Manager
**Settings → Prompts → Open the Quotes Manager** (or the menu bar): every quote pool, live counts, and **A/G/P badges** showing which lines are Authored, ChatGPT-Generated, or Personalized to your apps. Click any pool to read every line, bucketed by time of day, tagged by source. One button refreshes **every single pool** (only study-mode enforcement lines stay hand-written), and each refresh log entry now opens with a plain-words summary — *"18 new lines in 7 pools: weather.rain×3, coding×2…"* — with the three latest outcomes pinned in the manager.

### Guided app study
The personalization setup now shows **every app it detected before you commit**, then fills in live per-app line counts as each generation batch lands. No promises you have to trust — the list is right there.

### One new Easter egg
The sprite sweep found the retired summoning-buildup sequence hiding in the bundle — it's back as the `ritualBuildup` rare event, anchored and voiced properly.

### Windows — the rewrite begins
**`Bill-Windows-Preview.zip`** is Milestone 1 of the published port plan: a real, compiling Windows app with Bill as a layered always-on-top window, per-pixel click-through outside his silhouette, idle and walk animation, and drag-to-move (he walks while you drag).

**Honest labeling:** this is the *shell* only — no chat, roaming, awareness, or settings yet (those are Milestones 2–6 in `docs/notes/WindowsPortPlan.md`). It was cross-compiled from macOS and **has not been run on a Windows machine yet** — if you try it, it needs the [.NET 8 Desktop Runtime](https://dotnet.microsoft.com/download/dotnet/8.0), and issue reports are worth their weight in gold. Source lives in `windows/` in this repo.

## Install (macOS)

Download **Bill-macOS.dmg** below, open it, drag **Bill** onto the **Applications** shortcut beside him, and right-click → Open on first launch (ad-hoc signed, not notarized).

**Requires** macOS 14 (Sonoma) or newer, and a ChatGPT account signed in once inside Bill's own chat window.

---

*Reality is an illusion, the universe is a hologram, buy gold, bye!*
