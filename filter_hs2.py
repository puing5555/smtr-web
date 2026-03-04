import re

with open('hs_academy_all.tsv', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

# Only match stock names that are unambiguous (no short English tickers that collide with common words)
stock_patterns = [
    # Korean stocks - exact Korean names (no false positives)
    (r'삼성전자', '삼성전자'), (r'SK하이닉스|하이닉스', 'SK하이닉스'), (r'현대차|현대자동차', '현대차'),
    (r'LG에너지솔루션|LG엔솔', 'LG에너지'), (r'카카오(?!톡|페이지|스토리)', '카카오'), (r'네이버', '네이버'),
    (r'삼성SDI', '삼성SDI'), (r'삼성바이오', '삼성바이오'), (r'포스코|POSCO', '포스코'),
    (r'기아(?!나)', '기아'), (r'LG화학', 'LG화학'), (r'LG전자', 'LG전자'),
    (r'셀트리온', '셀트리온'), (r'크래프톤', '크래프톤'), (r'한화에어로', '한화에어로'),
    (r'한화오션', '한화오션'), (r'두산에너빌리티', '두산에너'), (r'한국전력|한전기', '한전'),
    (r'에코프로', '에코프로'), (r'포스코퓨처엠', '포스코퓨처엠'), (r'한미반도체', '한미반도체'),
    (r'현대로템', '현대로템'), (r'HD현대|HD한국조선', 'HD현대'), (r'삼성중공업', '삼성중공업'),
    (r'LS일렉트릭', 'LS일렉'), (r'한화시스템', '한화시스템'), (r'LIG넥스원', 'LIG넥스원'),
    # US stocks - Korean names (safe)
    (r'엔비디아', '엔비디아'), (r'테슬라', '테슬라'), (r'애플(?!워치|뮤직|TV)', '애플'),
    (r'아마존', '아마존'), (r'마이크로소프트', 'MS'), (r'구글|알파벳', '구글'),
    (r'넷플릭스', '넷플릭스'), (r'팔란티어', '팔란티어'), (r'인텔(?!리전)', '인텔'),
    (r'브로드컴', '브로드컴'), (r'퀄컴', '퀄컴'), (r'마이크론', '마이크론'),
    (r'슈퍼마이크로', '슈퍼마이크로'), (r'일라이릴리', '일라이릴리'),
    (r'노보노디스크', '노보노디스크'), (r'로켓랩', '로켓랩'),
    (r'크라우드스트라이크', '크라우드스트라이크'), (r'스노우플레이크', '스노우플레이크'),
    (r'세일즈포스', '세일즈포스'), (r'코인베이스', '코인베이스'),
    (r'비트코인', '비트코인'), (r'이더리움', '이더리움'), (r'솔라나', '솔라나'), (r'리플(?!효과)', '리플'),
    (r'바이두', '바이두'), (r'알리바바', '알리바바'), (r'텐센트', '텐센트'), (r'샤오미', '샤오미'),
    (r'소프트뱅크', '소프트뱅크'), (r'도요타', '도요타'),
    # US tickers - only long/unambiguous ones
    (r'\bNVIDIA\b', '엔비디아'), (r'\bNVDA\b', '엔비디아'),
    (r'\bTesla\b', '테슬라'), (r'\bTSLA\b', '테슬라'),
    (r'\bApple\b', '애플'), (r'\bAAPL\b', '애플'),
    (r'\bAmazon\b', '아마존'), (r'\bAMZN\b', '아마존'),
    (r'\bMicrosoft\b', 'MS'), (r'\bMSFT\b', 'MS'),
    (r'\bGoogle\b', '구글'), (r'\bAlphabet\b', '구글'),
    (r'\bNetflix\b', '넷플릭스'), (r'\bPalantir\b', '팔란티어'),
    (r'\bTSMC\b', 'TSMC'), (r'\bASML\b', 'ASML'), (r'\bAMD\b', 'AMD'),
    (r'\bIntel\b', '인텔'), (r'\bBroadcom\b', '브로드컴'),
    (r'\bBerkshire\b|워렌버핏|버핏', '버핏'),
    (r'메타(?!버스|데이터|인지)', '메타'),  # 메타 but not 메타버스
]

exclude_patterns = [
    r'라이브', r'\bLIVE\b', r'Q&A', r'QnA', r'질의응답',
    r'기초용어', r'입문', r'왕초보',
    r'#shorts', r'#Shorts',
]

filtered = []
for line in lines:
    parts = line.split('\t')
    if len(parts) < 2: continue
    vid_id, title = parts[0], parts[1]
    date = parts[2] if len(parts) > 2 else 'NA'
    
    if any(re.search(p, title, re.IGNORECASE) for p in exclude_patterns):
        continue
    
    matched = set()
    for pattern, label in stock_patterns:
        if re.search(pattern, title):
            matched.add(label)
    
    if matched:
        filtered.append((vid_id, title, date, matched))

print(f"Total: {len(lines)}")
print(f"Filtered: {len(filtered)}")

print("\n=== SAMPLE (first 30) ===")
for i, (vid_id, title, date, matched) in enumerate(filtered[:30]):
    stocks = ', '.join(sorted(matched))
    print(f"{i+1}. [{stocks}] {title}")

from collections import Counter
c = Counter()
for _,_,_,m in filtered:
    for s in m: c[s] += 1
print("\n=== TOP 20 STOCKS ===")
for s, n in c.most_common(20):
    print(f"  {s}: {n}")

with open('hs_academy_stock_filtered.tsv', 'w', encoding='utf-8') as f:
    for vid_id, title, date, matched in filtered:
        f.write(f"{vid_id}\t{title}\t{date}\t{','.join(sorted(matched))}\n")
