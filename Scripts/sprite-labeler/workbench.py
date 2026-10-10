#!/usr/bin/env python3
"""
Sprite Workbench v2 — label animations, select frames from sheets, view extractions.

Three tabs:
  1. Sheets    — original sprite sheets with clickable sprite boxes, save selections as named animations
  2. Extracted — the pre-extracted animation rows (the ones the app currently uses), rename them
  3. Saved     — all saved animations + broken flags + export

Usage:
    python3 Scripts/sprite-labeler/workbench.py
    open http://localhost:8478
"""
import http.server
import json
import pathlib
import io
import urllib.parse
import base64
from PIL import Image
import numpy as np
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
EXTRACTED = ROOT / "build-assets" / "extracted"
SHEETS = pathlib.Path.home() / "Downloads" / "sprite sheets"
WORKBENCH_FILE = ROOT / "build-assets" / "workbench.json"
PORT = 8478

PURPLE_DARK = np.array([138, 90, 157])
PURPLE_LIGHT = np.array([195, 134, 255])


def detect_sprites(sheet_path):
    """Auto-detect individual sprite bounding boxes on a sprite sheet.
    Handles both purple-convention (Undertale) and solid-background sheets."""
    arr = np.asarray(Image.open(str(sheet_path)).convert("RGBA"))
    h, w = arr.shape[:2]
    alpha = arr[:, :, 3] > 30

    def close_to(target, tol=45):
        return (np.abs(arr[:, :, :3].astype(int) - target[None, None, :]).max(axis=2) <= tol) & alpha

    def flood_bg(mask):
        lbl, _ = ndimage.label(mask)
        border = set(np.unique(lbl[0, :])) | set(np.unique(lbl[-1, :]))
        border |= set(np.unique(lbl[:, 0])) | set(np.unique(lbl[:, -1]))
        border.discard(0)
        return np.isin(lbl, list(border)) if border else mask

    # Try purple first (Undertale convention)
    purple = close_to(PURPLE_DARK) | close_to(PURPLE_LIGHT)
    content = None
    if purple.sum() > w * h * 0.15:
        bg = flood_bg(purple)
        candidate = alpha & ~bg
        if candidate.sum() > 100 and candidate.sum() < w * h * 0.95:
            content = candidate

    if content is None:
        # Fallback: dominant color as bg
        op = arr[alpha][:, :3]
        if len(op) == 0:
            return []
        from collections import Counter
        bg_color = np.array(Counter(map(tuple, op)).most_common(1)[0][0])
        bg_mask = close_to(bg_color, 40)
        bg_flood = flood_bg(bg_mask | ~alpha)
        content = alpha & ~bg_flood

        # Panel-style sheets (battle Sans): the bg is dark teal, but sprites
        # sit on CYAN PANELS that are also "content" after the first pass.
        # Detect and remove large cyan/teal regions that span most of the width
        # — those are panels, not sprites.
        if content.sum() > w * h * 0.3:
            from collections import Counter as _C
            colors = _C(map(tuple, arr[content][:, :3]))
            # find cyan-ish or teal-ish colors that make up large regions
            content_arr = np.zeros((h, w), bool)
            content_arr[np.where(content)] = True
            for color, cnt in colors.most_common(8):
                if cnt < 1000:
                    continue
                cr, cg, cb = color
                # cyan-ish: g and b much higher than r
                if cg > cr + 40 and cb > cr + 40:
                    mask = close_to(np.array([cr, cg, cb]), 30)
                    # if this color makes up a big chunk of "content", it's a panel fill
                    if (mask & content).sum() > content.sum() * 0.15:
                        content = content & ~mask

    # Connected components on content
    lbl, n = ndimage.label(content)
    sprites = []
    for i, sl in enumerate(ndimage.find_objects(lbl)):
        if sl is None:
            continue
        y0, y1 = sl[0].start, sl[0].stop
        x0, x1 = sl[1].start, sl[1].stop
        px = int((lbl[sl] == i + 1).sum())
        cw, ch = x1 - x0, y1 - y0
        if px < 20 or cw < 6 or ch < 6:
            continue
        if ch <= 14 and cw > ch * 3:
            continue
        if cw > w * 0.55 or ch > h * 0.45:
            continue
        # Skip giant blobs (unresolved background)
        if px > w * h * 0.3:
            continue
        sprites.append({"x": int(x0), "y": int(y0), "w": int(cw), "h": int(ch)})
    return sprites


