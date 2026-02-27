"""
Fetch recent 10 videos from a YouTube channel and their subtitles.
Usage: python fetch_channel.py <channel_handle> <output_dir>
Example: python fetch_channel.py @syuka_world subs_syuka
"""
import urllib.request, json, re, os, sys, time

def get_channel_videos(handle, count=10):
    """Get recent videos from a channel via web scrape."""
    url = f'https://www.youtube.com/{handle}/videos'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9'
    })
    resp = urllib.request.urlopen(req, timeout=30)
    html = resp.read().decode('utf-8')
    
    # Extract ytInitialData
    m = re.search(r'var ytInitialData\s*=\s*({.*?});</script>', html)
    if not m:
        m = re.search(r'ytInitialData\s*=\s*({.*?});</script>', html)
    if not m:
        print("Could not find ytInitialData", flush=True)
        return []
    
    data = json.loads(m.group(1))
    
    videos = []
    # Navigate to video list
    try:
        tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
        for tab in tabs:
            tr = tab.get('tabRenderer', {})
            if tr.get('selected'):
                items = tr['content']['richGridRenderer']['contents']
                for item in items:
                    vid_r = item.get('richItemRenderer', {}).get('content', {}).get('videoRenderer', {})
                    if vid_r:
                        vid_id = vid_r.get('videoId', '')
                        title = vid_r.get('title', {}).get('runs', [{}])[0].get('text', '')
                        length = vid_r.get('lengthText', {}).get('simpleText', '')
                        if vid_id and title:
                            videos.append({'id': vid_id, 'title': title, 'length': length})
                            if len(videos) >= count:
                                break
                break
    except (KeyError, IndexError) as e:
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
            mins, secs = t_ms // 60000, (t_ms % 60000) // 1000
            lines.append(f'[{mins:02d}:{secs:02d}] {text}')
    if not lines:
        for m in re.finditer(r'<text start="([\d.]+)"[^>]*>(.*?)</text>', xml_text, re.DOTALL):
            t = float(m.group(1))
            text = re.sub(r'<[^>]+>', '', m.group(2).strip())
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
            if text:
                lines.append(f'[{int(t)//60:02d}:{int(t)%60:02d}] {text}')
    return lines

def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch_channel.py <handle> <output_dir>")
        sys.exit(1)
    
    handle = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Fetching videos from {handle}...", flush=True)
    videos = get_channel_videos(handle, 10)
    print(f"Found {len(videos)} videos", flush=True)
    
    # Save video list
    with open(f'{out_dir}/_videos.txt', 'w', encoding='utf-8') as f:
        for v in videos:
            f.write(f"{v['id']}|{v['title']}|{v['length']}\n")
    
    # Fetch subtitles
    ok, fail = 0, 0
    for i, v in enumerate(videos):
        outfile = f"{out_dir}/{v['id']}.txt"
        if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
            print(f"[{i+1}/{len(videos)}] SKIP {v['id']}", flush=True)
            ok += 1
            continue
        
        print(f"[{i+1}/{len(videos)}] {v['id']} - {v['title'][:40]}...", end=' ', flush=True)
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
