import requests, re, json, time, random

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
})

vid = '1NUkBQ9MQf8'
print(f'Test: {vid}')

# Visit YouTube main to get cookies
r0 = session.get('https://www.youtube.com/', timeout=10)
print(f'Main page: {r0.status_code}, cookies: {len(session.cookies)}')
time.sleep(2)

# Video page
r = session.get(f'https://www.youtube.com/watch?v={vid}', timeout=15)
print(f'Video page: {r.status_code}')

match = re.search(r'"captionTracks":\s*(\[.*?\])', r.text)
if match:
    tracks = json.loads(match.group(1).replace('\\u0026', '&'))
    print(f'Tracks: {len(tracks)}')
    track = next((t for t in tracks if t.get('languageCode') == 'ko'), tracks[0] if tracks else None)
    if track:
        print(f'Lang: {track.get("languageCode")}')
        time.sleep(random.uniform(3, 6))
        caption_url = track['baseUrl'] + '&fmt=json3'
        cr = session.get(caption_url, timeout=15)
        print(f'Caption status: {cr.status_code}')
        if cr.status_code == 200:
            data = cr.json()
            events = data.get('events', [])
            segs = []
            for evt in events:
                ss = evt.get('segs', [])
                text = ''.join(s.get('utf8', '') for s in ss).strip()
                if text and text != '\n':
                    segs.append(text)
            print(f'SUCCESS: {len(segs)} segments')
            print(f'First: {segs[0][:100] if segs else "empty"}')
        else:
            print(f'Response: {cr.text[:200]}')
else:
    # Check if consent page
    if 'CONSENT' in r.text or 'consent' in r.url:
        print('Got consent page - need to accept cookies')
    print('No caption tracks found')
    # Check for sign-in wall
    if 'Sign in' in r.text[:5000]:
        print('Sign-in wall detected')
