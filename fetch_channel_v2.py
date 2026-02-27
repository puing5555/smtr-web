"""
Fetch recent videos from YouTube channel via innertube browse API.
Usage: python fetch_channel_v2.py <channel_url_or_handle> <output_dir>
"""
import urllib.request, json, re, os, sys, time

def resolve_channel_id(handle_or_url):
    """Resolve channel ID from handle or URL via innertube."""
    # Try direct resolve via web page
    if handle_or_url.startswith('@'):
        url = f'https://www.youtube.com/{handle_or_url}'
    elif 'youtube.com' in handle_or_url:
        url = handle_or_url.rstrip('/')
        if '/videos' in url:
            url = url.replace('/videos', '')
    else:
        url = f'https://www.youtube.com/@{handle_or_url}'
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9'
    })
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8')
    
    # Find channel ID
    m = re.search(r'"channelId"\s*:\s*"(UC[^"]+)"', html)
    if m:
        return m.group(1)
    
    # Try externalId
    m = re.search(r'"externalId"\s*:\s*"(UC[^"]+)"', html)
    if m:
        return m.group(1)
    
    return None

def browse_channel_videos(channel_id):
    """Browse channel videos via innertube API."""
    url = 'https://www.youtube.com/youtubei/v1/browse'
    payload = json.dumps({
        'browseId': channel_id,
        'params': 'EgZ2aWRlb3PyBgQKAjoA',  # videos tab
        'context': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20240101.00.00',
                'hl': 'ko',
                'gl': 'KR'
            }
        }
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    })
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    
    videos = []
    # Navigate the response
    try:
        tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
        for tab in tabs:
            tr = tab.get('tabRenderer', {})
            content = tr.get('content', {})
            # richGridRenderer path
            rgr = content.get('richGridRenderer', {})
            if rgr:
                for item in rgr.get('contents', []):
                    vr = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                    if vr and vr.get('videoId'):
                        videos.append({
                            'id': vr['videoId'],
                            'title': vr.get('title', {}).get('runs', [{}])[0].get('text', ''),
                            'length': vr.get('lengthText', {}).get('simpleText', '')
                        })
                        if len(videos) >= 10:
                            break
            # sectionListRenderer path
            slr = content.get('sectionListRenderer', {})
            if slr and not videos:
                for section in slr.get('contents', []):
                    isr = section.get('itemSectionRenderer', {})
                    for item in isr.get('contents', []):
                        gr = item.get('gridRenderer', {})
                        for gi in gr.get('items', []):
                            gvr = gi.get('gridVideoRenderer', {})
                            if gvr and gvr.get('videoId'):
                                videos.append({
                                    'id': gvr['videoId'],
                                    'title': gvr.get('title', {}).get('runs', [{}])[0].get('text', ''),
                                    'length': gvr.get('thumbnailOverlays', [{}])[0].get('thumbnailOverlayTimeStatusRenderer', {}).get('text', {}).get('simpleText', '')
                                })
                                if len(videos) >= 10:
                                    break
    except Exception as e:
        print(f"Parse error: {e}", flush=True)
    
    return videos

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
    captions = result.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    if not captions:
        return None
    cap_url = captions[0]['baseUrl']
    for c in captions:
        if c.get('languageCode') == 'ko':
            cap_url = c['baseUrl']
    return cap_url

def fetch_via_proxy(cap_url):
    proxy_url = 'https://corsproxy.io/?' + urllib.request.quote(cap_url, safe='')
    req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30)
    return resp.read().decode('utf-8')

def parse_xml(xml_text):
    lines = []
    for m in re.finditer(r'<p t="(\d+)"[^>]*>(.*?)</p>', xml_text, re.DOTALL):
        t_ms = int(m.group(1))
        inner = m.group(2)
        segs = re.findall(r'<s[^>]*>([^<]*)</s>', inner)
        text = ''.join(segs).strip() if segs else re.sub(r'<[^>]+>', '', inner).strip()
        if text:
            lines.append(f'[{t_ms//60000:02d}:{(t_ms%60000)//1000:02d}] {text}')
    if not lines:
        for m in re.finditer(r'<text start="([\d.]+)"[^>]*>(.*?)</text>', xml_text, re.DOTALL):
            t = float(m.group(1))
            text = re.sub(r'<[^>]+>', '', m.group(2).strip())
            for old, new in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&#39;',"'"),('&quot;','"')]:
                text = text.replace(old, new)
            if text:
                lines.append(f'[{int(t)//60:02d}:{int(t)%60:02d}] {text}')
    return lines

def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch_channel_v2.py <channel_handle_or_url> <output_dir>")
        sys.exit(1)
    
    handle = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Resolving channel: {handle}...", flush=True)
    channel_id = resolve_channel_id(handle)
    if not channel_id:
        print("Could not resolve channel ID!", flush=True)
        sys.exit(1)
    print(f"Channel ID: {channel_id}", flush=True)
    
    print("Fetching video list...", flush=True)
    videos = browse_channel_videos(channel_id)
    print(f"Found {len(videos)} videos", flush=True)
    
    with open(f'{out_dir}/_videos.txt', 'w', encoding='utf-8') as f:
        for v in videos:
            f.write(f"{v['id']}|{v['title']}|{v['length']}\n")
            print(f"  {v['id']} | {v['title'][:60]}", flush=True)
    
    ok, fail = 0, 0
    for i, v in enumerate(videos):
        outfile = f"{out_dir}/{v['id']}.txt"
        if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
            print(f"[{i+1}/{len(videos)}] SKIP {v['id']}", flush=True)
            ok += 1
            continue
        print(f"[{i+1}/{len(videos)}] {v['id']}...", end=' ', flush=True)
        try:
            cap_url = get_caption_url(v['id'])
            if not cap_url:
                print("NO CAPTIONS", flush=True)
                fail += 1
                time.sleep(2)
                continue
            xml = fetch_via_proxy(cap_url)
            lines = parse_xml(xml)
            if len(lines) > 5:
                with open(outfile, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"OK ({len(lines)} lines)", flush=True)
                ok += 1
            else:
                print(f"TOO FEW ({len(lines)})", flush=True)
                fail += 1
        except Exception as e:
            print(f"ERROR: {str(e)[:60]}", flush=True)
            fail += 1
        time.sleep(3)
    
    print(f"\n=== {handle}: {ok} OK, {fail} failed ===", flush=True)

if __name__ == '__main__':
    main()
