
import yfinance as yf
import pandas as pd
import datetime

# CRCL 일별 데이터
print("=== CRCL 일별 데이터 (2/20~3/4) ===")
crcl = yf.download("CRCL", start="2026-02-20", end="2026-03-04", interval="1d", auto_adjust=True, progress=False)
if len(crcl) > 0:
    crcl.columns = [c[0] if isinstance(c, tuple) else c for c in crcl.columns]
    crcl["pct_change"] = crcl["Close"].pct_change() * 100
    print(crcl[["Open","High","Low","Close","Volume","pct_change"]].to_string())
else:
    print("데이터 없음")

# 시간봉
print("\n=== 2/25~2/27 시간봉 (prepost=True) ===")
crcl_1h = yf.download("CRCL", start="2026-02-25", end="2026-02-28", interval="1h", auto_adjust=True, prepost=True, progress=False)
if len(crcl_1h) > 0:
    crcl_1h.columns = [c[0] if isinstance(c, tuple) else c for c in crcl_1h.columns]
    print(crcl_1h[["Open","High","Low","Close","Volume"]].to_string())
else:
    print("데이터 없음")

# CRCL 어닝 및 뉴스
print("\n=== CRCL 어닝/뉴스 ===")
crcl_ticker = yf.Ticker("CRCL")
try:
    ed = crcl_ticker.earnings_dates
    print("earnings_dates:")
    print(ed)
except Exception as e:
    print(f"earnings_dates 오류: {e}")

print("\n뉴스:")
try:
    news = crcl_ticker.news
    for n in news[:15]:
        title = n.get("title", "")
        ts = n.get("providerPublishTime", 0)
        if ts:
            dt = datetime.datetime.fromtimestamp(ts)
        else:
            dt = "N/A"
        print(f"{dt} | {title}")
except Exception as e:
    print(f"뉴스 오류: {e}")
