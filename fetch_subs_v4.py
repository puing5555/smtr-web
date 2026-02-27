"""
Fetch YouTube subtitles via Android innertube API + corsproxy.io
"""
import urllib.request, json, re, os, time

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

def get_caption_url(vid):
    """Get caption URL via Android innertube API"""
    url = 'https://www.youtube.com/youtubei/v1/player'
    payload = json.dumps({
        'videoId': vid,
        'context': {'client': {'clientName': 'ANDROID', 'clientVersion': '19.09.37', 'androidSdkVersion': 30, 'hl': 'ko', 'gl': 'KR'}}
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip'
    })
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    title = result.get('videoDetails', {}).get('title', '?')
    captions = result.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    if not captions:
        return title, None
    # prefer ko
    cap_url = captions[0]['baseUrl']
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
    return title, cap_url

def fetch_via_proxy(cap_url):
    """Fetch subtitle XML via corsproxy.io"""
    proxy_url = 'https://corsproxy.io/?' + urllib.request.quote(cap_url, safe='')
    req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30)
    return resp.read().decode('utf-8')

def parse_timedtext_xml(xml_text):
    """Parse YouTube timedtext XML format (format 3 with <p> tags)"""
    lines = []
    # Format 3 uses <p t="ms" d="ms"> with <s> segments inside
    for m in re.finditer(r'<p t="(\d+)"[^>]*>(.*?)</p>', xml_text, re.DOTALL):
        t_ms = int(m.group(1))
        inner = m.group(2)
        # Extract text from <s> tags
        segs = re.findall(r'<s[^>]*>([^<]*)</s>', inner)
        if segs:
            text = ''.join(segs).strip()
        else:
            # fallback: just strip tags
            text = re.sub(r'<[^>]+>', '', inner).strip()
        if text:
            mins = t_ms // 60000
            secs = (t_ms % 60000) // 1000
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    
    # Also try format 1 with <text start="seconds">
    if not lines:
        for m in re.finditer(r'<text start="([\d.]+)"[^>]*>(.*?)</text>', xml_text, re.DOTALL):
            t = float(m.group(1))
            text = m.group(2).strip()
            text = re.sub(r'<[^>]+>', '', text)
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
            if text:
                mins = int(t) // 60
                secs = int(t) % 60
                lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    
    return lines

def main():
    success = 0
    fail = 0
    
    for i, vid in enumerate(ALL_IDS):
        outfile = f'{SUBS_DIR}/{vid}.txt'
        if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
            print(f'[{i+1}/{len(ALL_IDS)}] {vid} - SKIP (exists)', flush=True)
            success += 1
            continue
        
        print(f'[{i+1}/{len(ALL_IDS)}] {vid}...', end=' ', flush=True)
        
        try:
            title, cap_url = get_caption_url(vid)
            if not cap_url:
                print(f'NO CAPTIONS - {title}', flush=True)
                fail += 1
                time.sleep(2)
                continue
            
            xml = fetch_via_proxy(cap_url)
            lines = parse_timedtext_xml(xml)
            
            if len(lines) > 5:
                with open(outfile, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f'OK {len(lines)} lines - {title[:50]}', flush=True)
                success += 1
            else:
                print(f'TOO FEW ({len(lines)}) - {title[:50]}', flush=True)
                fail += 1
        except Exception as e:
            print(f'ERROR: {str(e)[:80]}', flush=True)
            fail += 1
        
        time.sleep(3)
    
    print(f'\n=== DONE: {success} OK, {fail} failed ===', flush=True)

if __name__ == '__main__':
    main()
