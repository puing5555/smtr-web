
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 후보 종목
candidates = {
    "060230.KS": "다날",
    "234340.KS": "헥토파이낸셜",
    "041590.KS": "NHN KCP",
    "035420.KS": "NAVER",
    "035720.KS": "카카오",
    "067160.KS": "아프리카TV",
    "222980.KQ": "아이씨케이",
    "250000.KQ": "핑거",
    "214270.KQ": "FSN",
    "003550.KS": "LG",
    "323410.KS": "카카오뱅크",
    "377300.KS": "카카오페이",
    "086520.KS": "에코프로",
    "095570.KQ": "AJ네트웍스",
}

print("=== 후보 종목 데이터 수집 시도 ===")
valid = {}
for ticker, name in candidates.items():
    try:
        info = yf.Ticker(ticker).fast_info
        price = getattr(info, 'last_price', None)
        if price and price > 0:
            print(f"OK {name} ({ticker}): {price}")
            valid[ticker] = name
        else:
            print(f"NO {name} ({ticker}): price={price}")
    except Exception as e:
        print(f"ERR {name} ({ticker}): {e}")

print(f"\n유효 종목: {list(valid.keys())}")

print("\n=== 유효 종목 2/24~2/28 데이터 ===")
results_data = {}
for ticker, name in valid.items():
    try:
        df = yf.download(ticker, start="2026-02-23", end="2026-03-03", auto_adjust=True, progress=False)
        if len(df) > 0:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df["pct"] = df["Close"].pct_change() * 100
            results_data[name] = df
            print(f"\n{name} ({ticker}):")
            print(df[["Open","High","Low","Close","Volume","pct"]].to_string())
    except Exception as e:
        print(f"  {name} 오류: {e}")

# 매매 시뮬레이션
print("\n=== 매매 시뮬레이션 (2/26 시가 매수) ===")
print(f"{'종목':<15} {'시가':>10} {'2/26종가':>10} {'2/27종가':>10} {'A당일%':>8} {'B다음날%':>10}")
for name, df in results_data.items():
    try:
        # 날짜 형식 맞추기
        df.index = pd.to_datetime(df.index)
        dates = [str(d.date()) for d in df.index]
        
        buy_d = "2026-02-26"
        sell_A = "2026-02-26"
        sell_B = "2026-02-27"
        
        if buy_d in dates:
            idx_buy = dates.index(buy_d)
            buy_price = float(df.iloc[idx_buy]["Open"])
            close_A = float(df.iloc[idx_buy]["Close"])
            ret_A = (close_A - buy_price) / buy_price * 100
            
            ret_B = None
            if sell_B in dates:
                idx_b = dates.index(sell_B)
                close_B = float(df.iloc[idx_b]["Close"])
                ret_B = (close_B - buy_price) / buy_price * 100
            
            ret_B_str = f"{ret_B:+.2f}%" if ret_B is not None else "N/A"
            print(f"{name:<15} {buy_price:>10.0f} {close_A:>10.0f} {'':>10} {ret_A:>+8.2f}% {ret_B_str:>10}")
        else:
            print(f"{name:<15} 2/26 데이터 없음 (available: {dates[:5]})")
    except Exception as e:
        print(f"{name}: 시뮬 오류 {e}")
