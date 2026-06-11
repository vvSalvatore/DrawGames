import re
import httpx

url = 'https://store.steampowered.com/search/results/?query=co-op&start=0&count=100'
print('Fetching', url)
with httpx.Client(headers={'User-Agent': 'Mozilla/5.0'}) as c:
    r = c.get(url, timeout=20)
    print('status', r.status_code)
    ids = set(re.findall(r'data-ds-appid="(\d+)"', r.text))
    print('ids', len(ids))
    print(sorted(ids)[:20])
