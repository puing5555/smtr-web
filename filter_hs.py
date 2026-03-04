import re

# Read all videos
with open('hs_academy_all.tsv', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total: {len(lines)}")

# Specific stock names/tickers only
stock_names = [
    # Korean stocks
    '삼성전자', 'SK하이닉스', '하이닉스', '현대차', '현대자동차', 'LG에너지솔루션', 'LG엔솔',
    '카카오', '네이버', '삼성SDI', '삼성바이오', '삼성물산', '포스코', 'POSCO', '기아',
    'LG화학', 'LG전자', 'SK이노베이션', 'SK텔레콤', 'KT', '셀트리온', '크래프톤',
    'HD현대', 'KB금융', '신한지주', '하나금융', '우리금융', '한화에어로스페이스', '한화오션',
    '두산에너빌리티', '한국전력', '한전', 'HLB', '에코프로', '에코프로비엠', '포스코퓨처엠',
    'NAVER', '한미반도체', '리노공업', '주성엔지니어링', 'ISC', '레인보우로보틱스',
    '한화시스템', '현대로템', 'HD한국조선', '삼성중공업', '대우조선', '코스모신소재',
    'LS일렉트릭', 'LS', '일진하이솔루스', '두산밥캣', '한온시스템',
    # US stocks  
    '엔비디아', 'NVIDIA', 'NVDA', '테슬라', 'Tesla', 'TSLA',
    '애플', 'Apple', 'AAPL', '아마존', 'Amazon', 'AMZN',
    '마이크로소프트', 'Microsoft', 'MSFT', '메타', 'Meta', 'META',
    '구글', '알파벳', 'Google', 'Alphabet', 'GOOG', 'GOOGL',
    '넷플릭스', 'Netflix', 'NFLX', '팔란티어', 'Palantir', 'PLTR',
    'AMD', '인텔', 'Intel', 'INTC', 'ASML', 'TSMC', 'TSM',
    '브로드컴', 'Broadcom', 'AVGO', '퀄컴', 'Qualcomm', 'QCOM',
    'ARM', '마이크론', 'Micron', 'MU', '코인베이스', 'Coinbase', 'COIN',
    '스노우플레이크', 'Snowflake', 'SNOW', '크라우드스트라이크', 'CrowdStrike', 'CRWD',
    '슈퍼마이크로', 'SMCI', '서비스나우', 'ServiceNow', 'NOW',
    '일라이릴리', 'Eli Lilly', 'LLY', '노보노디스크', 'Novo Nordisk', 'NVO',
    '버크셔', 'Berkshire', 'BRK', '워렌버핏', '버핏',
    'SOXX', 'QQQ', 'SPY', 'VOO',
    '로켓랩', 'Rocket Lab', 'RKLB', '리비안', 'Rivian', 'RIVN',
    '루시드', 'Lucid', 'LCID', '니오', 'NIO',
    'Dell', '델', 'HPE', '오라클', 'Oracle', 'ORCL',
    '세일즈포스', 'Salesforce', 'CRM', '아이온큐', 'IonQ', 'IONQ',
    '도요타', 'Toyota', '소니', 'Sony', '소프트뱅크', 'SoftBank',
    '비트코인', 'BTC', '이더리움', 'ETH', '솔라나', 'SOL', '리플', 'XRP',
    # Shipbuilding/defense specific
    'HD현대중공업', '한화에어로', '한화디펜스', 'LIG넥스원',
    # Additional
    '샤오미', '바이두', '알리바바', '텐센트', 'BABA', 'TCEHY', 'PDD', '핀둬둬',
]

# Exclude patterns
exclude_patterns = [
    r'라이브', r'LIVE', r'live', r'Q&A', r'QnA', r'질의응답',
    r'기초용어', r'입문', r'왕초보', r'처음.*시작',
    r'shorts', r'#shorts', r'Shorts',
]

filtered = []
for line in lines:
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    vid_id, title = parts[0], parts[1]
    date = parts[2] if len(parts) > 2 else 'NA'
    
    # Check exclude
    if any(re.search(p, title, re.IGNORECASE) for p in exclude_patterns):
        continue
    
    # Check if any stock name/ticker appears in title
    matched = []
    for stock in stock_names:
        if stock.lower() in title.lower():
            matched.append(stock)
    
    if matched:
        filtered.append((vid_id, title, date, matched))

print(f"Filtered (stock name in title): {len(filtered)}")

# Show sample 30
print("\n=== SAMPLE (first 30) ===")
for i, (vid_id, title, date, matched) in enumerate(filtered[:30]):
    print(f"{i+1}. [{', '.join(set(matched))}] {title}")

# Stats: most mentioned stocks
from collections import Counter
stock_counts = Counter()
for _, _, _, matched in filtered:
    for m in set(matched):
        # Normalize
        m_lower = m.lower()
        if m_lower in ['엔비디아','nvidia','nvda']: stock_counts['엔비디아'] += 1
        elif m_lower in ['테슬라','tesla','tsla']: stock_counts['테슬라'] += 1
        elif m_lower in ['애플','apple','aapl']: stock_counts['애플'] += 1
        elif m_lower in ['삼성전자']: stock_counts['삼성전자'] += 1
        elif m_lower in ['sk하이닉스','하이닉스']: stock_counts['SK하이닉스'] += 1
        elif m_lower in ['마이크로소프트','microsoft','msft']: stock_counts['MS'] += 1
        elif m_lower in ['구글','알파벳','google','alphabet','goog','googl']: stock_counts['구글'] += 1
        elif m_lower in ['아마존','amazon','amzn']: stock_counts['아마존'] += 1
        elif m_lower in ['메타','meta']: stock_counts['메타'] += 1
        elif m_lower in ['tsmc','tsm']: stock_counts['TSMC'] += 1
        elif m_lower in ['amd']: stock_counts['AMD'] += 1
        elif m_lower in ['asml']: stock_counts['ASML'] += 1
        elif m_lower in ['비트코인','btc']: stock_counts['비트코인'] += 1
        elif m_lower in ['팔란티어','palantir','pltr']: stock_counts['팔란티어'] += 1
        else: stock_counts[m] += 1

print("\n=== TOP 20 STOCKS ===")
for stock, count in stock_counts.most_common(20):
    print(f"  {stock}: {count}")

# Save filtered
with open('hs_academy_stock_filtered.tsv', 'w', encoding='utf-8') as f:
    for vid_id, title, date, matched in filtered:
        f.write(f"{vid_id}\t{title}\t{date}\t{','.join(set(matched))}\n")
