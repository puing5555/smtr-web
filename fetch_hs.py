import subprocess, json, sys

result = subprocess.run(
    [sys.executable, "-m", "yt_dlp", "--flat-playlist", 
     "--print", "%(id)s\t%(title)s\t%(upload_date)s",
     "https://www.youtube.com/@hs_academy/videos"],
    capture_output=True, text=True, encoding='utf-8', timeout=300
)

lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
print(f"Total videos: {len(lines)}")

# Save raw
with open('hs_academy_all.tsv', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

# Investment keywords
invest_kw = [
    '주식', '투자', '종목', '매수', '매도', '실적', '주가', '배당', '증시', '코스피', '코스닥',
    '나스닥', 'S&P', 'ETF', '반도체', 'AI', '삼성', 'SK', '엔비디아', 'NVIDIA', '테슬라', 'Tesla',
    '애플', 'Apple', '마이크로소프트', '구글', '아마존', '메타', '비트코인', '코인', '암호화폐',
    '금리', '환율', '달러', '인플레이션', '연준', 'Fed', '채권', '부동산', '경제', '시장',
    '성장주', '가치주', '배당주', '포트폴리오', '리밸런싱', '밸류에이션', 'PER', 'PBR', 'ROE',
    '수익률', '차트', '기술적', '펀더멘탈', '실적', '어닝', '분기', '매출', '영업이익',
    '원전', '방산', '바이오', '제약', '2차전지', '배터리', '자동차', 'EV', '전기차',
    '엔터', '게임', '플랫폼', '클라우드', '데이터센터', '로봇', '자율주행',
    '상승', '하락', '폭락', '급등', '랠리', '조정', '저점', '고점', '바닥',
    '트럼프', '관세', '무역', '전쟁', '지정학', '중국', '일본', '유럽',
    '삼프로', '이효석', '홍춘욱', '박세익', '이경수', '김한진',
    '전망', '분석', '해설', '리뷰', '브리핑', '전략',
    'LG', '현대', '카카오', '네이버', 'TSMC', 'AMD', 'ASML',
    '금', '은', '원유', '구리', '원자재',
]

# Exclude keywords
exclude_kw = [
    '브이로그', 'vlog', '일상', '먹방', '쿡방', '여행', '운동', '헬스',
    'shorts', 'Short', '#shorts',
]

filtered = []
excluded = []

for line in lines:
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    vid_id, title = parts[0], parts[1]
    date = parts[2] if len(parts) > 2 else 'NA'
    
    title_lower = title.lower()
    
    # Check exclude first
    if any(kw.lower() in title_lower for kw in exclude_kw):
        excluded.append((vid_id, title, date, 'excluded'))
        continue
    
    # Check investment keywords
    if any(kw.lower() in title_lower for kw in invest_kw):
        filtered.append((vid_id, title, date))
    else:
        excluded.append((vid_id, title, date, 'no_keyword'))

print(f"Investment-related: {len(filtered)}")
print(f"Excluded: {len(excluded)}")

# Save filtered
with open('hs_academy_filtered.tsv', 'w', encoding='utf-8') as f:
    for vid_id, title, date in filtered:
        f.write(f"{vid_id}\t{title}\t{date}\n")

# Print sample
print("\n=== SAMPLE (first 20) ===")
for i, (vid_id, title, date) in enumerate(filtered[:20]):
    print(f"{i+1}. [{date}] {title}")

print(f"\n=== EXCLUDED SAMPLE (first 10) ===")
for i, (vid_id, title, date, reason) in enumerate(excluded[:10]):
    print(f"{i+1}. [{date}] {title} ({reason})")
