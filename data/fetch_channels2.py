import urllib.request, re, json, time

def get_channel_info(handle):
    """Fetch video count and subscriber count from YouTube channel page HTML."""
    url = f'https://www.youtube.com/{handle}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9'
    })
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
    except Exception as e:
        return None, None
    
    # Video count - look for videosCountText in the raw HTML
    video_count = None
    patterns = [
        r'"videosCountText":\{"runs":\[\{"text":"([\d,]+)"\}',
        r'"videosCountText":\{"simpleText":"[^\d]*([\d,]+)',
        r'"videoCountText":\{"runs":\[\{"text":"([\d,]+)"\}',
        r'"videoCountText":\{"simpleText":"([\d,]+)',
        r'([\d,]+)\s*개의 동영상',
        r'"videoCount":"(\d+)"',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            video_count = int(m.group(1).replace(',', ''))
            break
    
    # Subscriber count
    sub_count = None
    sub_patterns = [
        r'"subscriberCountText":\{"simpleText":"구독자\s*([\d.]+[만천]?)명?"',
        r'"subscriberCountText":\{"simpleText":"([\d.]+[KMB]?) subscribers"',
        r'"subscriberCountText":\{[^}]*"simpleText":"([^"]+)"',
    ]
    for p in sub_patterns:
        m = re.search(p, html)
        if m:
            sub_count = m.group(1)
            break
    
    return video_count, sub_count

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
for category, ch_dict in channels.items():
    for name, handle in ch_dict.items():
        print(f"Fetching {name} ({handle})...", end=" ", flush=True)
        vc, sc = get_channel_info(handle)
        print(f"videos={vc}, subs={sc}", flush=True)
        results.append({
            "name": name,
            "category": category,
            "youtube_handle": handle,
            "video_count": vc if vc else -1,
            "subscriber_estimate": sc if sc else "N/A"
        })
        time.sleep(0.5)

with open(r"C:\Users\Mario\work\data\channel_video_counts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone! {len(results)} channels.")
found = sum(1 for r in results if r['video_count'] > 0)
print(f"Successfully found: {found}/{len(results)}")
for r in results:
    print(f"  {r['name']}: {r['video_count']} videos, {r['subscriber_estimate']} subs")
