import httpx

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://store.steampowered.com/',
    'DNT': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

urls = [
    'https://store.steampowered.com/search/results/?query=co-op&start=0&count=100',
    'https://store.steampowered.com/api/storesearch/?term=co-op&cc=us&l=en',
]

with httpx.Client(headers=headers, follow_redirects=True, timeout=25) as client:
    for url in urls:
        r = client.get(url)
        print('URL:', url)
        print('Status:', r.status_code)
        text = r.text[:1000].replace('\n', ' ')
        print('Head:', text[:500])
        print('---')
