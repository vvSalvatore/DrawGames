import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parent.parent
IMPORT_FILE = ROOT / "import_games.json"

client = MongoClient("mongodb://localhost:27017")
db = client["drawgames"]

if not IMPORT_FILE.exists():
    raise SystemExit(f"Missing {IMPORT_FILE}")

games = json.loads(IMPORT_FILE.read_text(encoding="utf-8"))
print(f"Loaded {len(games)} games from {IMPORT_FILE}")
added = 0
for idx, g in enumerate(games, start=1):
    title = g.get("title", "").strip()
    sid = str(g.get("steam_app_id")) if g.get("steam_app_id") else None
    if not title or not sid:
        continue
    if db.games.find_one({"steam_app_id": sid}):
        continue
    if db.games.find_one({"title": re.compile(f"^{re.escape(title)}$", re.I)}):
        continue
    source = g.get("source", "fitgirl")
    base = {
        "id": f"g_{sid}",
        "steam_app_id": sid,
        "title": title,
        "description": "",
        "image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg",
        "background": "",
        "screenshots": [],
        "size": g.get("size", "—"),
        "year": g.get("year", "—"),
        "genres": ["Co-op", "Online"],
        "source": source,
        "torrent_url": "",
        "status": "cracked",
        "is_coop": True,
        "is_multiplayer": True,
        "coop_count": 4,
        "is_coming_soon": False,
        "release_date": None,
        "nsfw": False,
        "archive_password": "online-fix.me" if source == "online-fix" else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.games.insert_one(base)
    added += 1
    if idx % 100 == 0:
        print(f"Processed {idx}/{len(games)} (added {added})")

print(f"Inserted {added} new games")
print(f"Final count: {db.games.count_documents({})}")
