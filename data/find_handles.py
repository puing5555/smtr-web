import subprocess, json, re, urllib.request, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

already_found = [
    {"name": "부읽남TV", "category": "한국주식", "youtube_handle": "@buiknam_tv", "video_count": 4100, "subscriber_estimate": "173만명", "youtube_name": "부읽남TV", "channel_url": ""}
]

failed_channels = [
    ("주코노미", "한국주식"),
    ("염승환 투자노트", "한국주식"),
    ("이효석아카데미", "한국주식"),
    ("달란트투자", "한국주식"),
    ("KB증권", "한국주식"),
    ("세상학개론", "한국주식"),
    ("이베스트스탁", "한국주식"),
    ("코린이아빠", "한국주식"),
    ("미주은", "미국주식"),
    ("미부", "미국주식"),
    ("뉴욕주민", "미국주식"),
    ("재테크하는 공대누나", "미국주식"),
    ("한그루", "미국주식"),
    ("머스야", "미국주식"),
    ("래퍼투자", "미국주식"),
    ("미국주식 주주총회", "미국주식"),
    ("배당쟁이", "미국주식"),
    ("정신과의사 투자클럽", "미국주식"),
    ("미래에셋 글로벌", "미국주식"),
    ("나스닥매니아", "미국주식"),
    ("테크형", "미국주식"),
    ("노미의 글로벌 투자", "미국주식"),
    ("미국주식 사관학교", "미국주식"),
    ("크립토지니", "크립토"),
    ("땡글아카데미", "크립토"),
]

def search_yt(query):
    """Use yt-dlp to search YouTube for a channel."""
    try:
        r = subprocess.run(
            ["python", "-m", "yt_dlp", "--dump-single-json", "--flat-playlist", "--playlist-end", "1",
             f"ytsearch1:{query} youtube 채널"],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode == 0:
            data = json.loads(r.stdout)
            entries = data.get("entries", [])
            if entries:
                e = entries[0]
                return e.get("channel_url", ""), e.get("channel_id", ""), e.get("uploader", ""), e.get("uploader_id", "")
    except:
        pass
    return None, None, None, None

def get_info_from_url(channel_url):
    """Get video count and subscriber count from channel page."""
    if not channel_url:
        return None, None
    req = urllib.request.Request(channel_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Cookie': 'CONSENT=YES+1'
    })
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except:
        return None, None
    
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not m:
        return None, None
    data = json.loads(m.group(1))
    text = json.dumps(data, ensure_ascii=False)
    
    video_count = None
    vm = re.search(r'"content":\s*"동영상\s*([\d,.]+)(만|천)?개"', text)
    if vm:
        num = float(vm.group(1).replace(',', ''))
        suffix = vm.group(2) or ''
        if suffix == '만': video_count = int(num * 10000)
        elif suffix == '천': video_count = int(num * 1000)
        else: video_count = int(num)
    
    sub = None
    sm = re.search(r'"content":\s*"구독자\s*([^"]+)"', text)
    if sm:
        sub = sm.group(1).strip()
    
    return video_count, sub

results = []
for name, category in failed_channels:
    print(f"Searching: {name}...", end=" ", flush=True)
    ch_url, ch_id, uploader, uploader_id = search_yt(name)
    handle = uploader_id if uploader_id and uploader_id.startswith("@") else f"@{uploader_id}" if uploader_id else "unknown"
    
    if ch_url:
        print(f"Found: {uploader} ({handle}), fetching info...", end=" ", flush=True)
        vc, sc = get_info_from_url(ch_url)
        print(f"videos={vc}, subs={sc}")
    else:
        vc, sc = None, None
        print("NOT FOUND")
    
    results.append({
        "name": name,
        "category": category,
        "youtube_handle": handle,
        "video_count": vc if vc else -1,
        "subscriber_estimate": sc if sc else "N/A",
        "youtube_name": uploader or "",
        "channel_url": ch_url or ""
    })
    time.sleep(0.5)

with open(r"C:\Users\Mario\work\data\failed_channels_resolved.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone! Resolved {sum(1 for r in results if r['video_count'] > 0)}/{len(results)}")
for r in results:
    vc = r['video_count'] if r['video_count'] > 0 else 'FAILED'
    print(f"  {r['name']}: {vc} ({r['youtube_handle']})")
