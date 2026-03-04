"""
Batch search YouTube channels using browser automation approach.
Uses ytInitialData from direct channel URL access.
"""
import urllib.request, urllib.parse, re, json, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def fetch_yt_page(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Cookie': 'CONSENT=YES+1'
    })
    return urllib.request.urlopen(req, timeout=15).read().decode('utf-8')

def parse_channel_page(html):
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not m:
        return None, None, None
    data = json.loads(m.group(1))
    text = json.dumps(data, ensure_ascii=False)
    
    vc = None
    vm = re.search(r'"content":\s*"동영상\s*([\d,.]+)(만|천)?개"', text)
    if vm:
        num = float(vm.group(1).replace(',', ''))
        s = vm.group(2) or ''
        if s == '만': vc = int(num * 10000)
        elif s == '천': vc = int(num * 1000)
        else: vc = int(num)
    
    sc = None
    sm = re.search(r'"content":\s*"구독자\s*([^"]+)"', text)
    if sm: sc = sm.group(1).strip()
    
    name = data.get('header', {}).get('pageHeaderRenderer', {}).get('pageTitle', '')
    return vc, sc, name

# Complete channel list with best-guess handles
all_channels = [
    # 한국주식
    ("삼프로TV", "한국주식", "@3protv"),
    ("부읽남TV", "한국주식", "@buiknam_tv"),
    ("주코노미", "한국주식", "@wallstkid"),
    ("염승환 투자노트", "한국주식", "@yumseunghwan"),
    ("한국경제TV", "한국주식", "@hkwowtv"),
    ("이효석아카데미", "한국주식", "@hs_academy"),
    ("소수몽키", "한국주식", "@sosumonkey"),
    ("삼성증권", "한국주식", "@samsungsecurities"),
    ("미래에셋증권", "한국주식", "@MiraeAssetSecurities"),
    ("달란트투자", "한국주식", "@talentinvestment"),
    ("KB증권", "한국주식", "@KBSecurities_official"),
    ("세상학개론", "한국주식", "@sesang101"),
    ("이베스트스탁", "한국주식", "@eBESTInvestment"),
    ("코린이아빠", "한국주식", "@corinpapa1106"),
    # 미국주식
    ("미주은", "미국주식", "@mijooeun"),
    ("미부", "미국주식", "@mibu_stock"),
    ("뉴욕주민", "미국주식", "@newyork-er"),
    ("재테크하는 공대누나", "미국주식", "@gongdenuna"),
    ("한그루", "미국주식", "@hangru_money"),
    ("수페TV", "미국주식", "@supetv"),
    ("머스야", "미국주식", "@meosya_stock"),
    ("래퍼투자", "미국주식", "@rapper_invest"),
    ("미국주식 주주총회", "미국주식", "@stockholdersmeeting"),
    ("배당쟁이", "미국주식", "@dividendjaengi"),
    ("정신과의사 투자클럽", "미국주식", "@investpsych"),
    ("미래에셋 글로벌", "미국주식", "@maboraeglobal"),
    ("나스닥매니아", "미국주식", "@NASDAQ_mania"),
    ("테크형", "미국주식", "@TechBro_kr"),
    ("노미의 글로벌 투자", "미국주식", "@nomi_invest"),
    ("미국주식 사관학교", "미국주식", "@usstock_school"),
    # 크립토
    ("김치코인", "크립토", "@kimchicoin"),
    ("크립토지니", "크립토", "@cryptojenie"),
    ("비트코인갤러리", "크립토", "@bitcoingallery"),
    ("코인읽어주는남자", "크립토", "@coinman"),
    ("크립토퀀트", "크립토", "@CryptoQuant"),
    ("땡글아카데미", "크립토", "@ddangle_academy"),
]

results = []
for name, category, handle in all_channels:
    print(f"{name} ({handle})...", end=" ", flush=True)
    try:
        url = f"https://www.youtube.com/{handle}"
        html = fetch_yt_page(url)
        vc, sc, yt_name = parse_channel_page(html)
        if vc is not None or sc is not None:
            print(f"✓ videos={vc}, subs={sc}, name={yt_name}")
            results.append({"name": name, "category": category, "youtube_handle": handle,
                          "video_count": vc or -1, "subscriber_estimate": sc or "N/A"})
        else:
            print("✗ (page exists but no data)")
            results.append({"name": name, "category": category, "youtube_handle": handle,
                          "video_count": -1, "subscriber_estimate": "N/A"})
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP {e.code}")
        results.append({"name": name, "category": category, "youtube_handle": handle,
                      "video_count": -1, "subscriber_estimate": "N/A"})
    except Exception as e:
        print(f"✗ {e}")
        results.append({"name": name, "category": category, "youtube_handle": handle,
                      "video_count": -1, "subscriber_estimate": "N/A"})
    time.sleep(0.3)

with open(r"C:\Users\Mario\work\data\channel_video_counts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== SUMMARY ===")
found = sum(1 for r in results if r['video_count'] > 0)
print(f"Found: {found}/{len(results)}")
not_found = [r for r in results if r['video_count'] <= 0]
if not_found:
    print(f"\nStill missing ({len(not_found)}):")
    for r in not_found:
        print(f"  {r['name']} ({r['youtube_handle']})")
