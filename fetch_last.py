import urllib.request, json, re, os

vid = 'KcajU321FKg'
SUBS_DIR = 'C:/Users/Mario/work/subs'

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
tracks = result.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])

cap_url = tracks[0]['baseUrl']
print(f'URL: {cap_url[:100]}...')
print(f'URL length: {len(cap_url)}')

# Try URL encoding the entire thing more carefully
encoded = urllib.request.quote(cap_url, safe='')
proxy_url = 'https://corsproxy.io/?' + encoded
print(f'Proxy URL length: {len(proxy_url)}')

try:
    req2 = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
    resp2 = urllib.request.urlopen(req2, timeout=30)
    xml = resp2.read().decode('utf-8')
    print(f'Got XML: {len(xml)} bytes')
    
    lines = []
    for m in re.finditer(r'<p t="(\d+)"[^>]*>(.*?)</p>', xml, re.DOTALL):
        t_ms = int(m.group(1))
        inner = m.group(2)
        segs = re.findall(r'<s[^>]*>([^<]*)</s>', inner)
        text = ''.join(segs).strip() if segs else re.sub(r'<[^>]+>', '', inner).strip()
        if text:
            lines.append(f'[{t_ms//60000:02d}:{(t_ms%60000)//1000:02d}] {text}')
    
    if lines:
        with open(f'{SUBS_DIR}/{vid}.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f'OK: {len(lines)} lines saved')
    else:
        print(f'Parsed 0 lines. XML sample: {xml[:300]}')
except Exception as e:
    print(f'Error: {e}')
    # Try with different encoding
    try:
        # Maybe the URL has special chars - try encoding differently
        proxy2 = 'https://corsproxy.io/?' + urllib.request.quote(cap_url, safe=':/?&=')
        req3 = urllib.request.Request(proxy2, headers={'User-Agent': 'Mozilla/5.0'})
        resp3 = urllib.request.urlopen(req3, timeout=30)
        xml2 = resp3.read().decode('utf-8')
        print(f'Alt encoding got: {len(xml2)} bytes')
        
        lines = []
        for m in re.finditer(r'<p t="(\d+)"[^>]*>(.*?)</p>', xml2, re.DOTALL):
            t_ms = int(m.group(1))
            inner = m.group(2)
            segs = re.findall(r'<s[^>]*>([^<]*)</s>', inner)
            text = ''.join(segs).strip() if segs else re.sub(r'<[^>]+>', '', inner).strip()
            if text:
                lines.append(f'[{t_ms//60000:02d}:{(t_ms%60000)//1000:02d}] {text}')
        
        if lines:
            with open(f'{SUBS_DIR}/{vid}.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f'OK (alt): {len(lines)} lines saved')
        else:
            print(f'Still 0 lines')
    except Exception as e2:
        print(f'Alt also failed: {e2}')
