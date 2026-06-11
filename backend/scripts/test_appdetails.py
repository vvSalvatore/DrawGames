import httpx

url = 'https://store.steampowered.com/api/appdetails'
params = {'appids': '739630', 'l': 'english', 'cc': 'us'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://store.steampowered.com/app/739630/',
    'Origin': 'https://store.steampowered.com',
    'Connection': 'keep-alive',
}
with httpx.Client(headers=headers, follow_redirects=True, timeout=20) as c:
    r = c.get(url, params=params)
    print('status', r.status_code)
    print(r.text[:1000])
