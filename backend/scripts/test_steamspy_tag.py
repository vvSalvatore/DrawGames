import httpx
for tag in ['Co-op','Multiplayer','Online Co-op','Action']:
    url = f'https://steamspy.com/api.php?request=tag&tag={tag}'
    print('tag', tag)
    with httpx.Client(timeout=20) as client:
        r = client.get(url)
        print('status', r.status_code)
        print(r.text[:300])
        print('---')
