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
    "toriel": {
        "idle": ("undertale/toriel", "row01", 0, 3),
        "walking": ("undertale/toriel", "row03", 0, 4),
        "talking": ("undertale/toriel", "row04", 0, 4),
        "happy": ("undertale/toriel", "handhold", 0, 3),
        "annoyed": ("undertale/toriel", "row09", 0, 3),
        "surprised": ("undertale/toriel", "row08", 0, 3),
        "sleeping": ("undertale/toriel", "chair-sleep", 0, 2),
        "coding": ("undertale/toriel", "chair-talk", 0, 4),
        "gaming": ("undertale/toriel", "chair-getup", 0, 4),
        "celebrating": ("undertale/toriel", "unused", 0, 4),
    },
    "undyne": {
        "idle": ("undertale/undyne", "armor", 0, 4),
        "walking": ("undertale/undyne", "row16-l189", 0, 6),
        "talking": ("undertale/undyne", "nohelmet", 0, 4),
        "happy": ("undertale/undyne", "row21", 0, 5),
        "annoyed": ("undertale/undyne", "noarmor", 0, 3),
        "surprised": ("undertale/undyne", "row15", 0, 4),
        "attack": ("undertale/undyne", "row35", 0, 6),
    },
    "frisk": {
        "idle": ("undertale/frisk", "row03", 0, 4),
        "walking": ("undertale/frisk", "row02", 0, 4),
        "talking": ("undertale/frisk", "row09", 0, 4),
        "happy": ("undertale/frisk", "row07", 0, 6),
        "surprised": ("undertale/frisk", "row12", 0, 4),
    },
    "flowey": {
        "idle": ("undertale/flowey", "talk", 0, 2),
        "talking": ("undertale/flowey", "talk", 0, 2),
        "happy": ("undertale/flowey", "face-grow", 0, 2),
        "annoyed": ("undertale/flowey", "shrink", 0, 2),
        "laugh": ("undertale/flowey", "laugh", 0, 8),
        "surprised": ("undertale/flowey", "face-shrink", 0, 2),
        "evil": ("undertale/flowey", "face-grow", 0, 4),
    },
    "temmie": {
        "idle": ("undertale/temmie", "idle-talk", 0, 4),
        "walking": ("undertale/temmie", "walk-unused", 0, 4),
        "talking": ("undertale/temmie", "hoi-talk", 0, 4),
        "happy": ("undertale/temmie", "hoi", 0, 8),
        "surprised": ("undertale/temmie", "feeling-watched", 0, 1),
    },
    "monsterkid": {
        "idle": ("undertale/monsterkid", "row1-l4", 0, 4),
        "walking": ("undertale/monsterkid", "row02", 0, 8),
        "talking": ("undertale/monsterkid", "row04", 0, 4),
        "happy": ("undertale/monsterkid", "row03", 0, 4),
        "surprised": ("undertale/monsterkid", "row05", 0, 4),
        "goner": ("undertale/monsterkid", "row1-l424", 0, 2),
    },
    "annoyingdog": {
        "idle": ("undertale/annoyingdog", "row01", 0, 2),
        "walking": ("undertale/annoyingdog", "row21", 0, 4),
        "talking": ("undertale/annoyingdog", "row10", 0, 3),
        "happy": ("undertale/annoyingdog", "row03", 0, 3),
        "sleeping": ("undertale/annoyingdog", "row19", 0, 2),
    },
    "niko": {
        "idle": ("oneshot/niko", "row01", 0, 4),
        "walking": ("oneshot/niko", "row01", 4, 4),
        "talking": ("oneshot/niko", "row03", 0, 4),
        "happy": ("oneshot/niko", "row05", 0, 4),
        "sad": ("oneshot/niko", "row07", 0, 4),
        "surprised": ("oneshot/niko", "row09", 0, 4),
        "walkup": ("oneshot/niko", "row02", 0, 4),
    },
    "nikodt": {
        # Each row is an 8-frame cycle (repeated 3x in the sheet). Slice the
        # FULL first cycle for every family — half-cycle slices were what made
        # this character look "really messed" before.
        "idle": ("oneshot/niko-deltarune", "row01", 0, 1),
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
        "idle": ("deltarune/ralsei", "row03", 0, 4),
        "walking": ("deltarune/ralsei", "row02", 0, 4),
        "talking": ("deltarune/ralsei", "row05", 0, 4),
        "happy": ("deltarune/ralsei", "row04", 0, 4),
        "annoyed": ("deltarune/ralsei", "row06", 0, 4),
        "surprised": ("deltarune/ralsei", "row09", 0, 4),
        "sad": ("deltarune/ralsei", "row01", 0, 2),
    },
    "susie": {
        "idle": ("deltarune/susie", "row01", 0, 4),
        "walking": ("deltarune/susie", "row03", 0, 6),
        "talking": ("deltarune/susie", "row07", 0, 6),
        "happy": ("deltarune/susie", "row04", 0, 4),
        "annoyed": ("deltarune/susie", "row05", 0, 4),
        "surprised": ("deltarune/susie", "row08", 0, 4),
        "laugh": ("deltarune/susie", "row09", 0, 4),
    },
}

PACK_OF = {
    "sans": "undertale", "papyrus": "undertale", "toriel": "undertale", "undyne": "undertale",
    "frisk": "undertale", "flowey": "undertale", "temmie": "undertale", "monsterkid": "undertale",
    "annoyingdog": "undertale", "niko": "oneshot", "nikodt": "oneshot", "knight": "hollowknight", "hornet": "hollowknight",
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
    frames = []
    for f in picked:
        a = np.asarray(Image.open(str(f)).convert("RGBA"))
        al = a[:, :, 3] > 10
        ys, xs = np.where(al)
        if len(ys) == 0:
            continue
        frames.append(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return frames


def main():
    manifest = {}
    for char, families in MAPPINGS.items():
        pack = PACK_OF[char]
        out_dir = DST / pack / "Sprites"
        out_dir.mkdir(parents=True, exist_ok=True)
        # collect all families first
        all_frames = {}
        for family, spec in families.items():
            frames = load_family(char, family, spec)
            if frames:
                all_frames[family] = frames
        if not all_frames:
            print(f"{char}: NO FRAMES, skipped")
            continue
        # shared canvas = max bbox across all included frames
        maxw = max(f.shape[1] for frs in all_frames.values() for f in frs)
        maxh = max(f.shape[0] for frs in all_frames.values() for f in frs)
        char_man = {"canvas": [maxw, maxh], "families": {}}
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
