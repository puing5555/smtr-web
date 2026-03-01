"""Use innertube get_transcript endpoint (different from timedtext)"""
import sys, io, json, requests, base64, struct, time, random, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/subs'

VIDEOS = [
    ('booread', '1NUkBQ9MQf8'),
    ('booread', 'IjDhjDgC4Ao'),
    ('booread', '1iuRuDfMLUE'),
    ('booread', 'f519DUfXkzQ'),
    ('booread', 'jXME1wXZDRU'),
    ('dalrant', 'DCpdPagMLbQ'),
    ('hyoseok', 'IjYr0FrINis'),
    ('hyoseok', 'Rdw1judfd5E'),
    ('hyoseok', 'Y-7UUKocmC0'),
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'X-YouTube-Client-Name': '1',
    'X-YouTube-Client-Version': '2.20240101.00.00',
})

def build_transcript_params(video_id):
    """Build the protobuf-like params for get_transcript"""
    # This is the engagement panel params for transcript
    # Format from reverse engineering YouTube
    import base64
    # Simple approach: encode video_id in the expected protobuf format
    # Field 1 (string) = video_id, nested in field 1
    inner = b'\n' + bytes([len(video_id)]) + video_id.encode()
    outer = b'\n' + bytes([len(inner)]) + inner
    return base64.b64encode(outer).decode()

def get_transcript_via_page(video_id):
    """Get transcript by scraping the page and using engagement panels"""
    url = f'https://www.youtube.com/watch?v={video_id}'
    resp = session.get(url)
    
    if resp.status_code != 200:
        return f'PAGE_{resp.status_code}', None
    
    # Find the serializedShareEntity or transcript params
    # Look for engagementPanels with transcript
    text = resp.text
    
    # Find transcript panel params
    import re
    # Look for "Show transcript" button params
    match = re.search(r'"serializedShareEntity":"([^"]+)"', text)
    
    # Alternative: find the transcript engagement panel
    match2 = re.search(r'"showEngagementPanelEndpoint":\{"panelIdentifier":"engagement-panel-searchable-transcript"', text)
    if match2:
        print("  Found transcript panel reference")
    
    # Try to find continuation token for transcript
    match3 = re.search(r'"continuation":"([^"]+)"[^}]*transcript', text)
    if match3:
        print(f"  Found transcript continuation")
    
    # Actually, let's try the get_transcript endpoint with proper params
    params = build_transcript_params(video_id)
    
    transcript_url = 'https://www.youtube.com/youtubei/v1/get_transcript'
    payload = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20240101.00.00",
                "hl": "ko",
                "gl": "KR"
            }
        },
        "params": params
    }
    
    resp2 = session.post(transcript_url, json=payload)
    print(f"  get_transcript status: {resp2.status_code}")
    
    if resp2.status_code == 200:
        data = resp2.json()
        # Extract transcript segments
        actions = data.get('actions', [])
        if actions:
            panel = actions[0].get('updateEngagementPanelAction', {}).get('content', {})
            transcript_renderer = panel.get('transcriptRenderer', {}).get('content', {}).get('transcriptSearchPanelRenderer', {})
            body = transcript_renderer.get('body', {}).get('transcriptSegmentListRenderer', {})
            segments_raw = body.get('initialSegments', [])
            
            segments = []
            for seg in segments_raw:
                renderer = seg.get('transcriptSegmentRenderer', {})
                text_runs = renderer.get('snippet', {}).get('runs', [])
                text = ''.join(r.get('text', '') for r in text_runs).strip()
                start_ms = int(renderer.get('startMs', '0'))
                end_ms = int(renderer.get('endMs', '0'))
                
                if text:
                    segments.append({
                        'start': start_ms / 1000.0,
                        'duration': (end_ms - start_ms) / 1000.0,
                        'text': text
                    })
            
            if segments:
                return 'OK', segments
            else:
                print(f"  No segments in response. Keys: {list(data.keys())}")
                if 'actions' in data:
                    print(f"  Actions: {json.dumps(data['actions'][0], ensure_ascii=False)[:300]}")
                return 'EMPTY', None
        else:
            print(f"  Response keys: {list(data.keys())}")
            print(f"  First 300: {json.dumps(data, ensure_ascii=False)[:300]}")
            return 'NO_ACTIONS', None
    else:
        print(f"  Error: {resp2.text[:200]}")
        return f'ERROR_{resp2.status_code}', None

results = []
for i, (prefix, vid) in enumerate(VIDEOS):
    out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
    ft_path = f'{SUBS_DIR}/{prefix}_{vid}_fulltext.txt'
    
    if os.path.exists(out_path):
        try:
            d = json.load(open(out_path, 'r', encoding='utf-8'))
            segs = d.get('segments', d.get('subtitles', []))
            if segs and len(segs) > 10:
                print(f"SKIP {vid} ({prefix}): {len(segs)} segs")
                results.append((vid, prefix, len(segs), 'skipped'))
                continue
        except:
            pass
    
    print(f"[{i+1}/9] {vid} ({prefix}):")
    status, segments = get_transcript_via_page(vid)
    
    if status == 'OK' and segments:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'video_id': vid, 'channel': prefix, 'subtitles': segments}, f, ensure_ascii=False, indent=2)
        fulltext = '\n'.join(s['text'] for s in segments)
        with open(ft_path, 'w', encoding='utf-8') as f:
            f.write(fulltext)
        print(f"  OK: {len(segments)} segments")
        results.append((vid, prefix, len(segments), 'ok'))
    else:
        print(f"  FAIL: {status}")
        results.append((vid, prefix, 0, status.lower()))
    
    if i < len(VIDEOS) - 1:
        delay = random.randint(3, 8)
        time.sleep(delay)

print(f"\n=== 결과 ===")
ok = sum(1 for _,_,_,s in results if s in ('ok', 'skipped'))
print(f"성공: {ok}/{len(results)}")
for vid, prefix, count, status in results:
    emoji = '✅' if status in ('ok','skipped') else '❌'
    print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")
