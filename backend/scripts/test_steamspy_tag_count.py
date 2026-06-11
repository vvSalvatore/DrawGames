import httpx
import json

tags = ['Online Co-op', 'Co-op', 'Multiplayer', 'Online Multiplayer']
headers = {'User-Agent': 'Mozilla/5.0'}
with httpx.Client(headers=headers, timeout=30) as client:
    for tag in tags:
        url = f'https://steamspy.com/api.php?request=tag&tag={tag}'
        r = client.get(url)
        data = json.loads(r.text)
        print(tag, r.status_code, len(data))
        sample = list(data.values())[:5]
        print(sample)
        print('---')
