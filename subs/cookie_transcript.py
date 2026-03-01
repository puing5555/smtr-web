"""
YouTube 자막 추출 - Chrome 쿠키 없이 직접 innertube API 사용
YouTube의 내부 API (InnerTube)를 통해 자막 추출
"""
import requests, json, re, time, sys

def get_transcript_innertube(video_id):
    """InnerTube API로 자막 URL 추출 후 다운로드"""
    # Step 1: 영상 페이지에서 자막 URL 추출
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    
    # Get video page
    url = f'https://www.youtube.com/watch?v={video_id}'
    r = session.get(url, timeout=15)
    print(f'  Page status: {r.status_code}')
    
    # Extract captionTracks from page source
    match = re.search(r'"captionTracks":\s*(\[.*?\])', r.text)
    if not match:
        print('  No captionTracks found')
        return None
    
    tracks = json.loads(match.group(1).replace('\\u0026', '&'))
    print(f'  Found {len(tracks)} caption tracks')
    
    # Find Korean
    ko_track = next((t for t in tracks if t.get('languageCode') == 'ko'), None)
    track = ko_track or tracks[0]
    lang = track.get('languageCode', '?')
    print(f'  Using track: {lang}')
    
    # Step 2: Fetch caption content
    caption_url = track.get('baseUrl', '')
    if not caption_url:
        return None
    
    # Get as JSON
    caption_url += '&fmt=json3'
    cr = session.get(caption_url, timeout=15)
    print(f'  Caption fetch: {cr.status_code}')
    
    if cr.status_code != 200:
        return None
    
    data = cr.json()
    events = data.get('events', [])
    segments = []
    for evt in events:
        segs = evt.get('segs', [])
        text = ''.join(s.get('utf8', '') for s in segs).strip()
        if text and text != '\n':
            segments.append({
                'start': evt.get('tStartMs', 0) / 1000.0,
                'duration': evt.get('dDurationMs', 0) / 1000.0,
                'text': text
            })
    
    return segments, lang

# Test
vid = sys.argv[1] if len(sys.argv) > 1 else 'fDZnPoK5lyc'
print(f'Testing video: {vid}')
result = get_transcript_innertube(vid)
if result:
    segments, lang = result
    print(f'SUCCESS: {len(segments)} segments (lang={lang})')
    print(f'First: {segments[0]["text"][:100]}')
else:
    print('FAILED')
