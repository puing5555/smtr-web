import urllib.request, re, json, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def google_search_channel(name):
    """Search Google for YouTube channel and extract the handle."""
    query = urllib.parse.quote(f'{name} youtube 채널')
    url = f'https://www.google.com/search?q={query}&hl=ko'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9'
    })
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    except Exception as e:
        return None
    
    # Find youtube.com/@handle patterns
    handles = re.findall(r'youtube\.com/@([\w\-._]+)', html)
    # Also find youtube.com/channel/ patterns
    channel_ids = re.findall(r'youtube\.com/channel/([\w\-]+)', html)
    
    return handles, channel_ids

def get_channel_info(handle_or_url):
    """Get video count and subscriber count from channel page."""
    if handle_or_url.startswith('http'):
        url = handle_or_url
    elif handle_or_url.startswith('@'):
        url = f'https://www.youtube.com/{handle_or_url}'
    else:
        url = f'https://www.youtube.com/@{handle_or_url}'
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Cookie': 'CONSENT=YES+1'
    })
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except:
        return None, None, None
    
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not m:
        return None, None, None
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
    
    name = data.get('header', {}).get('pageHeaderRenderer', {}).get('pageTitle', '')
    return video_count, sub, name

# Channels that need correct handles
need_handles = [
    ("주코노미", "한국주식"),
    ("KB증권", "한국주식"),
    ("이베스트스탁", "한국주식"),
    ("미부", "미국주식"),
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
    ("염승환 투자노트", "한국주식"),  # retry
]

# Also try known handle guesses
handle_guesses = {
    "주코노미": ["@zuconomy", "@jooconomyTV", "@주코노미", "@Jooconomy_hankyung"],
    "KB증권": ["@KBSecurities", "@kb_securities", "@KBsec_official"],
    "이베스트스탁": ["@eBESTstock", "@ebeststalk", "@eBEST"],
    "미부": ["@mibu_us", "@미부", "@mibu_stock"],
    "재테크하는 공대누나": ["@engineering_sister", "@공대누나재테크"],
    "한그루": ["@hangru_invest", "@한그루"],
    "머스야": ["@meosya_stock", "@머스야"],
    "래퍼투자": ["@rapper_invest", "@래퍼투자"],
    "미국주식 주주총회": ["@us_shareholders", "@미국주식주주총회"],
    "배당쟁이": ["@dividendjaengi", "@배당쟁이"],
    "정신과의사 투자클럽": ["@doctor_invest", "@정신과의사투자"],
    "미래에셋 글로벌": ["@MiraeAssetGlobalInvest", "@maboraeglobal"],
    "나스닥매니아": ["@NASDAQ_mania", "@나스닥매니아"],
    "테크형": ["@TechBro_kr", "@테크형"],
    "노미의 글로벌 투자": ["@nomi_invest", "@노미"],
    "미국주식 사관학교": ["@US_stock_school", "@미국주식사관학교"],
    "크립토지니": ["@crypto_genie", "@크립토지니"],
    "땡글아카데미": ["@ddangle_academy", "@땡글"],
    "염승환 투자노트": ["@yeom_invest", "@염승환", "@yeomseunghwan"],
}

results = []
for name, category in need_handles:
    print(f"\n=== {name} ===", flush=True)
    
    # First try Google search
    print(f"  Google search...", end=" ", flush=True)
    try:
        handles, ch_ids = google_search_channel(name)
        print(f"handles={handles[:5] if handles else []}", flush=True)
    except:
        handles, ch_ids = [], []
        print("failed", flush=True)
    
    found = False
    # Try handles from Google
    tried = set()
    for h in (handles or [])[:5]:
        if h in tried:
            continue
        tried.add(h)
        print(f"  Trying @{h}...", end=" ", flush=True)
        vc, sc, yt_name = get_channel_info(f"@{h}")
        if vc is not None or sc is not None:
            print(f"✓ {yt_name}: videos={vc}, subs={sc}", flush=True)
            results.append({
                "name": name, "category": category,
                "youtube_handle": f"@{h}",
                "video_count": vc or -1,
                "subscriber_estimate": sc or "N/A",
                "youtube_name": yt_name or ""
            })
            found = True
            break
        else:
            print("✗", flush=True)
        time.sleep(0.3)
    
    if not found:
        # Try guessed handles
        for h in handle_guesses.get(name, []):
            if h.lstrip('@') in tried:
                continue
            tried.add(h.lstrip('@'))
            print(f"  Trying {h}...", end=" ", flush=True)
            vc, sc, yt_name = get_channel_info(h)
            if vc is not None or sc is not None:
                print(f"✓ {yt_name}: videos={vc}, subs={sc}", flush=True)
                results.append({
                    "name": name, "category": category,
                    "youtube_handle": h if h.startswith("@") else f"@{h}",
                    "video_count": vc or -1,
                    "subscriber_estimate": sc or "N/A",
                    "youtube_name": yt_name or ""
                })
                found = True
                break
            else:
                print("✗", flush=True)
            time.sleep(0.3)
    
    if not found:
        print(f"  ✗ NOT FOUND", flush=True)
        results.append({
            "name": name, "category": category,
            "youtube_handle": "unknown",
            "video_count": -1,
            "subscriber_estimate": "N/A",
            "youtube_name": ""
        })
    
    time.sleep(0.5)

with open(r"C:\Users\Mario\work\data\failed_resolved2.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\n=== SUMMARY ===")
found_count = sum(1 for r in results if r['video_count'] > 0)
print(f"Found: {found_count}/{len(results)}")
for r in results:
    vc = r['video_count'] if r['video_count'] > 0 else 'FAILED'
    print(f"  {r['name']}: {vc} videos ({r['youtube_handle']})")
