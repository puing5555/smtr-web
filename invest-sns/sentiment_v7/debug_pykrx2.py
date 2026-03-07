from pykrx.website import krx
import pandas as pd

# 직접 API 호출 테스트
try:
    df = krx.get_market_trading_value_and_volume_on_market_by_investor(
        '20260220', '20260306', 'KOSPI'
    )
    print('타입:', type(df))
    print('컬럼:', df.columns.tolist() if df is not None else None)
    if df is not None:
        print(df.head(3))
except Exception as e:
    print('오류:', e)
    import traceback; traceback.print_exc()

print()
# get_market_ohlcv_by_ticker 하위 함수
try:
    df2 = krx.get_market_ohlcv_by_ticker('20260306', 'KOSPI')
    print('ohlcv 타입:', type(df2))
    if df2 is not None:
        print('ohlcv 컬럼:', df2.columns.tolist())
        print(df2.head(3))
except Exception as e:
    print('ohlcv 오류:', e)
    import traceback; traceback.print_exc()

print()
# IndexTicker 테스트
try:
    from pykrx.website.krx.market import ticker as ticker_mod
    t = ticker_mod.IndexTicker()
    print('IndexTicker df columns:', t.df.columns.tolist() if t.df is not None else None)
    print(t.df.head())
except Exception as e:
    print('IndexTicker 오류:', e)
    import traceback; traceback.print_exc()
