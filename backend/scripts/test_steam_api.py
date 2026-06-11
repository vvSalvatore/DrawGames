import httpx

url = 'https://store.steampowered.com/api/storesearch/?term=co-op&cc=us&l=en'
print('Fetching', url)
with httpx.Client(headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}) as client:
    r = client.get(url, timeout=20)
    print('status', r.status_code)
    print(r.text[:500])
