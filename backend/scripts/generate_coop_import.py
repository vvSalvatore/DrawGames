import asyncio
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

import httpx

ROOT = Path(__file__).resolve().parent.parent
IMPORT_FILE = ROOT / "import_games.json"
FRONTEND_SEED = ROOT.parent / "frontend" / "src" / "data" / "seed.js"

SEARCH_TERMS = [
    "co-op",
    "coop",
    "co op",
    "multiplayer",
    "online multiplayer",
    "online co-op",
    "cooperative",
    "cooperative multiplayer",
    "co-op multiplayer",
    "online coop",
]
SOURCE_ORDER = ["fitgirl", "online-fix", "ankergames", "steamunlocked"]
PER_PAGE = 100
MAX_PAGES = 20
TARGET_GAMES = 1100

CATEGORY_MATCH = [
    "co-op",
    "online co-op",
    "multi-player",
    "online multi-player",
    "multiplayer",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
        appids.update(re.findall(r'steam_app_id":\s*"(\d+)"', text))
    return appids


def parse_search_ids(html_text):
    return re.findall(r'data-ds-appid="(\d+)"', html_text)


def normalize_category(text: str) -> str:
    return text.strip().lower()


def app_has_coop(categories):
    normalized = {normalize_category(c.get("description", "")) for c in (categories or [])}
    if not any(tag in normalized for tag in CATEGORY_MATCH):
        return False
    return True


def extract_year(release_date: str) -> str:
    if not release_date:
        return "—"
    m = re.search(r"(19|20)\d{2}", release_date)
    return m.group(0) if m else "—"


async def fetch_search_appids(client: httpx.AsyncClient, search_term: str, start: int):
    url = f"https://store.steampowered.com/search/results/?query={quote_plus(search_term)}&start={start}&count={PER_PAGE}"
    r = await client.get(url, timeout=25)
    if r.status_code != 200:
        return []
    return parse_search_ids(r.text)


async def fetch_app_details(client: httpx.AsyncClient, appid: str):
    r = await client.get(
        "https://store.steampowered.com/api/appdetails",
        params={"appids": appid, "l": "english", "cc": "us"},
        timeout=20,
    )
    if r.status_code != 200:
        return None
    data = r.json()
    entry = data.get(str(appid)) or data.get(int(appid))
    if not entry or not entry.get("success"):
        return None
    return entry.get("data")


async def main():
    existing_appids = load_existing_appids()
    print(f"Existing app ids in seed/import: {len(existing_appids)}")

    candidate_ids = []
    seen_ids = set(existing_appids)

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        for term in SEARCH_TERMS:
            if len(candidate_ids) >= TARGET_GAMES * 2:
                break
            for page in range(MAX_PAGES):
                start = page * PER_PAGE
                ids = await fetch_search_appids(client, term, start)
                for appid in ids:
                    if appid in seen_ids:
                        continue
                    candidate_ids.append(appid)
                    seen_ids.add(appid)
                print(f"term={term} page={page} found={len(ids)} total_candidates={len(candidate_ids)}")
                if len(candidate_ids) >= TARGET_GAMES * 2:
                    break

        new_games = []
        source_index = 0
        for appid in candidate_ids:
            if len(new_games) >= TARGET_GAMES:
                break
            details = await fetch_app_details(client, appid)
            if not details:
                continue
            if details.get("type") != "game":
                continue
            categories = details.get("categories") or []
            if not app_has_coop(categories):
                continue
            title = details.get("name")
            if not title:
                continue
            year = extract_year(details.get("release_date", {}).get("date", ""))
            source = SOURCE_ORDER[source_index % len(SOURCE_ORDER)]
            source_index += 1
            new_games.append(
                {
                    "title": title,
                    "year": year,
                    "size": "—",
                    "source": source,
                }
            )
            print(f"added {len(new_games)}: {title} ({appid}) source={source}")

    print(f"Writing {len(new_games)} games to {IMPORT_FILE}")
    IMPORT_FILE.write_text(json.dumps(new_games, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
