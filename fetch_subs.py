import urllib.request, json, re, os, time, sys

def fetch_captions_from_html(vid):
    """Get captions URL from YouTube page HTML, then download subtitles"""
    url = f'https://www.youtube.com/watch?v={vid}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Cookie': ''
    })
    resp = urllib.request.urlopen(req, timeout=20)
    html = resp.read().decode('utf-8')
    
    # Extract ytInitialPlayerResponse
    match = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.+?\});\s*(?:var|</script>)', html, re.DOTALL)
    if not match:
        return None, "No ytInitialPlayerResponse"
    
    player_data = json.loads(match.group(1))
    title = player_data.get('videoDetails', {}).get('title', '?')
    
    captions = player_data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    if not captions:
        return title, "No captions available"
    
    # Find Korean captions
    cap_url = None
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
            break
    if not cap_url:
        cap_url = captions[0]['baseUrl']
    
    # Download subtitle as json3
    sub_url = cap_url + '&fmt=json3'
    req2 = urllib.request.Request(sub_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://www.youtube.com/watch?v={vid}'
    })
    resp2 = urllib.request.urlopen(req2, timeout=15)
    sub_data = json.loads(resp2.read())
    
    lines = []
    for ev in sub_data.get('events', []):
        segs = ev.get('segs', [])
        t_ms = ev.get('tStartMs', 0)
        text = ''.join(s.get('utf8', '') for s in segs).strip()
        if text and text != '\n':
            mins = t_ms // 60000
            secs = (t_ms % 60000) // 1000
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    
    return title, lines


def fetch_via_innertube(vid):
    """Fallback: use innertube player API"""
    url = 'https://www.youtube.com/youtubei/v1/player'
    payload = {
        'videoId': vid,
        'context': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20260101.00.00',
                'hl': 'ko',
                'gl': 'KR'
            }
        }
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    
    title = result.get('videoDetails', {}).get('title', '?')
    captions = result.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    if not captions:
        return title, "No captions"
    
    cap_url = captions[0]['baseUrl']
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
    
    sub_url = cap_url + '&fmt=json3'
    req2 = urllib.request.Request(sub_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    resp2 = urllib.request.urlopen(req2, timeout=15)
    sub_data = json.loads(resp2.read())
    
    lines = []
    for ev in sub_data.get('events', []):
        segs = ev.get('segs', [])
        t_ms = ev.get('tStartMs', 0)
        text = ''.join(s.get('utf8', '') for s in segs).strip()
        if text and text != '\n':
            mins = t_ms // 60000
            secs = (t_ms % 60000) // 1000
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    
    return title, lines


def main():
    all_ids = [
        'x0TKvrIdIwI', '3BLhG-e7cJ4', 'brSsrpX92LM', 'GVibO0T0zWI',
        'irK0YCnox78', 'KcajU321FKg', 'I4Tt3tevuTU',
        'hxpOT8n_ICw', 'R6w3T3eUVIs', 'WWtau8xFUU4',
        'zdMneplXBvQ', '-US4r1E1kOQ', 'lXxz7WJj76Y',
        '6R1HiMUAQkM', 'RdAzQQJUvRU', '8-hYd-8eojE',
        'qYAiv0Kljas', 'XFHD_1M3Mxg', 'ldT75QwBB6g'
    ]
    
    os.makedirs('C:/Users/Mario/work/subs', exist_ok=True)
    
    success = 0
    fail = 0
    
    for i, vid in enumerate(all_ids):
        print(f'\n[{i+1}/{len(all_ids)}] {vid}...', flush=True)
        
        # Try HTML method first
        try:
            title, result = fetch_captions_from_html(vid)
            if isinstance(result, list) and len(result) > 0:
                with open(f'C:/Users/Mario/work/subs/{vid}.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(result))
                print(f'  OK (HTML): {title[:50]} - {len(result)} lines', flush=True)
                success += 1
                time.sleep(3)
                continue
            else:
                print(f'  HTML method: {result}', flush=True)
        except Exception as e:
            print(f'  HTML error: {e}', flush=True)
        
        time.sleep(2)
        
        # Try innertube fallback
        try:
            title, result = fetch_via_innertube(vid)
            if isinstance(result, list) and len(result) > 0:
                with open(f'C:/Users/Mario/work/subs/{vid}.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(result))
                print(f'  OK (innertube): {title[:50]} - {len(result)} lines', flush=True)
                success += 1
                time.sleep(3)
                continue
            else:
                print(f'  Innertube: {result}', flush=True)
        except Exception as e:
            print(f'  Innertube error: {e}', flush=True)
        
        fail += 1
        time.sleep(3)
    
    print(f'\n=== Done: {success} OK, {fail} failed ===', flush=True)


if __name__ == '__main__':
    main()
