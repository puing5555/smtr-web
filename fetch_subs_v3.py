"""
Fetch YouTube subtitles using third-party services that proxy through their own servers.
This bypasses our IP's 429 rate limit.
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

def method_tactiq(vid):
    """Use Tactiq's free transcript API"""
    url = f'https://tactiq-apps-prod.tactiq.io/transcript?videoUrl=https://www.youtube.com/watch?v={vid}&langCode=ko'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Origin': 'https://tactiq.io',
        'Referer': 'https://tactiq.io/'
    })
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    
    captions = data.get('captions', [])
    if not captions:
        return "No captions from tactiq"
    
    lines = []
    for c in captions:
        t = c.get('start', 0)
        text = c.get('text', '').strip()
        if text:
            mins = int(t) // 60
            secs = int(t) % 60
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    return lines

def method_kome(vid):
    """Use Kome.ai transcript API"""
    url = 'https://kome.ai/api/tools/youtube-transcript'
    payload = json.dumps({
        'video_id': vid,
        'format': True
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Origin': 'https://kome.ai',
        'Referer': 'https://kome.ai/tools/youtube-transcript-generator'
    })
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    
    transcript = data.get('transcript', '')
    if not transcript:
        return "No transcript from kome"
    
    lines = transcript.split('\n')
    return [l.strip() for l in lines if l.strip()]

def method_searchapi(vid):
    """Use youtubetranscript.com API"""
    url = f'http://youtubetranscript.com/?server_vid2={vid}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
    })
    resp = urllib.request.urlopen(req, timeout=20)
    xml = resp.read().decode('utf-8')
    
    lines = []
    for m in re.finditer(r'<text start="([\d.]+)"[^>]*>(.*?)</text>', xml, re.DOTALL):
        t = float(m.group(1))
        text = m.group(2).strip()
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
        if text:
            mins = int(t) // 60
            secs = int(t) % 60
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    
    if not lines:
        return "No transcript from youtubetranscript.com"
    return lines

def method_rapidapi_alt(vid):
    """Use a free transcript extraction service"""
    # Try savesubs
    url = f'https://savesubs.com/action/extract?url=https://www.youtube.com/watch?v={vid}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    })
    resp = urllib.request.urlopen(req, timeout=20)
    data = json.loads(resp.read())
    
    formats = data.get('formats', data.get('response', {}).get('formats', []))
    if not formats:
        return "No formats from savesubs"
    
    # Find Korean or first available
    dl_url = None
    for f in formats:
        lang = f.get('language', {}).get('code', '')
        if 'ko' in lang:
            dl_url = f.get('url', f.get('urls', {}).get('srt', ''))
            break
    if not dl_url and formats:
        dl_url = formats[0].get('url', formats[0].get('urls', {}).get('srt', ''))
    
    if dl_url:
        req2 = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'})
        resp2 = urllib.request.urlopen(req2, timeout=15)
        srt_text = resp2.read().decode('utf-8')
        # Parse SRT
        lines = []
        for block in srt_text.split('\n\n'):
            parts = block.strip().split('\n')
            if len(parts) >= 3:
                time_line = parts[1]
                text = ' '.join(parts[2:]).strip()
                m = re.match(r'(\d{2}):(\d{2}):(\d{2})', time_line)
                if m and text:
                    mins = int(m.group(1)) * 60 + int(m.group(2))
                    secs = int(m.group(3))
                    lines.append(f'[{mins:02d}:{secs:02d}] {text}')
        if lines:
            return lines
    
    return "No download URL from savesubs"

def main():
    success = 0
    fail = 0
    
    for i, vid in enumerate(ALL_IDS):
        outfile = f'{SUBS_DIR}/{vid}.txt'
        if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
            print(f'[{i+1}/{len(ALL_IDS)}] {vid} - SKIP (exists)', flush=True)
            success += 1
            continue
        
        print(f'[{i+1}/{len(ALL_IDS)}] {vid}...', flush=True)
        
        methods = [
            ('youtubetranscript.com', method_searchapi),
            ('tactiq', method_tactiq),
            ('kome', method_kome),
            ('savesubs', method_rapidapi_alt),
        ]
        
        got_it = False
        for name, method in methods:
            try:
                result = method(vid)
                if isinstance(result, list) and len(result) > 10:
                    with open(outfile, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(result))
                    print(f'  OK ({name}): {len(result)} lines', flush=True)
                    success += 1
                    got_it = True
                    break
                else:
                    msg = result if isinstance(result, str) else f'{len(result)} lines (too few)'
                    print(f'  {name}: {msg}', flush=True)
            except Exception as e:
                print(f'  {name}: {str(e)[:80]}', flush=True)
            time.sleep(1)
        
        if not got_it:
            fail += 1
        time.sleep(1)
    
    print(f'\n=== DONE: {success} OK, {fail} failed ===', flush=True)

if __name__ == '__main__':
    main()
