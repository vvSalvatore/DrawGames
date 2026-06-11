import json
import re
from pathlib import Path
from urllib.parse import quote_plus

import httpx

ROOT = Path(__file__).resolve().parent.parent
IMPORT_FILE = ROOT / "import_games.json"
FRONTEND_SEED = ROOT.parent / "frontend" / "src" / "data" / "seed.js"
TAG = "Online Co-op"
TARGET_GAMES = 1200
SOURCES = ["fitgirl", "online-fix", "ankergames", "steamunlocked"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}


def load_existing_appids():
    appids = set()
    if IMPORT_FILE.exists():
        try:
            data = json.loads(IMPORT_FILE.read_text(encoding="utf-8"))
            for item in data:
                sid = item.get("steam_app_id")
                if sid:
                    appids.add(str(sid))
        except Exception:
            pass
    if FRONTEND_SEED.exists():
        text = FRONTEND_SEED.read_text(encoding="utf-8")
        appids.update(re.findall(r'steam_app_id"\s*:\s*"(\d+)"', text))
    return appids


def parse_steamspy_tag(data):
    if isinstance(data, dict):
        return [item for item in data.values() if isinstance(item, dict) and item.get("appid")]
    return []


def build_games(entries, existing_appids):
    games = []
    used_titles = set()
    source_index = 0
    for item in entries:
        appid = str(item.get("appid"))
        title = item.get("name")
        if not appid or not title:
            continue
        if appid in existing_appids:
            continue
        norm_title = title.strip().lower()
        if norm_title in used_titles:
            continue
        if title.lower().startswith("steam"):  # ignore non-game results
            continue
        if len(games) >= TARGET_GAMES:
            break
        games.append(
            {
                "steam_app_id": appid,
                "title": title,
                "year": "—",
                "size": "—",
                "source": SOURCES[source_index % len(SOURCES)],
            }
        )
        used_titles.add(norm_title)
        source_index += 1
    return games


def main():
    existing_appids = load_existing_appids()
    print(f"Existing steam_app_ids in seed/import: {len(existing_appids)}")

    url = f"https://steamspy.com/api.php?request=tag&tag={quote_plus(TAG)}"
    with httpx.Client(headers=HEADERS, timeout=30) as client:
        r = client.get(url)
        r.raise_for_status()
        data = r.json()

    entries = parse_steamspy_tag(data)
    entries_sorted = sorted(entries, key=lambda item: int(item.get("positive", 0) or 0), reverse=True)
    games = build_games(entries_sorted, existing_appids)

    print(f"Collected {len(games)} games from SteamSpy tag '{TAG}'")
    IMPORT_FILE.write_text(json.dumps(games, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(games)} games to {IMPORT_FILE}")


if __name__ == "__main__":
    main()
