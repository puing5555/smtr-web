
import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("CRCL 이번 주 일별 데이터 수집")
print("=" * 60)

# CRCL 일별 데이터
crcl = yf.download("CRCL", start="2026-02-24", end="2026-03-08", interval="1d", auto_adjust=True, progress=False)
print(crcl)

# 등락률 계산
if not crcl.empty:
    crcl_df = crcl.copy()
    # Handle MultiIndex columns
    if isinstance(crcl_df.columns, pd.MultiIndex):
        crcl_df.columns = crcl_df.columns.get_level_values(0)
    
    crcl_df["Change%"] = crcl_df["Close"].pct_change() * 100
    print("\n일별 데이터 (등락률 포함):")
    print(crcl_df[["Open", "High", "Low", "Close", "Volume", "Change%"]].to_string())
    
    # 급등일 찾기
    surge_days = crcl_df[crcl_df["Change%"] >= 5]
    print(f"\n급등일(+5% 이상): {surge_days.index.tolist()}")

print("\n" + "=" * 60)
print("CRCL 1시간봉 데이터 (이번 주)")
print("=" * 60)
crcl_1h = yf.download("CRCL", start="2026-03-03", end="2026-03-08", interval="1h", auto_adjust=True, prepost=True, progress=False)
if not crcl_1h.empty:
    if isinstance(crcl_1h.columns, pd.MultiIndex):
        crcl_1h.columns = crcl_1h.columns.get_level_values(0)
    print(crcl_1h[["Open", "High", "Low", "Close", "Volume"]].to_string())

print("\n" + "=" * 60)
print("CRCL 회사 정보 & 뉴스")
print("=" * 60)
crcl_ticker = yf.Ticker("CRCL")

try:
    info = crcl_ticker.info
    print("Sector:", info.get("sector"))
    print("Industry:", info.get("industry"))
    print("Description:", info.get("longBusinessSummary", "")[:300])
    print("Market Cap:", info.get("marketCap"))
    print("52W High:", info.get("fiftyTwoWeekHigh"))
    print("52W Low:", info.get("fiftyTwoWeekLow"))
except Exception as e:
    print(f"Info error: {e}")

print("\n--- 실적 데이터 ---")
try:
    earnings = crcl_ticker.earnings_dates
    print(earnings)
except Exception as e:
    print(f"Earnings error: {e}")

print("\n--- 뉴스 ---")
try:
    news = crcl_ticker.news
    for n in news[:10]:
        title = n.get("title", "")
        ts = n.get("providerPublishTime", "")
        link = n.get("link", "")
        if ts:
            import datetime
            dt = datetime.datetime.fromtimestamp(ts)
            print(f"[{dt.strftime('%Y-%m-%d %H:%M')}] {title}")
            print(f"  {link}")
        else:
            print(f"{title}\n  {link}")
except Exception as e:
    print(f"News error: {e}")

print("\n" + "=" * 60)
print("한국 관련주 데이터 (pykrx)")
print("=" * 60)

KR_TICKERS = {
    "094480": "갤럭시아머니트리",
    "054920": "한컴위드",
    "041190": "우리기술투자",
    "121800": "비덴트",
    "377330": "카카오페이",
    "251270": "넷마블",
    "112040": "위메이드",
    "036570": "엔씨소프트",
    "024120": "서울옥션블루",
}

try:
    from pykrx import stock
    
    results = {}
    for code, name in KR_TICKERS.items():
        try:
            df = stock.get_market_ohlcv_by_date("20260303", "20260307", code)
            if not df.empty:
                df["등락률"] = df["종가"].pct_change() * 100
                print(f"\n{name} ({code}):")
                print(df[["시가", "고가", "저가", "종가", "거래량", "등락률"]].to_string())
                results[code] = df
            else:
                print(f"\n{name} ({code}): 데이터 없음")
        except Exception as e:
            print(f"\n{name} ({code}): 오류 - {e}")
    
    # 매매 시뮬레이션 - 금요일(3/6) 시가→종가
    print("\n" + "=" * 60)
    print("매매 시뮬레이션: 3/6(금) 시가 매수 → 종가 매도")
    print("=" * 60)
    
    sim_results = []
    for code, name in KR_TICKERS.items():
        if code in results:
            df = results[code]
            # 3/6 데이터 찾기
            friday_rows = [idx for idx in df.index if str(idx).startswith("2026-03-06")]
            if friday_rows:
                row = df.loc[friday_rows[0]]
                buy = row["시가"]
                sell = row["종가"]
                ret = (sell - buy) / buy * 100 if buy > 0 else 0
                sim_results.append({
                    "종목": name,
                    "시가": buy,
                    "종가": sell,
                    "수익률": ret
                })
                print(f"{name}: 시가 {buy:,}원 → 종가 {sell:,}원 = {ret:+.2f}%")
            else:
                # 목요일(3/5) 또는 다른 날 데이터 보기
                print(f"{name}: 3/6 데이터 없음 (가용 날짜: {list(df.index)})")
    
    if sim_results:
        avg_ret = sum(r["수익률"] for r in sim_results) / len(sim_results)
        print(f"\n평균 수익률: {avg_ret:+.2f}%")

except ImportError:
    print("pykrx 없음, yfinance 폴백 사용")
    kr_tickers_yf = {
        "094480.KS": "갤럭시아머니트리",
        "054920.KS": "한컴위드",
        "041190.KS": "우리기술투자",
        "121800.KS": "비덴트",
        "112040.KS": "위메이드",
    }
    for ticker, name in kr_tickers_yf.items():
        df = yf.download(ticker, start="2026-03-03", end="2026-03-08", auto_adjust=True, progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df["Change%"] = df["Close"].pct_change() * 100
            print(f"\n{name}:")
            print(df[["Open", "High", "Low", "Close", "Volume", "Change%"]].to_string())

print("\n분석 완료")
