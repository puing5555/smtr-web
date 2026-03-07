"""
=============================================================
뉴스 브리핑 파이프라인 v1
=============================================================
1단계: RSS 뉴스 수집
2단계: 시황 데이터 (yfinance)
3단계: Claude Sonnet AI 브리핑 생성
=============================================================
"""

import feedparser
import yfinance as yf
import pandas as pd
import anthropic
import os, json
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")

print("=" * 60)
print(f"뉴스 브리핑 파이프라인 | {NOW}")
print("=" * 60)


# ============================================================
# 1단계: RSS 뉴스 수집
# ============================================================

print("\n【1단계】 RSS 뉴스 수집")
print("-" * 40)

FEEDS = {
    "한국경제": "https://www.hankyung.com/feed/stock",
    "매일경제": "https://www.mk.co.kr/rss/30100041/",
    "조선비즈":  "https://biz.chosun.com/rss/stock/",
    "연합뉴스":  "https://www.yna.co.kr/rss/economy.xml",
    "이데일리":  "https://rss.edaily.co.kr/edaily_stock.xml",
}

# 대체 URL 목록 (메인 실패 시)
FALLBACK_FEEDS = {
    "한국경제":  "https://www.hankyung.com/feed/all-news",
    "매일경제":  "https://www.mk.co.kr/rss/30000001/",
    "조선비즈":  "https://biz.chosun.com/rss/finance/",
    "연합뉴스":  "https://www.yna.co.kr/rss/news.xml",
    "이데일리":  "https://rss.edaily.co.kr/edaily_economy.xml",
}

all_articles = []
feed_stats = {}

for source, url in FEEDS.items():
    try:
        feed = feedparser.parse(url)
        entries = feed.entries

        # 실패하면 fallback 시도
        if len(entries) == 0 and source in FALLBACK_FEEDS:
            print(f"  {source}: 기본 URL 실패 → 대체 URL 시도...")
            feed = feedparser.parse(FALLBACK_FEEDS[source])
            entries = feed.entries
            url = FALLBACK_FEEDS[source]

        count = len(entries)
        feed_stats[source] = count
        print(f"  {source}: {count}개 수집 ({url[:50]}...)")

        for entry in entries[:15]:  # 소스당 최대 15개
            title = entry.get('title', '').strip()
            link  = entry.get('link', '')
            pub   = entry.get('published', entry.get('updated', ''))

            if title:
                all_articles.append({
                    'source': source,
                    'title':  title,
                    'link':   link,
                    'published': pub,
                })

    except Exception as e:
        print(f"  {source}: ERROR — {e}")
        feed_stats[source] = 0

total_count = len(all_articles)
print(f"\n  ✅ 총 {total_count}개 기사 수집 ({len([s for s,c in feed_stats.items() if c>0])}개 소스 성공)")

# 최신 기사 30개 선택 (중복 제목 유사도 체크 간단 버전)
def is_duplicate(title, seen_titles, threshold=10):
    t_words = set(title[:20].split())
    for seen in seen_titles:
        s_words = set(seen[:20].split())
        if len(t_words & s_words) >= 3:
            return True
    return False

seen = []
deduped = []
for art in all_articles:
    if not is_duplicate(art['title'], seen):
        seen.append(art['title'])
        deduped.append(art)

print(f"  중복제거 후: {len(deduped)}개")

# 상위 40개 제목 출력
news_titles = [f"[{a['source']}] {a['title']}" for a in deduped[:40]]
print("\n📰 수집된 뉴스 (상위 20개):")
for i, t in enumerate(news_titles[:20], 1):
    print(f"  {i:02d}. {t[:70]}")


# ============================================================
# 2단계: 시황 데이터
# ============================================================

print("\n\n【2단계】 시황 데이터 수집")
print("-" * 40)

market_data = {}
market_display = []

