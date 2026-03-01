"""Extract transcript using innertube - get params from page source"""
import sys, io, json, requests, re, time, random, os
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
    'Accept-Language': 'ko-KR,ko;q=0.9',
})

def extract_transcript(video_id):
    # Step 1: Load YouTube page
    url = f'https://www.youtube.com/watch?v={video_id}'
    resp = session.get(url)
    if resp.status_code != 200:
        return f'PAGE_{resp.status_code}', None
    
    html = resp.text
    
    # Step 2: Extract API key
    api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    api_key = api_key_match.group(1) if api_key_match else 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    
    # Step 3: Find transcript params from engagement panel
    # Look for the "Show transcript" button which contains the params
    params_match = re.search(r'"showEngagementPanelEndpoint":\s*\{[^}]*"panelIdentifier"\s*:\s*"engagement-panel-searchable-transcript"[^}]*\}', html)
    
    # Alternative: find serialized params for transcript
    # The params are in the engagement panel trigger
    params_match2 = re.search(r'"params":"([^"]+)"[^}]*?"engagement-panel-searchable-transcript"', html)
    if not params_match2:
        params_match2 = re.search(r'"engagement-panel-searchable-transcript"[^}]*?"params":"([^"]+)"', html)
    
    if not params_match2:
        # Try broader search - look for transcript params near the panel identifier
        # Search in ytInitialData
        init_data_match = re.search(r'var ytInitialData\s*=\s*(\{.+?\});\s*</script>', html)
        if init_data_match:
            try:
                init_data = json.loads(init_data_match.group(1))
                panels = init_data.get('engagementPanels', [])
                for panel in panels:
                    pid = panel.get('engagementPanelSectionListRenderer', {}).get('panelIdentifier', '')
                    if pid == 'engagement-panel-searchable-transcript':
                        # Found transcript panel - get continuation
                        content = panel.get('engagementPanelSectionListRenderer', {}).get('content', {})
                        continuation_items = content.get('continuationItemRenderer', {})
                        if not continuation_items:
                            # Try deeper
                            sr = content.get('transcriptSearchPanelRenderer', {})
                            body = sr.get('body', {}).get('transcriptSegmentListRenderer', {})
                            initial_segs = body.get('initialSegments', [])
                            if initial_segs:
                                segments = []
                                for seg in initial_segs:
                                    r = seg.get('transcriptSegmentRenderer', {})
                                    runs = r.get('snippet', {}).get('runs', [])
                                    text = ''.join(run.get('text', '') for run in runs).strip()
                                    start_ms = int(r.get('startMs', '0'))
                                    end_ms = int(r.get('endMs', '0'))
                                    if text:
                                        segments.append({
                                            'start': start_ms / 1000.0,
                                            'duration': (end_ms - start_ms) / 1000.0,
                                            'text': text
                                        })
                                if segments:
                                    return 'OK', segments
                        
                        # Try continuation
                        cont = json.dumps(panel, ensure_ascii=False)
                        cont_match = re.search(r'"continuation":"([^"]+)"', cont)
                        if cont_match:
                            continuation = cont_match.group(1)
                            print(f"  Found continuation token")
                            
                            # Use continuation endpoint
                            cont_url = f'https://www.youtube.com/youtubei/v1/get_transcript?key={api_key}'
                            cont_payload = {
                                "context": {
                                    "client": {
                                        "clientName": "WEB",
                                        "clientVersion": "2.20240101.00.00",
                                        "hl": "ko"
                                    }
                                },
                                "params": continuation
                            }
                            resp2 = session.post(cont_url, json=cont_payload, headers={'Content-Type': 'application/json'})
                            print(f"  Transcript API status: {resp2.status_code}")
                            if resp2.status_code == 200:
                                data = resp2.json()
                                # Parse the response
                                actions = data.get('actions', [])
                                for action in actions:
                                    panel_content = action.get('updateEngagementPanelAction', {}).get('content', {})
                                    sr = panel_content.get('transcriptRenderer', {}).get('content', {}).get('transcriptSearchPanelRenderer', {})
                                    body = sr.get('body', {}).get('transcriptSegmentListRenderer', {})
                                    initial_segs = body.get('initialSegments', [])
                                    
                                    segments = []
                                    for seg in initial_segs:
                                        r = seg.get('transcriptSegmentRenderer', {})
                                        runs = r.get('snippet', {}).get('runs', [])
                                        text = ''.join(run.get('text', '') for run in runs).strip()
                                        start_ms = int(r.get('startMs', '0'))
                                        end_ms = int(r.get('endMs', '0'))
                                        if text:
                                            segments.append({
                                                'start': start_ms / 1000.0,
                                                'duration': (end_ms - start_ms) / 1000.0,
                                                'text': text
                                            })
                                    if segments:
                                        return 'OK', segments
                                
                                print(f"  Response keys: {list(data.keys())}")
                                return 'NO_SEGMENTS', None
                            else:
                                return f'API_{resp2.status_code}', None
            except json.JSONDecodeError:
                pass
    
    return 'NO_PARAMS', None

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
    status, segments = extract_transcript(vid)
    
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
        time.sleep(random.randint(3, 8))

print(f"\n=== 결과 ===")
ok = sum(1 for _,_,_,s in results if s in ('ok', 'skipped'))
print(f"성공: {ok}/{len(results)}")
for vid, prefix, count, status in results:
    emoji = '✅' if status in ('ok','skipped') else '❌'
    print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")
