import urllib.request, re, json, time

def get_channel_info(handle):
    url = f'https://www.youtube.com/{handle}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Cookie': 'CONSENT=YES+1'
    })
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except Exception as e:
        return None, None, None
    
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not m:
        return None, None, None
    
    text = m.group(1)  # raw JSON string
    
    # Video count: "동영상 X개" or "동영상 X만개" or "동영상 X,XXX개"
    video_count = None
    vm = re.search(r'\\"content\\":\s*\\"동영상\s*([\d,.]+)(만|천)?개\\"', text)
    if not vm:
        vm = re.search(r'"content":\s*"동영상\s*([\d,.]+)(만|천)?개"', text)
    if not vm:
        # Try unicode escaped
        vm = re.search(r'\\ub3d9\\uc601\\uc0c1\s*([\d,.]+)(\\ub9cc|\\ucc9c)?\\uac1c', text)
    if vm:
        num = float(vm.group(1).replace(',', ''))
        suffix = vm.group(2) if vm.group(2) else ''
        if suffix in ('만', '\\ub9cc'):
            video_count = int(num * 10000)
        elif suffix in ('천', '\\ucc9c'):
            video_count = int(num * 1000)
        else:
            video_count = int(num)
    
    # Subscriber count: "구독자 X만명" etc
    sub = None
    sm = re.search(r'\\"content\\":\s*\\"구독자\s*([^"\\]+)\\"', text)
    if not sm:
        sm = re.search(r'"content":\s*"구독자\s*([^"]+)"', text)
    if not sm:
        sm = re.search(r'\\uad6c\\ub3c5\\uc790\s*([^"\\]+?)\\u', text)
    if sm:
        sub = sm.group(1).strip()
    
    # Channel name from page title
    name = None
    nm = re.search(r'"pageTitle":\s*"([^"]+)"', text)
    if nm:
        name = nm.group(1)
    
    return video_count, sub, name

# Also try to decode the JSON properly
def get_channel_info_v2(handle):
    url = f'https://www.youtube.com/{handle}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Cookie': 'CONSENT=YES+1'
    })
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except Exception as e:
        return None, None, None
    
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not m:
        return None, None, None
    
    try:
        data = json.loads(m.group(1))
    except:
        return None, None, None
    
    text = json.dumps(data, ensure_ascii=False)
    
    video_count = None
    vm = re.search(r'"content":\s*"동영상\s*([\d,.]+)(만|천)?개"', text)
    if vm:
        num = float(vm.group(1).replace(',', ''))
        suffix = vm.group(2) or ''
        if suffix == '만':
            video_count = int(num * 10000)
        elif suffix == '천':
            video_count = int(num * 1000)
        else:
            video_count = int(num)
    
    sub = None
    sm = re.search(r'"content":\s*"구독자\s*([^"]+)"', text)
    if sm:
        sub = sm.group(1).strip()
    
    name = None
    header = data.get('header', {}).get('pageHeaderRenderer', {})
    name = header.get('pageTitle', '')
    
    return video_count, sub, name


channels = {
    "한국주식": {
        "삼프로TV": "@3protv",
        "부읽남TV": "@buridnam",
        "주코노미": "@jooconomy",
        "염승환 투자노트": "@yeominvest",
        "한국경제TV": "@WOWTV",
        "이효석아카데미": "@hyoseokacademy",
        "소수몽키": "@sosumonkey",
        "삼성증권": "@SamsungSecurities",
        "미래에셋증권": "@MiraeAssetSecurities",
        "달란트투자": "@dalranttuja",
        "KB증권": "@kbsec",
        "세상학개론": "@sesanghak",
        "이베스트스탁": "@ebesttv",
        "코린이아빠": "@coriniappa",
    },
    "미국주식": {
        "미주은": "@mijueun",
        "미부": "@mibustocks",
        "뉴욕주민": "@newyorkjumin",
        "재테크하는 공대누나": "@gongdaenuna",
        "한그루": "@hangru",
        "수페TV": "@supetv",
        "머스야": "@meosya",
        "래퍼투자": "@rappertuja",
        "미국주식 주주총회": "@jujuchonghoe",
        "배당쟁이": "@baedangjaengi",
        "정신과의사 투자클럽": "@psychiatrist_invest",
        "미래에셋 글로벌": "@MiraeAssetGlobal",
        "나스닥매니아": "@nasdaqmania",
        "테크형": "@techhyung",
        "노미의 글로벌 투자": "@nomi_global",
        "미국주식 사관학교": "@usstock_academy",
    },
    "크립토": {
        "김치코인": "@kimchicoin",
        "크립토지니": "@cryptogenie",
        "비트코인갤러리": "@bitcoingallery",
        "코인읽어주는남자": "@coinman",
        "크립토퀀트": "@CryptoQuant",
        "땡글아카데미": "@ddangle",
    },
}

results = []
failed = []
for category, ch_dict in channels.items():
    for name, handle in ch_dict.items():
        print(f"Fetching {name} ({handle})...", end=" ", flush=True)
        vc, sc, yt_name = get_channel_info_v2(handle)
        if vc is None and sc is None:
            print(f"FAILED (404 or parse error)", flush=True)
            failed.append((name, handle, category))
        else:
            print(f"videos={vc}, subs={sc}, yt_name={yt_name}", flush=True)
        results.append({
            "name": name,
            "category": category,
            "youtube_handle": handle,
            "video_count": vc if vc else -1,
            "subscriber_estimate": sc if sc else "N/A",
            "youtube_name": yt_name or ""
        })
        time.sleep(0.3)

with open(r"C:\Users\Mario\work\data\channel_video_counts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== RESULTS ===")
found = sum(1 for r in results if r['video_count'] > 0)
print(f"Found: {found}/{len(results)}")
for r in results:
    vc = r['video_count'] if r['video_count'] > 0 else 'FAILED'
    print(f"  [{r['category']}] {r['name']}: {vc} videos, {r['subscriber_estimate']} subs")

if failed:
    print(f"\n=== FAILED ({len(failed)}) - need handle correction ===")
    for name, handle, cat in failed:
        print(f"  {name} ({handle})")
