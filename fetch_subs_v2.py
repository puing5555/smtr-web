"""
Fetch YouTube subtitles via multiple fallback methods:
1. allorigins proxy for the YouTube page
2. Direct timedtext with different IPs via public proxies
3. Invidious instances
"""
import urllib.request, json, re, os, time, sys

SUBS_DIR = 'C:/Users/Mario/work/subs'
os.makedirs(SUBS_DIR, exist_ok=True)

ALL_IDS = [
    'x0TKvrIdIwI', '3BLhG-e7cJ4', 'brSsrpX92LM', 'GVibO0T0zWI',
    'irK0YCnox78', 'KcajU321FKg', 'I4Tt3tevuTU',
    'hxpOT8n_ICw', 'R6w3T3eUVIs', 'WWtau8xFUU4',
    'zdMneplXBvQ', '-US4r1E1kOQ', 'lXxz7WJj76Y',
    '6R1HiMUAQkM', 'RdAzQQJUvRU', '8-hYd-8eojE',
    'qYAiv0Kljas', 'XFHD_1M3Mxg', 'ldT75QwBB6g'
]

def parse_json3(sub_data):
    lines = []
    for ev in sub_data.get('events', []):
        segs = ev.get('segs', [])
        t_ms = ev.get('tStartMs', 0)
        text = ''.join(s.get('utf8', '') for s in segs).strip()
        if text and text != '\n':
            mins = t_ms // 60000
            secs = (t_ms % 60000) // 1000
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    return lines

def parse_xml(xml_text):
    """Parse XML subtitle format"""
    lines = []
    for m in re.finditer(r'<text start="([\d.]+)"[^>]*>(.*?)</text>', xml_text, re.DOTALL):
        t = float(m.group(1))
        text = m.group(2).strip()
        # decode HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
        if text:
            mins = int(t) // 60
            secs = int(t) % 60
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    return lines

def method_allorigins(vid):
    """Use allorigins.win to proxy YouTube page and extract caption URLs"""
    yt_url = f'https://www.youtube.com/watch?v={vid}'
    proxy_url = f'https://api.allorigins.win/raw?url={urllib.request.quote(yt_url, safe="")}'
    req = urllib.request.Request(proxy_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    resp = urllib.request.urlopen(req, timeout=30)
    html = resp.read().decode('utf-8')
    
    # Find player response
    match = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.+?\});\s*(?:var|</script>)', html, re.DOTALL)
    if not match:
        return None, "No player response in proxied HTML"
    
    player = json.loads(match.group(1))
    title = player.get('videoDetails', {}).get('title', '?')
    captions = player.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    if not captions:
        return title, "No captions"
    
    cap_url = captions[0]['baseUrl']
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
    
    # Download subs via allorigins too
    sub_proxy = f'https://api.allorigins.win/raw?url={urllib.request.quote(cap_url + "&fmt=json3", safe="")}'
    req2 = urllib.request.Request(sub_proxy, headers={'User-Agent': 'Mozilla/5.0'})
    resp2 = urllib.request.urlopen(req2, timeout=20)
    sub_data = json.loads(resp2.read())
    lines = parse_json3(sub_data)
    return title, lines if lines else "Empty subs"

def method_invidious(vid):
    """Try multiple Invidious instances"""
    instances = [
        'https://invidious.protokolla.fi',
        'https://inv.tux.pizza',
        'https://invidious.privacyredirect.com',
        'https://yewtu.be',
        'https://vid.puffyan.us',
    ]
    for inst in instances:
        try:
            # Get captions list
            url = f'{inst}/api/v1/captions/{vid}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            
            captions = data.get('captions', [])
            if not captions:
                continue
            
            # Find Korean
            cap_label = None
            for c in captions:
                if 'ko' in c.get('language_code', '') or 'Korean' in c.get('label', ''):
                    cap_label = c.get('label', '')
                    break
            if not cap_label and captions:
                cap_label = captions[0].get('label', '')
            
            if cap_label:
                sub_url = f'{inst}/api/v1/captions/{vid}?label={urllib.request.quote(cap_label)}'
                req2 = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
                resp2 = urllib.request.urlopen(req2, timeout=10)
                xml_text = resp2.read().decode('utf-8')
                lines = parse_xml(xml_text)
                if lines:
                    return f'via {inst}', lines
        except:
            continue
    return None, "All invidious instances failed"

def method_android_api(vid):
    """Android innertube API - sometimes avoids rate limits"""
    url = 'https://www.youtube.com/youtubei/v1/player'
    payload = {
        'videoId': vid,
        'context': {
            'client': {
                'clientName': 'ANDROID',
                'clientVersion': '19.09.37',
                'androidSdkVersion': 30,
                'hl': 'ko', 'gl': 'KR'
            }
        }
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip'
    })
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    
    title = result.get('videoDetails', {}).get('title', '?')
    captions = result.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    if not captions:
        return title, "No captions via Android API"
    
    cap_url = captions[0]['baseUrl']
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
    
    # Try downloading via allorigins proxy
    sub_proxy = f'https://api.allorigins.win/raw?url={urllib.request.quote(cap_url + "&fmt=json3", safe="")}'
    req2 = urllib.request.Request(sub_proxy, headers={'User-Agent': 'Mozilla/5.0'})
    resp2 = urllib.request.urlopen(req2, timeout=20)
    sub_data = json.loads(resp2.read())
    lines = parse_json3(sub_data)
    return title, lines if lines else "Empty subs"

def main():
    success = 0
    fail = 0
    
    for i, vid in enumerate(ALL_IDS):
        outfile = f'{SUBS_DIR}/{vid}.txt'
        if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
            print(f'[{i+1}/{len(ALL_IDS)}] {vid} - SKIP (already exists)', flush=True)
            success += 1
            continue
        
        print(f'[{i+1}/{len(ALL_IDS)}] {vid}...', flush=True)
        
        methods = [
            ('allorigins', method_allorigins),
            ('android+proxy', method_android_api),
            ('invidious', method_invidious),
        ]
        
        got_it = False
        for name, method in methods:
            try:
                title, result = method(vid)
                if isinstance(result, list) and len(result) > 10:
                    with open(outfile, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(result))
                    print(f'  OK ({name}): {len(result)} lines', flush=True)
                    success += 1
                    got_it = True
                    break
                else:
                    print(f'  {name}: {result}', flush=True)
            except Exception as e:
                err = str(e)[:80]
                print(f'  {name}: {err}', flush=True)
            time.sleep(1)
        
        if not got_it:
            fail += 1
        
        time.sleep(2)
    
    print(f'\n=== DONE: {success} OK, {fail} failed ===', flush=True)

if __name__ == '__main__':
    main()
