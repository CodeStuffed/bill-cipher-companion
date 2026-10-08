#!/usr/bin/env python3
"""
Process extracted pack sprites into app-ready frame families.

Every character gets ONE shared canvas (the max bounding box across all its
families), with each frame's content bottom-center aligned onto it — the
same anti-snap convention BillSpriteCatalog uses (see its doc comment).
Output: Sources/Bill/Resources/Packs/<pack>/Sprites/<char>_<family>_<NN>.png
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

SRC = pathlib.Path(__file__).resolve().parent.parent / "build-assets" / "extracted"
DST = pathlib.Path(__file__).resolve().parent.parent / "Sources" / "Bill" / "Resources" / "Packs"

# char -> { family: (pack, section-or-pattern, start, count) }
MAPPINGS = {
    "sans": {
        "idle": ("undertale/sans", "basic-down", 0, 4),
        "walking": ("undertale/sans", "basic-left", 0, 4),
        "talking": ("undertale/sans", "basic-down", 0, 4),
        "happy": ("undertale/sans", "trick", 0, 4),
        "annoyed": ("undertale/sans", "shrug", 0, 3),
        "surprised": ("undertale/sans", "shrug", 1, 3),
        "sleeping": ("undertale/sans", "sleep", 0, 2),
        "coding": ("undertale/sans", "stool", 0, 2),
        "gaming": ("undertale/sans", "stool-comb", 0, 3),
        "charging": ("undertale/sans", "stool-cup", 0, 8),
        "celebrating": ("undertale/sans", "trombone", 0, 4),
        "smug": ("undertale/sans", "trick", 1, 4),
        "heating": ("undertale/sans", "darkbg", 0, 2),
        "confused": ("undertale/sans", "basic-up", 0, 4),
        "dazed": ("undertale/sans", "laugh-unused", 0, 2),
        "poked": ("undertale/sans", "handshake", 0, 4),
        "ghost": ("undertale/sans", "shadow-left", 0, 3),
        "dining": ("undertale/sans", "icecream-unused", 0, 10),
    },
    "sansdt": {
        # Battle strip rows — visible-expression rows only. Rows 06-08 are
        # the sheet's full-black dramatic frames (dropped by the black-frame
        # filter); 09-12 carry the actual expression beats.
        "idle": ("undertale/sans-battle", "row01", 0, 8),
        "talking": ("undertale/sans-battle", "row03", 0, 12),
        "happy": ("undertale/sans-battle", "row09", 0, 8),
        "surprised": ("undertale/sans-battle", "row11", 0, 8),
        "annoyed": ("undertale/sans-battle", "row02", 0, 8),
        "dazed": ("undertale/sans-battle", "row12", 0, 8),
    },
    "papyrus": {
        "idle": ("undertale/papyrus", "row01", 0, 4),
        "walking": ("undertale/papyrus", "row02", 0, 4),
        "talking": ("undertale/papyrus", "row07", 0, 6),
        "happy": ("undertale/papyrus", "row05", 0, 4),
        "annoyed": ("undertale/papyrus", "row10", 0, 4),
        "surprised": ("undertale/papyrus", "row09", 0, 3),
        "celebrating": ("undertale/papyrus", "row08", 0, 6),
        "confused": ("undertale/papyrus", "row04", 0, 2),
        "back": ("undertale/papyrus", "row04", 0, 4),
    },
    "frisk": {
        "idle": ("undertale/frisk", "row12", 0, 4),
        "walking": ("undertale/frisk", "row11", 0, 4),
        "talking": ("undertale/frisk", "row09", 0, 4),
        "happy": ("undertale/frisk", "row07", 0, 4),
        "surprised": ("undertale/frisk", "row10", 0, 4),
    },
    "flowey": {
        # "talk" holds two identical default-face boxes — idle plays the
        # real 9-frame face-morph cycle so Flowey actually moves on his own.
        "idle": ("undertale/flowey", "face-grow", 0, 9),
        "talking": ("undertale/flowey", "talk", 0, 2),
        "happy": ("undertale/flowey", "face-grow", 0, 2),
        "annoyed": ("undertale/flowey", "shrink", 0, 2),
        "laugh": ("undertale/flowey", "laugh", 0, 8),
        "surprised": ("undertale/flowey", "face-shrink", 0, 2),
        "evil": ("undertale/flowey", "face-grow", 0, 4),
    },
    "temmie": {
        # Flood-fill extraction rows (purple no longer eats tEM's fur):
        # row01=idle-talk(4), row02=hoi(5), row03=hoi-talk(2), row04/05=walk.
        "idle": ("undertale/temmie", "row01", 0, 4),
        "happy": ("undertale/temmie", "row02", 0, 4),
        "talking": ("undertale/temmie", "row03", 0, 2),
        "walking": ("undertale/temmie", "row04", 0, 4),
        "surprised": ("undertale/temmie", "row06", 0, 1),
    },
    "monsterkid": {
        # row01 is the verified period-4 walk cycle — the later rows mix
        # facing directions (the "sometimes flipped" frames).
        "idle": ("undertale/monsterkid", "row1-l4", 0, 4),
        "walking": ("undertale/monsterkid", "row01", 0, 8),
        "talking": ("undertale/monsterkid", "row04", 0, 4),
        "happy": ("undertale/monsterkid", "row07", 0, 4),
        "surprised": ("undertale/monsterkid", "row05", 0, 4),
        "goner": ("undertale/monsterkid", "row1-l424", 0, 2),
    },
    "annoyingdog": {
        "idle": ("undertale/annoyingdog", "row01", 0, 1),
        "walking": ("undertale/annoyingdog", "row10", 0, 4),
        "talking": ("undertale/annoyingdog", "row03", 0, 2),
        "happy": ("undertale/annoyingdog", "row03", 2, 2),
        "sleeping": ("undertale/annoyingdog", "row05", 0, 1),
    },
    "nikoow": {
        "idle": ("oneshot/niko", "row03", 0, 3),
        "walking": ("oneshot/niko", "row01", 0, 3),
        "walkup": ("oneshot/niko", "row05", 0, 3),
        "talking": ("oneshot/niko", "row07", 0, 3),
        "happy": ("oneshot/niko", "row07", 3, 3),
        "sad": ("oneshot/niko", "row07", 9, 3),
        "surprised": ("oneshot/niko", "row09", 0, 3),
    },
    "niko": {
        # The DEFAULT Niko is the battle-style sheet now (user preference),
        # re-extracted with flood-fill so no purple eats the colors. Each
        # row is one 8-frame pose cycle (repeated 3x on the sheet).
        "idle": ("oneshot/niko-deltarune", "row01", 0, 8),
        "walking": ("oneshot/niko-deltarune", "row01", 0, 8),
        "talking": ("oneshot/niko-deltarune", "row02", 0, 8),
        "happy": ("oneshot/niko-deltarune", "row03", 0, 8),
        "sad": ("oneshot/niko-deltarune", "row04", 0, 8),
        "surprised": ("oneshot/niko-deltarune", "row05", 0, 8),
    },

    "knight": {
        "idle": ("hollowknight/knight", "row01", 0, 4),
        "walking": ("hollowknight/knight", "row03", 0, 7),
        "talking": ("hollowknight/knight", "row16", 0, 5),
        "happy": ("hollowknight/knight", "row10", 0, 9),
        "attack": ("hollowknight/knight", "row35", 0, 17),
        "surprised": ("hollowknight/knight", "row13", 0, 5),
        "dazed": ("hollowknight/knight", "row50", 0, 8),
        "sit": ("hollowknight/knight", "row23", 0, 6),
        "focus": ("hollowknight/knight", "row30", 0, 6),
    },
    "hornet": {
        "idle": ("hollowknight/hornet", "idle", 0, 2),
        "walking": ("hollowknight/hornet", "oc-row01", 0, 6),
        "talking": ("hollowknight/hornet", "oc-row05", 0, 4),
        "happy": ("hollowknight/hornet", "oc-row07", 0, 8),
        "jump": ("hollowknight/hornet", "jump", 0, 10),
        "land": ("hollowknight/hornet", "hardland", 0, 6),
        "throw": ("hollowknight/hornet", "throwside", 0, 8),
    },
    "kris": {
        "idle": ("deltarune/kris", "idle", 0, 4),
        "walking": ("deltarune/kris", "basic-movements", 0, 8),
        "talking": ("deltarune/kris", "act", 0, 4),
        "happy": ("deltarune/kris", "item", 0, 4),
        "annoyed": ("deltarune/kris", "defend", 0, 4),
        "surprised": ("deltarune/kris", "prepare", 0, 4),
        "attack": ("deltarune/kris", "attack-intro", 0, 8),
        "celebrating": ("deltarune/kris", "hug-raise", 0, 4),
    },
    "ralsei": {
        # Full-body rows only (23x43 class); the 17x18 rows are head
        # closeups that read as glitched partial sprites on the desktop.
        "idle": ("deltarune/ralsei", "row03", 0, 4),
        "walking": ("deltarune/ralsei", "row05", 0, 4),
        "talking": ("deltarune/ralsei", "row04", 0, 4),
        "happy": ("deltarune/ralsei", "row09", 0, 4),
        "annoyed": ("deltarune/ralsei", "row11", 0, 4),
        "surprised": ("deltarune/ralsei", "row10", 0, 4),
        "sad": ("deltarune/ralsei", "row06", 0, 4),
    },
    "susie": {
        # Flood-fill rows — her purple hair survived extraction this time.
        "idle": ("deltarune/susie", "row01", 0, 4),
        "walking": ("deltarune/susie", "row03", 0, 6),
        "talking": ("deltarune/susie", "row04", 0, 4),
        "happy": ("deltarune/susie", "row05", 0, 4),
        "annoyed": ("deltarune/susie", "row07", 0, 4),
        "surprised": ("deltarune/susie", "row08", 0, 4),
        "laugh": ("deltarune/susie", "row09", 0, 4),
    },
}

PACK_OF = {
    "sans": "undertale", "papyrus": "undertale", "toriel": "undertale", "undyne": "undertale",
    "frisk": "undertale", "flowey": "undertale", "temmie": "undertale", "monsterkid": "undertale",
    "annoyingdog": "undertale", "sansdt": "undertale", "niko": "oneshot", "nikoow": "oneshot", "knight": "hollowknight", "hornet": "hollowknight",
    "kris": "deltarune", "ralsei": "deltarune", "susie": "deltarune",
}


def load_family(char, family, spec):
    pack_sec, pattern, start, count = spec
    base = SRC / pack_sec
    matches = sorted(p for p in base.iterdir() if p.name == pattern)
    if not matches:
        # fall back to prefix match
        matches = sorted(p for p in base.iterdir() if p.name.startswith(pattern))
    if not matches:
        print(f"  MISSING section {pack_sec}/{pattern} for {char}/{family}")
        return []
    files = sorted(matches[0].glob("*.png"))
    picked = files[start:start + count]
    raw = []
    for f in picked:
        a = np.asarray(Image.open(str(f)).convert("RGBA"))
        al = a[:, :, 3] > 10
        ys, xs = np.where(al)
        if len(ys) == 0:
            continue  # blank frame — never ship an invisible flash
        raw.append(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    if len(raw) >= 4:
        # Quality filter, per frame vs the family's medians — three real
        # bug classes this kills:
        #  - half-body crops ("sans clips half his body repeatedly"):
        #    torn row splits whose content is far narrower/shorter than
        #    their siblings
        #  - black/blank frames (Monster Kid's flip rows)
        #  - tiny fragments (the dog's weird small sprite)
        widths = sorted(f.shape[1] for f in raw)
        heights = sorted(f.shape[0] for f in raw)
        median_w = widths[len(widths) // 2]
        median_h = heights[len(heights) // 2]
        kept = []
        for f in raw:
            if f.shape[1] < 0.6 * median_w or f.shape[0] < 0.55 * median_h:
                continue  # torn crop / fragment
            al = f[:, :, 3] > 10
            if not al.any():
                continue  # blank
            lum = 0.299*f[:,:,0] + 0.587*f[:,:,1] + 0.114*f[:,:,2]
            if lum[al].mean() < 35:
                continue  # near-solid-black frame
            kept.append(f)
        raw = kept if kept else raw  # never return nothing
    return raw


def available_rows(char):
    """Every extraction row for this character, as (row_name, frame_paths)."""
    pack = PACK_OF[char]
    base = SRC / pack / char
    rows = {}
    if base.exists():
        for sec in sorted(base.iterdir()):
            if not sec.is_dir():
                continue
            files = sorted(sec.glob("*.png"))
            if files:
                rows[sec.name] = files
    return rows


def main():
    manifest = {}
    for char, families in MAPPINGS.items():
        pack = PACK_OF[char]
        out_dir = DST / pack / "Sprites"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Claimed rows: everything a core family already slices from.
        claimed = {spec[1].split(" ")[0] for spec in families.values()}
        # Auto-wire every remaining row as an "x" family so the entire
        # sheet is playable — 16 frames per family keeps beats snappy on
        # the giant battle rows.
        rows = available_rows(char)
        extras = 0
        for row_name, files in sorted(rows.items()):
            if row_name in claimed:
                continue
            if len(families) > 40 and not row_name.startswith("row"):
                continue  # curated sections already serve this character
            families[f"x{extras + 1:02d}"] = (f"{pack}/{char}", row_name, 0, min(16, len(files)))
            extras += 1
            if extras >= 64:
                break

        # collect all families first
        all_frames = {}
        for family, spec in families.items():
            frames = load_family(char, family, spec)
            if frames:
                all_frames[family] = frames
        if not all_frames:
            print(f"{char}: NO FRAMES, skipped")
            continue
        # Shared canvas: sized by the CORE families, plus any auto-extra
        # that fits within 1.45x of them. Oversized cutscene strips are
        # dropped entirely — a 114px-wide strip on a 40px body is how the
        # canvas ballooned and every core sprite ended up squashed-small.
        core = {k: v for k, v in all_frames.items() if not k.startswith("x")}
        core_w = max(f.shape[1] for frs in core.values() for f in frs)
        core_h = max(f.shape[0] for frs in core.values() for f in frs)
        dropped = []
        for name in list(all_frames.keys()):
            if name.startswith("x"):
                fw = max(f.shape[1] for f in all_frames[name])
                fh = max(f.shape[0] for f in all_frames[name])
                if fw > core_w * 1.45 or fh > core_h * 1.45:
                    # Integer downscale (clean nearest steps) until the row
                    # fits 1.45x the core canvas — full-sheet coverage
                    # without ballooning the shared canvas or squashing
                    # every core sprite.
                    factor = 2
                    while factor <= 8:
                        if fw // factor <= core_w * 1.45 and fh // factor <= core_h * 1.45:
                            break
                        factor += 1
                    if factor > 8:
                        dropped.append(name)
                        del all_frames[name]
                        continue
                    from PIL import Image as _I
                    scaled = []
                    for f in all_frames[name]:
                        img = _I.fromarray(f)
                        img = img.resize((f.shape[1] // factor, f.shape[0] // factor), _I.NEAREST)
                        scaled.append(np.asarray(img))
                    all_frames[name] = scaled
        maxw = max(f.shape[1] for frs in all_frames.values() for f in frs)
        maxh = max(f.shape[0] for frs in all_frames.values() for f in frs)
        char_man = {"canvas": [maxw, maxh], "families": {}}
        if dropped:
            print(f"  {char}: dropped {len(dropped)} oversized extras (>{core_w * 1.45:.0f}x{core_h * 1.45:.0f})")
        for family, frames in all_frames.items():
            char_man["families"][family] = len(frames)
            for n, f in enumerate(frames, 1):
                canvas = np.zeros((maxh, maxw, 4), dtype=np.uint8)
                h, w = f.shape[:2]
                # bottom-center align
                y0 = maxh - h
                x0 = (maxw - w) // 2
                canvas[y0:y0 + h, x0:x0 + w] = f
                Image.fromarray(canvas).save(out_dir / f"{char}_{family}_{n:02d}.png")
        manifest[char] = char_man
        fams = ", ".join(f"{k}:{v}" for k, v in sorted(char_man["families"].items()))
        print(f"{char}: canvas {maxw}x{maxh} — {fams}")

    json.dump(manifest, open(DST / "packs_manifest.json", "w"), indent=1)
    print(f"\nwrote {DST / 'packs_manifest.json'}")


if __name__ == "__main__":
    main()
