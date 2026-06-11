import httpx
url = 'https://steamspy.com/api.php?request=top100in2weeks'
print('url', url)
with httpx.Client(timeout=20) as client:
    r = client.get(url)
    print('status', r.status_code)
    print(r.text[:500])
