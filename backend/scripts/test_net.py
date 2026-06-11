import httpx
r = httpx.get('https://example.com', timeout=20)
print(r.status_code)
print(r.text[:80])
