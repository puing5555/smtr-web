
from pykrx import stock
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

KR_TICKERS = {
    "094480": "갤럭시아머니트리",
    "054920": "한컴위드",
    "041190": "우리기술투자",
    "121800": "비덴트",
    "112040": "위메이드",
    "251270": "넷마블",
    "036570": "엔씨소프트",
}

print("=" * 60)
print("한국 관련주 2/24 ~ 3/6 전체 데이터 (2/25 어닝 반응 포함)")
print("=" * 60)

for code, name in KR_TICKERS.items():
    try:
        df = stock.get_market_ohlcv_by_date("20260223", "20260307", code)
        if not df.empty:
            df["등락률"] = df["종가"].pct_change() * 100
            print(f"\n{name} ({code}):")
            print(df[["시가", "고가", "저가", "종가", "거래량", "등락률"]].to_string())
    except Exception as e:
        print(f"{name}: 오류 - {e}")

print("\n완료")
