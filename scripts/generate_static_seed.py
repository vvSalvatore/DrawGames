import re
import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = (root / "backend" / "server.py").read_text(encoding="utf-8")

for name in ("SOURCES", "CATALOG"):
    match = re.search(rf"{name}(?:\s*:\s*[^=]+)?\s*=\s*([\[\{{])", src)
    if not match:
        raise RuntimeError(f"Could not find {name} in server.py")
    start = match.start(1)
    open_char = src[start]
    close_char = "]" if open_char == "[" else "}"
    depth = 0
    i = start
    while i < len(src):
        if src[i] == open_char:
            depth += 1
        elif src[i] == close_char:
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    text = src[start:end]
    value = ast.literal_eval(text)
    globals()[name] = value

for g in CATALOG:
    if "steam_app_id" in g:
        g["id"] = f"g_{g['steam_app_id']}"
    else:
        cleaned = re.sub(r"[^0-9a-zA-Z]", "", g.get("title", "").lower())
        g["id"] = f"g_{cleaned}"
    if "status" not in g:
        g["status"] = "coming_soon" if g.get("is_coming_soon") else "cracked"
    if not g.get("image") and g.get("steam_app_id"):
        g["image"] = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{g['steam_app_id']}/header.jpg"
    g.setdefault("background", "")
    g.setdefault("description", "")
    g.setdefault("screenshots", [])
    g.setdefault("torrent_url", "")
    if "archive_password" not in g:
        g["archive_password"] = "online-fix.me" if g.get("source") == "online-fix" else None

out = root / "frontend" / "src" / "data" / "seed.js"
out.parent.mkdir(parents=True, exist_ok=True)
text = "export const GAMES = " + json.dumps(CATALOG, ensure_ascii=False, indent=2) + ";\n\n"
text += "export const SOURCES = " + json.dumps(SOURCES, ensure_ascii=False, indent=2) + ";\n"
out.write_text(text, encoding="utf-8")
print(f"Wrote {out}")