def load_workbench():
    if WORKBENCH_FILE.exists():
        return json.load(open(WORKBENCH_FILE))
    return {"animations": {}, "labels": {}, "broken": {}}


def save_workbench(data):
    json.dump(data, open(WORKBENCH_FILE, "w"), indent=1)


def sheet_list():
    sheets = []
    for f in sorted(SHEETS.glob("*.png")):
        try:
            img = Image.open(str(f))
            sheets.append({"file": f.name, "w": img.width, "h": img.height, "dir": str(SHEETS)})
        except Exception:
            pass
    # Add the Hollow Knight atlas files (extracted from zips)
    hk_dir = pathlib.Path.home() / "Downloads"
    for pattern in ["The Knight-*.zip", "NPCs-*.zip", "Bosses-*.zip", "Enemies*.zip"]:
        pass  # These are zips, not PNGs — skip
    # Instead, add the already-extracted atlas PNGs if they exist
    hk_extracted = ROOT / "build-assets" / "extracted" / "hollowknight"
    if hk_extracted.exists():
        # The Knight atlas is already unpacked somewhere — find it
        import zipfile, tempfile
        knight_zip = hk_dir / "The Knight-20261003T153026Z-1-001.zip"
        if knight_zip.exists():
            # List the atlas PNGs inside without extracting
            with zipfile.ZipFile(str(knight_zip), "r") as zf:
                for name in zf.namelist():
                    if name.endswith(".png") and "atlas" in name.lower():
                        sheets.append({"file": name, "w": 4096, "h": 4096, "dir": "zip:" + str(knight_zip)})
    return sheets


def extracted_chars():
    chars = {}
    for pack_dir in sorted(EXTRACTED.iterdir()):
        if not pack_dir.is_dir():
            continue
        for char_dir in sorted(pack_dir.iterdir()):
            if not char_dir.is_dir():
                continue
            rows = []
            for row_dir in sorted(char_dir.iterdir()):
                if not row_dir.is_dir():
                    continue
                files = sorted(row_dir.glob("*.png"))
                if files:
                    rows.append({
                        "id": row_dir.name,
                        "frame_count": len(files),
                        "frames": [str(f.relative_to(EXTRACTED)) for f in files],
                    })
            if rows:
                chars[f"{pack_dir.name}/{char_dir.name}"] = {
                    "pack": pack_dir.name,
                    "character": char_dir.name,
                    "rows": rows,
                }
    return chars


HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Sprite Workbench</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; }
.layout { display: flex; height: 100vh; }
.sidebar { width: 230px; background: #16162a; border-right: 1px solid #333; padding: 12px; overflow-y: auto; flex-shrink: 0; }
.sidebar h3 { font-size: 12px; color: #fac726; margin: 14px 0 6px; text-transform: uppercase; letter-spacing: 1px; }
.sidebar button { display: block; width: 100%; margin: 2px 0; padding: 6px 8px; background: #222244; color: #ccc; border: 1px solid #3a3a5a; border-radius: 5px; cursor: pointer; text-align: left; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sidebar button:hover { background: #333366; }
.sidebar button.active { background: #fac726; color: #000; font-weight: bold; }
.main { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.tabs { display: flex; background: #16162a; border-bottom: 1px solid #333; flex-shrink: 0; }
.tabs button { flex: 1; padding: 10px; background: none; border: none; color: #777; font-size: 13px; cursor: pointer; border-bottom: 2px solid transparent; }
.tabs button.active { color: #fac726; border-bottom: 2px solid #fac726; }
.content { flex: 1; overflow: auto; padding: 16px; }
.controls { padding: 10px; background: #222244; border-radius: 8px; margin-bottom: 14px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.controls input[type=text] { padding: 6px 10px; background: #1a1a2e; color: #fac726; border: 1px solid #444; border-radius: 5px; font-size: 13px; width: 220px; }
.controls button { padding: 6px 14px; background: #fac726; color: #000; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 12px; }
.controls .msg { color: #8be9fd; font-size: 12px; }
.controls select { padding: 6px 8px; background: #1a1a2e; color: #eee; border: 1px solid #444; border-radius: 5px; font-size: 12px; }

.sheet-container { position: relative; display: inline-block; max-width: 100%; }
.sheet-container img { image-rendering: pixelated; max-width: 100%; display: block; border: 1px solid #444; border-radius: 4px; }
.sprite-box { position: absolute; border: 1px solid rgba(139, 233, 253, 0.4); cursor: pointer; }
.sprite-box:hover { border-color: #8be9fd; background: rgba(139, 233, 253, 0.1); }
.sprite-box.selected { border: 2px solid #fac726; background: rgba(250, 199, 38, 0.2); }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }
.card { background: #222244; border: 1px solid #333; border-radius: 8px; padding: 8px; }
.card img { width: 100%; image-rendering: pixelated; border-radius: 4px; background: #28283e; height: 100px; object-fit: contain; }
.card .meta { color: #888; font-size: 10px; margin-top: 4px; }
.card input[type=text] { width: 100%; margin-top: 4px; padding: 4px 6px; background: #1a1a2e; color: #fac726; border: 1px solid #444; border-radius: 3px; font-size: 11px; font-family: monospace; }
.card.broken { border-color: #ff4444; }
.card.broken::after { content: "⚠ BROKEN"; color: #ff4444; font-size: 10px; font-weight: bold; display: block; margin-top: 4px; }
.card button { margin-top: 4px; margin-right: 3px; padding: 3px 6px; font-size: 10px; border: none; border-radius: 3px; cursor: pointer; }
.btn-broken { background: #ff4444; color: #fff; }
.btn-del { background: #666; color: #fff; }
.char-section { grid-column: span all; margin-top: 16px; margin-bottom: 4px; color: #8be9fd; font-size: 14px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 4px; }
.status-bar { padding: 8px 12px; background: #16162a; border-top: 1px solid #333; font-size: 11px; color: #888; flex-shrink: 0; }
</style>
</head>
<body>
<div class="layout">
<div class="sidebar" id="sidebar"></div>
<div class="main">
  <div class="tabs">
    <button id="tab-sheet" onclick="showTab('sheet')">Sheet Selector</button>
    <button id="tab-extracted" onclick="showTab('extracted')">Extracted Rows</button>
    <button id="tab-saved" onclick="showTab('saved')">Saved Animations</button>
  </div>
  <div class="content" id="content"></div>
  <div class="status-bar" id="status"></div>
</div>
</div>
<script>
let S = {
  sheets: [], sheetIdx: -1,
  sprites: [], selected: new Set(), selectedList: [],
  extracted: {}, charKeys: [], charIdx: -1,
  anims: {}, labels: {}, broken: {},
  tab: 'sheet',
};

const esc = s => s.replace(/&/g,'&').replace(/</g,'<').replace(/>/g,'>').replace(/"/g,'"').replace(/'/g,'&#39;');
const setStatus = msg => document.getElementById('status').textContent = msg;

async function init() {
  const [sheetsR, wbR, charsR] = await Promise.all([
    fetch('/api/sheets'), fetch('/api/workbench'), fetch('/api/chars')
  ]);
  S.sheets = await sheetsR.json();
  const wb = await wbR.json();
  S.anims = wb.anims || {}; S.labels = wb.labels || {}; S.broken = wb.broken || {};
  S.extracted = await charsR.json();
  S.charKeys = Object.keys(S.extracted);
  buildSidebar();
  showTab('sheet');
}

function buildSidebar() {
  const sb = document.getElementById('sidebar');
  let h = '<h3>Sprite Sheets</h3>';
  S.sheets.forEach((s, i) => {
    const short = s.file.split(' - ').pop().replace('.png','');
    h += `<button data-idx="${i}" onclick="loadSheet(${i})" title="${esc(s.file)}">${esc(short)}</button>`;
  });
  h += '<h3>Extracted Characters</h3>';
  S.charKeys.forEach((k, i) => {
    const info = S.extracted[k];
    h += `<button data-ckey="${esc(k)}" onclick="showExtracted(${i})">${esc(info.character)} (${info.rows.length} rows)</button>`;
  });
  sb.innerHTML = h;
}

// ============ SHEET TAB ============
async function loadSheet(idx) {
  S.sheetIdx = idx;
  S.selected = new Set();
  S.selectedList = [];
  const s = S.sheets[idx];
  setStatus('Detecting sprites on ' + s.file + '...');
  const resp = await fetch('/api/detect?idx=' + idx);
  const data = await resp.json();
  S.sprites = data.sprites || [];
  document.querySelectorAll('.sidebar button').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.sidebar button[data-idx="${idx}"]`);
  if (btn) btn.classList.add('active');
  renderSheet();
  setStatus(S.sprites.length + ' sprites detected — click boxes to select, then name and save');
}

function autoCharacter(filename) {
  // "PC _ Computer - Undertale - Non-Playable Characters - Sans.png" → "Sans"
  // "PC _ Computer - Deltarune - Playable Characters - Kris (Chapter 1 + 2).png" → "Kris"
  // "Custom _ Edited - Undertale Customs - Sans - Sans (Deltarune Battle...).png" → "Sans"
  let name = filename.replace('.png', '');
  const parts = name.split(' - ');
  let last = parts[parts.length - 1].trim();
  if (last.includes('(')) last = last.split('(')[0].trim();
  return last.toLowerCase().replace(/\s+/g, '');
}

function renderSheet() {
  const c = document.getElementById('content');
  if (S.sheetIdx < 0) {
    c.innerHTML = '<p style="color:#888;padding:40px">← Select a sprite sheet from the sidebar</p>';
    return;
  }
  const s = S.sheets[S.sheetIdx];
  const autoChar = autoCharacter(s.file);
  const imgUrl = '/sheet-img/' + S.sheetIdx;
  c.innerHTML = `
    <div class="controls">
      <span id="autoChar" style="color:#8be9fd;font-size:13px;font-weight:bold;padding:4px 8px;background:#1a1a2e;border-radius:4px;border:1px solid #444">${autoChar}</span>
      <input type="text" id="animName" placeholder="animation name" style="width:180px">
      <button onclick="saveAnim()">Save Selected → Animation</button>
      <button onclick="S.selected = new Set(S.sprites.map((_,i)=>i)); S.selectedList = S.sprites.map((_,i)=>i); renderSheet()">Select All</button>
      <button onclick="S.selected.clear(); S.selectedList = []; renderSheet()">Clear</button>
      <span class="msg" id="sheetMsg"></span>
    </div>
    <div class="sheet-container">
      <img src="${imgUrl}" id="sheetImg" onload="onImgLoad()">
      <div id="boxes" style="position:absolute;top:0;left:0;width:100%;height:100%"></div>
    </div>`;
}

function onImgLoad() {
  const img = document.getElementById('sheetImg');
  const boxes = document.getElementById('boxes');
  boxes.style.width = img.offsetWidth + 'px';
  boxes.style.height = img.offsetHeight + 'px';
  const sx = img.offsetWidth / img.naturalWidth;
  const sy = img.offsetHeight / img.naturalHeight;
  let h = '';
  S.sprites.forEach((sp, i) => {
    const sel = S.selected.has(i) ? ' selected' : '';
    h += `<div class="sprite-box${sel}" style="left:${sp.x*sx}px;top:${sp.y*sy}px;width:${sp.w*sx}px;height:${sp.h*sy}px" onclick="toggleSel(${i})"></div>`;
  });
  boxes.innerHTML = h;
  updateSheetMsg();
}

function toggleSel(i) {
  if (S.selected.has(i)) {
    S.selected.delete(i);
    S.selectedList = S.selectedList.filter(x => x !== i);
  } else {
    S.selected.add(i);
    S.selectedList.push(i);  // click order = frame order
  }
  const boxes = document.getElementById('boxes');
  if (boxes) {
    const box = boxes.children[i];
    if (box) box.classList.toggle('selected', S.selected.has(i));
  }
  updateSheetMsg();
}

function updateSheetMsg() {
  const el = document.getElementById('sheetMsg');
  if (el) el.textContent = S.selected.size + ' selected';
}

async function saveAnim() {
  const name = document.getElementById('animName').value.trim();
  if (!name) { setStatus('Type a name first!'); return; }
  if (S.selectedList.length === 0) { setStatus('Select some sprites first!'); return; }
  // CRITICAL: use the user's CLICK ORDER as the frame order —
  // the first sprite they clicked is frame 1, second is frame 2, etc.
  const selection = S.selectedList.map(i => S.sprites[i]);
  const resp = await fetch('/api/save-anim', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ sheetIdx: S.sheetIdx, name, selection })
  });
  const result = await resp.json();
  S.anims[result.key] = result.anim;
  setStatus(`Saved "${name}" (${selection.length} frames from ${S.sheets[S.sheetIdx].file})`);
  document.getElementById('animName').value = '';
}

// ============ EXTRACTED TAB ============
function showExtracted(idx) {
  S.charIdx = idx;
  S.tab = 'extracted';
  document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-extracted').classList.add('active');
  const key = S.charKeys[idx];
  const info = S.extracted[key];
  let h = `<p style="color:#888;margin-bottom:12px;font-size:13px">${esc(info.character)} — ${info.rows.length} extracted animation rows. Rename any that are wrong.</p>`;
  h += '<div class="grid">';
  for (const row of info.rows) {
    const labelKey = key + '/' + row.id;
    const existing = S.labels[labelKey] || '';
    const gifUrl = '/row-gif?frames=' + encodeURIComponent(row.frames.join('|'));
    h += `<div class="card ${S.broken[labelKey] ? 'broken' : ''}">
      <img src="${gifUrl}" loading="lazy">
      <div class="meta">${esc(row.id)} — ${row.frame_count} frames</div>
      <input type="text" value="${esc(existing)}" placeholder="rename..."
             onchange="renameRow('${esc(labelKey)}', this.value)">
    </div>`;
  }
  h += '</div>';
  document.getElementById('content').innerHTML = h;
  setStatus('Viewing ' + info.character);
}

function renameRow(key, value) {
  if (value.trim()) S.labels[key] = value.trim();
  else delete S.labels[key];
  fetch('/api/workbench', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ anims: S.anims, labels: S.labels, broken: S.broken })
  });
  setStatus('Renamed to "' + value + '"');
}

// ============ SAVED TAB ============
function showTab(tab) {
  S.tab = tab;
  document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  if (tab === 'sheet') renderSheet();
  else if (tab === 'extracted') {
    if (S.charIdx >= 0) showExtracted(S.charIdx);
    else document.getElementById('content').innerHTML = '<p style="color:#888;padding:40px">← Select a character from the sidebar</p>';
  }
  else if (tab === 'saved') renderSaved();
}

function renderSaved() {
  const keys = Object.keys(S.anims);
  if (keys.length === 0) {
    document.getElementById('content').innerHTML = '<p style="color:#888;padding:40px">No saved animations yet. Use the Sheet Selector tab to create some.</p>';
    return;
  }
  let h = '<div class="controls"><button onclick="exportJson()">Export for App</button><span class="msg" id="savedMsg"></span></div>';
  h += '<div class="grid">';
  for (const key of keys) {
    const a = S.anims[key];
    const gifUrl = '/anim-gif?key=' + encodeURIComponent(key);
    h += `<div class="card ${S.broken[key] ? 'broken' : ''}">
      <img src="${gifUrl}" loading="lazy">
      <div style="color:#fac726;font-size:12px;font-weight:bold;margin-top:4px">${esc(a.name)}</div>
      <div class="meta">${esc(a.character ? a.character + ' — ' : '')}${a.selection.length} frames — ${esc(a.sheetShort || '')}</div>
      <button class="btn-broken" onclick="toggleBroken('${esc(key)}')">${S.broken[key] ? 'Unmark' : 'Broken'}</button>
      <button class="btn-del" onclick="deleteAnim('${esc(key)}')">Delete</button>
    </div>`;
  }
  h += '</div>';
  document.getElementById('content').innerHTML = h;
}

async function toggleBroken(key) {
  if (S.broken[key]) delete S.broken[key];
  else S.broken[key] = true;
  await fetch('/api/workbench', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ anims: S.anims, labels: S.labels, broken: S.broken })
  });
  renderSaved();
}

async function deleteAnim(key) {
  delete S.anims[key];
  delete S.broken[key];
  await fetch('/api/workbench', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ anims: S.anims, labels: S.labels, broken: S.broken })
  });
  renderSaved();
}

async function exportJson() {
  const resp = await fetch('/api/export');
  const result = await resp.json();
  const el = document.getElementById('savedMsg');
  if (el) el.textContent = 'Exported to ' + result.path;
}

init();
</script>
</body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/":
            self._html(HTML)
        elif path == "/api/sheets":
            self._json(sheet_list())
        elif path == "/api/workbench":
            self._json(load_workbench())
        elif path == "/api/chars":
            self._json(extracted_chars())
        elif path == "/api/detect":
            idx = int(qs.get("idx", ["-1"])[0])
            if 0 <= idx < len(sheet_list()):
                s = sheet_list()[idx]
                if s.get("dir", "").startswith("zip:"):
                    import zipfile
                    zip_path = pathlib.Path(s["dir"][4:])
                    with zipfile.ZipFile(str(zip_path), "r") as zf:
                        png_data = zf.read(s["file"])
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        tmp.write(png_data)
                        tmp_path = pathlib.Path(tmp.name)
                    sprites = detect_sprites(tmp_path)
                    tmp_path.unlink()
                else:
                    sprites = detect_sprites(SHEETS / s["file"])
                self._json({"sprites": sprites})
            else:
                self._json({"sprites": []})
        elif path.startswith("/sheet-img/"):
            idx = int(path.split("/")[-1])
            if 0 <= idx < len(sheet_list()):
                s = sheet_list()[idx]
                if s.get("dir", "").startswith("zip:"):
                    import zipfile
                    zip_path = pathlib.Path(s["dir"][4:])
                    with zipfile.ZipFile(str(zip_path), "r") as zf:
                        png_data = zf.read(s["file"])
                    img = Image.open(io.BytesIO(png_data)).convert("RGBA")
                    arr = np.asarray(img)
                    alpha = arr[:, :, 3] > 30
                    dark = np.zeros_like(arr)
                    dark[:, :, :3] = 28
                    dark[:, :, 3] = 255
                    spr = alpha
                    dark[spr] = arr[spr]
                    buf = io.BytesIO()
                    Image.fromarray(dark).save(buf, format="PNG")
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    self.wfile.write(buf.getvalue())
                    return
                filepath = SHEETS / s["file"]
                if filepath.exists():
                    # Serve with purple background stripped → transparent,
                    # composited over a dark checkerboard-friendly dark bg
                    img = Image.open(str(filepath)).convert("RGBA")
                    arr = np.asarray(img)
                    alpha = arr[:, :, 3] > 30

                    def close_to(target, tol=45):
                        return (np.abs(arr[:, :, :3].astype(int) - target[None, None, :]).max(axis=2) <= tol) & alpha

                    purple = close_to(PURPLE_DARK) | close_to(PURPLE_LIGHT)
                    # Flood from edges to find background purple only
                    lbl, _ = ndimage.label(purple)
                    border = set(np.unique(lbl[0, :])) | set(np.unique(lbl[-1, :]))
                    border |= set(np.unique(lbl[:, 0])) | set(np.unique(lbl[:, -1]))
                    border.discard(0)
                    bg = np.isin(lbl, list(border)) if border else purple
                    # Make bg transparent
                    out = arr.copy()
                    out[bg, 3] = 0
                    # Composite over dark grey so sprites are visible
                    dark = np.zeros_like(out)
                    dark[:, :, :3] = 28  # dark grey
                    dark[:, :, 3] = 255
                    # where sprite pixels exist, use the sprite
                    spr = out[:, :, 3] > 0
                    dark[spr] = out[spr]
                    buf = io.BytesIO()
                    Image.fromarray(dark).save(buf, format="PNG")
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Cache-Control", "max-age=60")
                    self.end_headers()
                    self.wfile.write(buf.getvalue())
                else:
                    self.send_response(404)
                    self.end_headers()
        elif path == "/row-gif":
            frames_str = qs.get("frames", [""])[0]
            paths = frames_str.split("|")
            gif = self._make_gif(paths)
            if gif:
                self._raw(gif, "image/gif")
            else:
                self.send_response(404)
                self.end_headers()
        elif path == "/anim-gif":
            key = qs.get("key", [""])[0]
            wb = load_workbench()
            anim = wb.get("anims", {}).get(key)
            if anim:
                gif = self._anim_gif(anim)
                if gif:
                    self._raw(gif, "image/gif")
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        elif path == "/api/export":
            self._export()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/api/workbench":
            save_workbench(body)
            self._json({"ok": True})
        elif self.path == "/api/save-anim":
            idx = body.get("sheetIdx", -1)
            name = body.get("name", "")
            selection = body.get("selection", [])
            character = body.get("character", "")
            if 0 <= idx < len(sheet_list()):
                s = sheet_list()[idx]
                sheet_file = s["file"]
                sheet_dir = s.get("dir", str(SHEETS))
                # Always derive character from the sheet filename server-side
                # — the JS autoCharacter may not have fired
                if not character:
                    parts = sheet_file.replace(".png", "").split(" - ")
                    character = parts[-1].strip()
                    if "(" in character:
                        character = character.split("(")[0].strip()
                    character = character.lower().replace(" ", "")
                key = f"{character}/{name}" if character else f"{idx}/{name}"
                short = sheet_file.split(" - ")[-1].replace(".png", "") if " - " in sheet_file else sheet_file.replace(".png", "")
                wb = load_workbench()
                wb.setdefault("anims", {})[key] = {
                    "name": name,
                    "character": character,
                    "sheetIdx": idx,
                    "sheet": sheet_file,
                    "sheetDir": sheet_dir,
                    "sheetShort": short,
                    "selection": selection,
                }
                save_workbench(wb)
                # AUTO-EXPORT: the export file updates on every save
                export = {}
                for k, a in wb.get("anims", {}).items():
                    char = a.get("character", "")
                    if not char:
                        # derive from sheet filename
                        sf = a.get("sheet", "")
                        parts = sf.replace(".png", "").split(" - ")
                        char = parts[-1].strip()
                        if "(" in char:
                            char = char.split("(")[0].strip()
                        char = char.lower().replace(" ", "")
                    export.setdefault(char, {})[a["name"]] = {
                        "frames": a["selection"],
                        "sheet": a["sheet"],
                    }
                for lk, name in wb.get("labels", {}).items():
                    parts = lk.split("/")
                    pack, char, row = parts[0], parts[1], "/".join(parts[2:])
                    export.setdefault(char, {}).setdefault("_row_labels", {})[row] = name
                export_path = ROOT / "build-assets" / "workbench_export.json"
                json.dump(export, open(export_path, "w"), indent=1)
                self._json({"key": key, "anim": wb["anims"][key], "exported": str(export_path)})
            else:
                self._json({"error": "bad sheet index"})
        else:
            self.send_response(404)
            self.end_headers()

    def _export(self):
        wb = load_workbench()
        export = {}
        for key, anim in wb.get("anims", {}).items():
            sheet_short = anim.get("sheetShort", "")
            export.setdefault(sheet_short, {})[anim["name"]] = {
                "frames": anim["selection"],
                "sheet": anim["sheet"],
            }
        for labelKey, name in wb.get("labels", {}).items():
            parts = labelKey.split("/")
            pack, char, row = parts[0], parts[1], "/".join(parts[2:])
            export.setdefault(char, {}).setdefault("_row_labels", {})[row] = name
        export_path = ROOT / "build-assets" / "workbench_export.json"
        json.dump(export, open(export_path, "w"), indent=1)
        self._json({"path": str(export_path), "sheets": len(export)})

    def _make_gif(self, paths):
        frames = []
        for p in paths:
            try:
                img = Image.open(str(EXTRACTED / p)).convert("RGBA")
            except Exception:
                continue
            scale = min(100 / img.width, 100 / img.height, 4.0)
            img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.NEAREST)
            frames.append(img)
        if not frames:
            return None
        return self._compose_gif(frames)

    def _anim_gif(self, anim):
        sheet_path = SHEETS / anim["sheet"]
        if not sheet_path.exists():
            return None
        img = Image.open(str(sheet_path)).convert("RGBA")
        frames = []
        for sel in anim["selection"]:
            crop = img.crop((sel["x"], sel["y"], sel["x"] + sel["w"], sel["y"] + sel["h"]))
            scale = min(100 / crop.width, 100 / crop.height, 4.0)
            crop = crop.resize((max(1, int(crop.width * scale)), max(1, int(crop.height * scale))), Image.NEAREST)
            frames.append(crop)
        if not frames:
            return None
        return self._compose_gif(frames)

    def _compose_gif(self, frames):
        max_w = max(f.width for f in frames)
        max_h = max(f.height for f in frames)
        composed = []
        for fr in frames:
            canvas = Image.new("RGBA", (max_w, max_h), (40, 40, 48, 255))
            canvas.paste(fr, ((max_w - fr.width) // 2, (max_h - fr.height) // 2), fr)
            composed.append(canvas.convert("RGB"))
        buf = io.BytesIO()
        composed[0].save(buf, format="GIF", save_all=True, append_images=composed[1:], duration=140, loop=0)
        return buf.getvalue()

    def _html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _raw(self, data, mime):
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = http.server.HTTPServer(("localhost", PORT), Handler)
    print(f"Sprite Workbench v2 at http://localhost:{PORT}")
    print(f"  {len(sheet_list())} sheets, {len(extracted_chars())} extracted characters")
    server.serve_forever()
