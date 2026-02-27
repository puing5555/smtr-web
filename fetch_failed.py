import urllib.request, json, re, os, time

SUBS_DIR = 'C:/Users/Mario/work/subs'
failed = ['KcajU321FKg', 'WWtau8xFUU4', 'lXxz7WJj76Y', '8-hYd-8eojE', 'XFHD_1M3Mxg']

def get_caption_url(vid):
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
    cap_url = captions[0]['baseUrl']
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
    return title, cap_url

def parse_xml(xml_text):
    lines = []
    for m in re.finditer(r'<p t="(\d+)"[^>]*>(.*?)</p>', xml_text, re.DOTALL):
        t_ms = int(m.group(1))
        inner = m.group(2)
        segs = re.findall(r'<s[^>]*>([^<]*)</s>', inner)
        text = ''.join(segs).strip() if segs else re.sub(r'<[^>]+>', '', inner).strip()
        if text:
            lines.append(f'[{t_ms//60000:02d}:{(t_ms%60000)//1000:02d}] {text}')
    return lines

for vid in failed:
    print(f'{vid}...', end=' ', flush=True)
    try:
        title, cap_url = get_caption_url(vid)
        if not cap_url:
            print('NO CAPS', flush=True)
            continue
        # Use codetabs proxy (different from corsproxy)
        proxies = [
            'https://api.codetabs.com/v1/proxy?quest=',
            'https://corsproxy.io/?',
        ]
        ok = False
        for p in proxies:
            try:
                full = p + urllib.request.quote(cap_url, safe='')
                req = urllib.request.Request(full, headers={'User-Agent': 'Mozilla/5.0'})
                resp = urllib.request.urlopen(req, timeout=30)
                xml = resp.read().decode('utf-8')
                lines = parse_xml(xml)
                if len(lines) > 5:
                    with open(f'{SUBS_DIR}/{vid}.txt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    print(f'OK {len(lines)} lines', flush=True)
                    ok = True
                    break
                else:
                    print(f'  {p[:25]}: only {len(lines)} lines', flush=True)
            except Exception as e:
                print(f'  {p[:25]}: {str(e)[:60]}', flush=True)
        if not ok:
            print('FAILED all proxies', flush=True)
        time.sleep(3)
    except Exception as e:
        print(f'ERROR: {str(e)[:60]}', flush=True)
