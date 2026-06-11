import httpx

url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}
with httpx.Client(headers=headers, timeout=20) as client:
    r = client.get(url)
    print('status', r.status_code)
    print(r.text[:500])
