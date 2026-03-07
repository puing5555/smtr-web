"""1단계+2단계만 실행해서 JSON 저장"""
import feedparser, yfinance as yf, pandas as pd
import json, os
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
print(f"수집 시작: {NOW}")

# ── RSS 수집 ──
FEEDS = {
    "한국경제": "https://www.hankyung.com/feed/all-news",
    "매일경제": "https://www.mk.co.kr/rss/30100041/",
    "연합뉴스": "https://www.yna.co.kr/rss/economy.xml",
    "이데일리": "https://rss.edaily.co.kr/edaily_stock.xml",
    "서울경제": "https://www.sedaily.com/RSS/RSS_Economy.xml",
}
FALLBACK = {
    "이데일리": "https://rss.edaily.co.kr/edaily_economy.xml",
    "서울경제": "https://www.sedaily.com/RSS/RSS_All.xml",
}

all_art = []
feed_stats = {}
for src, url in FEEDS.items():
    try:
        feed = feedparser.parse(url)
        entries = feed.entries
        if len(entries) == 0 and src in FALLBACK:
            feed = feedparser.parse(FALLBACK[src])
            entries = feed.entries
        feed_stats[src] = len(entries)
        for e in entries[:20]:
            t = e.get('title', '').strip()
            if t:
                all_art.append({'source': src, 'title': t, 'link': e.get('link',''), 'pub': e.get('published','')})
        print(f"  {src}: {len(entries)}개")
    except Exception as ex:
        print(f"  {src}: ERROR {ex}")
        feed_stats[src] = 0

# 간단 중복 제거
seen, deduped = [], []
for a in all_art:
    w = set(a['title'][:30].split())
    dup = any(len(w & set(s[:30].split())) >= 3 for s in seen)
    if not dup:
        seen.append(a['title'])
        deduped.append(a)

print(f"\n총 {len(all_art)}개 → 중복제거 {len(deduped)}개")

# ── 시황 수집 ──
TICKERS = [
    ("^KS11",   "코스피",    False),
    ("^KQ11",   "코스닥",    False),
    ("^GSPC",   "S&P500",   False),
    ("^IXIC",   "나스닥",    False),
    ("^DJI",    "다우",      False),
    ("BTC-USD", "BTC/USD",  False),
    ("ETH-USD", "ETH/USD",  False),
    ("KRW=X",   "USD/KRW",  True),
    ("GC=F",    "금(Gold)", False),
    ("CL=F",    "WTI유가",  False),
    ("^VIX",    "VIX",      False),
]

mkt = {}
for sym, name, fx in TICKERS:
    try:
        d = yf.download(sym, period='5d', auto_adjust=True, progress=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.droplevel(1)
        d = d.dropna()
        if len(d) < 2: continue
        cur  = float(d['Close'].iloc[-1])
        prev = float(d['Close'].iloc[-2])
        chg  = (cur - prev) / prev * 100
        sign = '+' if chg >= 0 else ''
        disp = f"{name}: {cur:.2f} ({sign}{chg:.2f}%)" if fx else f"{name}: {cur:,.2f} ({sign}{chg:.2f}%)"
        mkt[name] = {'price': cur, 'change': chg, 'display': disp}
        print(f"  {disp}")
    except Exception as ex:
        print(f"  {name}: ERR {ex}")

# 외국인 수급 proxy
if 'USD/KRW' in mkt:
    c = mkt['USD/KRW']['change']
    flow = f"외국인수급proxy: USD/KRW {'+' if c>=0 else ''}{c:.2f}% → 원화 {'약세(순매도 추정)' if c>0 else '강세(순매수 추정)'}"
    mkt['외국인수급proxy'] = {'display': flow}
    print(f"  {flow}")

# 저장
result = {
    "timestamp": NOW,
    "feed_stats": feed_stats,
    "articles_total": len(all_art),
    "articles_deduped": len(deduped),
    "news_titles": [f"[{a['source']}] {a['title']}" for a in deduped[:45]],
    "market": {k: v['display'] for k, v in mkt.items()},
}
out = r"C:\Users\Mario\work\news_briefing_latest.json"
with open(out, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n저장 완료: {out}")