def get_ticker(symbol, name, is_fx=False):
    try:
        d = yf.download(symbol, period='5d', auto_adjust=True, progress=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.droplevel(1)
        d = d.dropna()
        if len(d) < 2:
            return None, None, None

        cur = float(d['Close'].iloc[-1])
        prev = float(d['Close'].iloc[-2])
        chg = (cur - prev) / prev * 100

        if is_fx:
            disp = f"{name}: {cur:.2f} ({'+' if chg >= 0 else ''}{chg:.2f}%)"
        else:
            disp = f"{name}: {cur:,.2f} ({'+' if chg >= 0 else ''}{chg:.2f}%)"

        return cur, chg, disp
    except Exception as e:
        print(f"  {name}: 오류 — {e}")
        return None, None, None

tickers = [
    ("^KS11",   "코스피",         False),
    ("^KQ11",   "코스닥",         False),
    ("^GSPC",   "S&P500",        False),
    ("^IXIC",   "나스닥",         False),
    ("^DJI",    "다우존스",        False),
    ("BTC-USD", "BTC/USD",       False),
    ("ETH-USD", "ETH/USD",       False),
    ("KRW=X",   "USD/KRW",       True),
    ("GC=F",    "금(Gold)",       False),
    ("CL=F",    "WTI유가",        False),
    ("^VIX",    "VIX(공포지수)", False),
    ("069500.KS", "KODEX200",    False),
]

for symbol, name, is_fx in tickers:
    cur, chg, disp = get_ticker(symbol, name, is_fx)
    if disp:
        print(f"  {disp}")
        market_data[name] = {'price': cur, 'change': chg, 'display': disp}
        market_display.append(disp)
    else:
        print(f"  {name}: 데이터 없음")

# pykrx 외국인 수급 시도 (보통 안 됨)
print("\n  외국인 수급 (proxy: USD/KRW 방향):")
if 'USD/KRW' in market_data:
    usd = market_data['USD/KRW']
    chg = usd['change']
    if chg > 0:
        flow_msg = f"  USD/KRW +{chg:.2f}% → 원화 약세 (외국인 순매도 추정)"
    else:
        flow_msg = f"  USD/KRW {chg:.2f}% → 원화 강세 (외국인 순매수 추정)"
    print(f"  {flow_msg}")
    market_display.append(flow_msg.strip())

print(f"\n  ✅ {len(market_data)}개 시황 지표 수집 완료")


# ============================================================
# 3단계: AI 브리핑 생성
# ============================================================

print("\n\n【3단계】 AI 브리핑 생성 (Claude Sonnet)")
print("-" * 40)

market_text = "\n".join(market_display)
news_text   = "\n".join(news_titles[:40])

prompt = f"""[시황 데이터]
{market_text}

[오늘 뉴스 제목]
{news_text}

위 데이터로 오후 브리핑을 써줘.

형식:
🇺🇸 미국장 (3줄, 시황 데이터의 숫자만 사용)
🇰🇷 국내장 (3줄, 수급 데이터 포함)
₿ 크립토 (2줄)
⚠️ 주의할 점 (2줄)

규칙:
- 뉴스 제목에 없는 숫자 만들어내지 마
- 시황 데이터에 있는 숫자만 사용
- 인과관계는 "~로 보인다" 추정 표현 사용
- 확실하지 않으면 빼
- 같은 사건 여러 언론사 보도면 1번만
- 브리핑 날짜: {NOW}"""

# OpenClaw Gateway HTTP API 사용 (local, port 18789)
import re, subprocess
try:
    # openclaw config에서 token 가져오기
    cfg_path = os.path.expanduser(r'~/.openclaw/openclaw.json')
    with open(cfg_path, 'r', encoding='utf-8') as cf:
        raw_cfg = cf.read()
    token_match = re.search(r"token:\s*'([^']+)'", raw_cfg)
    gw_token = token_match.group(1) if token_match else ''
except:
    gw_token = ''

if gw_token:
    import urllib.request, json as _json
    payload = _json.dumps({
        "model": "anthropic/claude-sonnet-4-6",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800
    }).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:18789/v1/messages',
        data=payload,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {gw_token}'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = _json.loads(resp.read().decode('utf-8'))
            briefing = r['content'][0]['text']
            print("  ✅ 브리핑 생성 완료 (Gateway)")
    except Exception as gw_e:
        print(f"  Gateway 오류: {gw_e}")
        briefing = f"(Gateway 오류: {gw_e})"
else:
    print("  ⚠️ Gateway token 없음 — Anthropic SDK 직접 시도")
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    briefing = msg.content[0].text
    print("  ✅ 브리핑 생성 완료")

print("\n" + "=" * 60)
print("📋 AI 브리핑 원문")
print("=" * 60)
print(briefing)

# 결과 저장
result = {
    "timestamp": NOW,
    "rss_stats": feed_stats,
    "total_articles": total_count,
    "deduped_articles": len(deduped),
    "market_data": {k: v['display'] for k, v in market_data.items()},
    "briefing": briefing,
}
with open("C:/Users/Mario/work/news_briefing_latest.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n✅ 저장: news_briefing_latest.json")
print("=" * 60)

# 요약 통계
print("\n📊 파이프라인 요약:")
for src, cnt in feed_stats.items():
    status = "✅" if cnt > 0 else "❌"
    print(f"  {status} {src}: {cnt}개")
print(f"\n  총 수집: {total_count}개 → 중복제거: {len(deduped)}개")
print(f"  시황 지표: {len(market_data)}개")
print(f"  브리핑 길이: {len(briefing)}자")
