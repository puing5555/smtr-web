
import yfinance as yf
import pandas as pd

# 추가 후보 종목 (스테이블코인 대장주로 언급된 종목들)
extra = {
    "186230.KQ": "쿠콘",
    "099190.KQ": "아이오케이",
    "240600.KQ": "나이벡",      # 확인용
    "053800.KQ": "안랩",        # 보안/블록체인
    "263800.KQ": "아이씨티케이",
    "357120.KS": "미래에셋증권",  # 크립토 서비스
    "139480.KS": "이마트",
    "192080.KQ": "더블유게임즈",
    "037270.KQ": "YG PLUS",
    "102310.KQ": "이랜시스",
    "182360.KQ": "큐렉소",
}

print("=== 추가 종목 확인 ===")
valid_extra = {}
for ticker, name in extra.items():
    try:
        fi = yf.Ticker(ticker).fast_info
        price = getattr(fi, 'last_price', None)
        if price and price > 0:
            print(f"OK {name} ({ticker}): {price}")
            valid_extra[ticker] = name
        else:
            print(f"NO {name} ({ticker})")
    except:
        print(f"ERR {name} ({ticker})")

# 쿠콘 체크
print("\n=== 쿠콘 + 핵심 관련주 2/26 데이터 ===")
check = {"186230.KQ": "쿠콘", "234340.KS": "헥토파이낸셜", "214270.KQ": "FSN", "035720.KS": "카카오"}
for ticker, name in check.items():
    try:
        df = yf.download(ticker, start="2026-02-24", end="2026-02-28", auto_adjust=True, progress=False)
        if len(df) > 0:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df["pct"] = df["Close"].pct_change() * 100
            print(f"\n{name}:")
            print(df[["Open","High","Low","Close","Volume","pct"]].to_string())
    except Exception as e:
        print(f"{name}: {e}")

# 헥토파이낸셜 사업 내용 확인
print("\n=== 헥토파이낸셜 info ===")
try:
    info = yf.Ticker("234340.KS").info
    print(f"sector: {info.get('sector')}")
    print(f"industry: {info.get('industry')}")
    desc = info.get('longBusinessSummary', '')
    print(f"desc: {desc[:300]}")
except Exception as e:
    print(f"오류: {e}")
