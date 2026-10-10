#!/usr/bin/env python3
"""
Sprite Labeler — a local web app for visually labeling every animation.

Serves every extracted sprite row as an animated GIF preview.
You name each row (idle, walk-left, talk, attack, ...), optionally group
rows into multi-row animations, and export a labels.json that
process_pack_sprites.py reads to wire the app's families.

Usage:
    python3 Scripts/sprite-labeler/labeler.py
    open http://localhost:8477
"""
import http.server
import json
import pathlib
import io
import urllib.parse
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
EXTRACTED = ROOT / "build-assets" / "extracted"
LABELS_FILE = ROOT / "build-assets" / "labels.json"
PORT = 8477


def character_list():
    """All characters with extracted sprite rows, with pack info."""
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
                        "label": row_dir.name,
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


def load_labels():
    if LABELS_FILE.exists():
        return json.load(open(LABELS_FILE))
    return {}


def save_labels(labels):
    json.dump(labels, open(LABELS_FILE, "w"), indent=1)


def make_gif(paths, duration_ms=140, max_size=180):
    """Render a row's frames as an animated GIF for the browser."""
    frames = []
    max_w = max_h = 0
    for p in paths:
        img = Image.open(str(EXTRACTED / p)).convert("RGBA")
        # scale to fit a preview box
        scale = min(max_size / img.width, max_size / img.height, 4.0)
        tw = max(1, int(img.width * scale))
        th = max(1, int(img.height * scale))
        img = img.resize((tw, th), Image.NEAREST)
        frames.append(img)
        max_w = max(max_w, tw)
        max_h = max(max_h, th)
    if not frames:
        return b""
    composed = []
    bg_color = (40, 40, 48, 255)
    for fr in frames:
        canvas = Image.new("RGBA", (max_w, max_h), bg_color)
        canvas.paste(fr, ((max_w - fr.width) // 2, (max_h - fr.height) // 2), fr)
        composed.append(canvas.convert("RGB"))
    buf = io.BytesIO()
    composed[0].save(buf, format="GIF", save_all=True,
                     append_images=composed[1:],
                     duration=duration_ms, loop=0)
    return buf.getvalue()


HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Sprite Labeler</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
h1 { font-size: 18px; margin-bottom: 16px; color: #fac726; }
h2 { font-size: 14px; margin: 20px 0 8px; color: #8be9fd; }
.sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: 220px; background: #16162a; padding: 20px; overflow-y: auto; border-right: 1px solid #333; }
.sidebar button { display: block; width: 100%; margin: 4px 0; padding: 8px 12px; background: #222244; color: #eee; border: 1px solid #444; border-radius: 6px; cursor: pointer; text-align: left; font-size: 13px; }
.sidebar button:hover { background: #333366; }
.sidebar button.active { background: #fac726; color: #000; font-weight: bold; }
.main { margin-left: 240px; }
.char-header { margin-bottom: 20px; }
.char-header h1 { font-size: 22px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.card { background: #222244; border: 1px solid #333; border-radius: 10px; padding: 12px; }
.card img { width: 100%; image-rendering: pixelated; border-radius: 6px; background: #28283e; }
.card .info { margin-top: 8px; font-size: 11px; color: #999; }
.card input[type=text] { width: 100%; margin-top: 6px; padding: 6px 8px; background: #1a1a2e; color: #fac726; border: 1px solid #444; border-radius: 4px; font-size: 13px; font-family: monospace; }
.card .labeled { border-color: #fac726; }
.controls { margin: 12px 0; padding: 12px; background: #222244; border-radius: 8px; }
.controls button { padding: 8px 16px; margin-right: 8px; background: #fac726; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
.controls .msg { display: inline-block; margin-left: 12px; color: #8be9fd; font-size: 13px; }
.legend { font-size: 11px; color: #888; margin-top: 8px; }
</style>
</head>
<body>
<div class="sidebar" id="sidebar"></div>
<div class="main">
  <div class="char-header">
    <h1 id="charTitle">Sprite Labeler</h1>
    <div class="controls">
      <button onclick="saveLabels()">Save Labels</button>
      <button onclick="exportJson()">Export for App</button>
      <span class="msg" id="status"></span>
    </div>
    <div class="legend">
      Type a name in each box (idle, walk-left, walk-right, talk, attack, hurt, ...).
      Yellow border = labeled. Click Save to persist. Click Export to generate the JSON
      the sprite processor reads.
    </div>
  </div>
  <div class="grid" id="grid"></div>
</div>
<script>
let chars = {};
let currentChar = '';
let labels = {};

async function load() {
  const resp = await fetch('/api/characters');
  chars = await resp.json();
  const labelResp = await fetch('/api/labels');
  labels = await labelResp.json();
  const sidebar = document.getElementById('sidebar');
  sidebar.innerHTML = '';
  for (const [key, info] of Object.entries(chars)) {
    const btn = document.createElement('button');
    btn.textContent = info.character + ' (' + info.pack + ')';
    btn.onclick = () => selectChar(key);
    btn.dataset.key = key;
    sidebar.appendChild(btn);
  }
  const keys = Object.keys(chars);
  if (keys.length > 0) selectChar(keys[0]);
}

function selectChar(key) {
  currentChar = key;
  document.querySelectorAll('.sidebar button').forEach(b => b.classList.toggle('active', b.dataset.key === key));
  const info = chars[key];
  document.getElementById('charTitle').textContent = info.character + ' — ' + info.pack;
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  for (const row of info.rows) {
    const card = document.createElement('div');
    card.className = 'card';
    const labelKey = key + '/' + row.id;
    const existing = labels[labelKey] || '';
    if (existing) card.classList.add('labeled');
    card.innerHTML = `
      <img src="/gif/${encodeURIComponent(row.frames.join('|'))}" loading="lazy">
      <div class="info">${row.id} — ${row.frame_count} frames</div>
      <input type="text" value="${existing}" placeholder="name this animation..."
             oninput="setLabel('${labelKey}', this.value, this.parentElement)"
             onchange="setLabel('${labelKey}', this.value, this.parentElement)">
    `;
    grid.appendChild(card);
  }
}

function setLabel(key, value, card) {
  if (value.trim()) {
    labels[key] = value.trim();
    card.classList.add('labeled');
  } else {
    delete labels[key];
    card.classList.remove('labeled');
  }
}

async function saveLabels() {
  const resp = await fetch('/api/labels', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(labels)
  });
  const result = await resp.json();
  document.getElementById('status').textContent = 'Saved ' + result.count + ' labels ✓';
}

async function exportJson() {
  const resp = await fetch('/api/export');
  const result = await resp.json();
  document.getElementById('status').textContent = 'Exported to ' + result.path;
}

load();
</script>
</body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == "/api/characters":
            data = json.dumps(character_list()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/api/labels":
            data = json.dumps(load_labels()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/api/export":
            labels = load_labels()
            export = {}
            for key, name in labels.items():
                parts = key.split("/")
                pack = parts[0]
                char = parts[1]
                row = "/".join(parts[2:])
                export.setdefault(char, {})[name] = row
            export_path = ROOT / "build-assets" / "labels_export.json"
            json.dump(export, open(export_path, "w"), indent=1)
            data = json.dumps({"path": str(export_path), "characters": len(export)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        elif self.path.startswith("/gif/"):
            paths_str = urllib.parse.unquote(self.path[5:])
            paths = paths_str.split("|")
            gif_data = make_gif(paths)
            if gif_data:
                self.send_response(200)
                self.send_header("Content-Type", "image/gif")
                self.send_header("Cache-Control", "max-age=3600")
                self.end_headers()
                self.wfile.write(gif_data)
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/labels":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            save_labels(data)
            response = json.dumps({"count": len(data)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet


if __name__ == "__main__":
    server = http.server.HTTPServer(("localhost", PORT), Handler)
    print(f"Sprite Labeler running at http://localhost:{PORT}")
    print(f"  characters: {len(character_list())}")
    print(f"  extracted dir: {EXTRACTED}")
    print(f"  labels file: {LABELS_FILE}")
    print("  Ctrl+C to stop")
    server.serve_forever()
