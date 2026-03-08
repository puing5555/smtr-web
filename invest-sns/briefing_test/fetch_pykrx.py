import sys
import io
import json

# Python 3.14 UTF-8 mode 우회 (EUC-KR 인코딩 문제 해결)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pykrx import stock

result = {}

# KOSPI/KOSDAQ index OHLCV - iloc 사용 (컬럼명 인코딩 무관)
# 컬럼 순서: iloc[0]=시가, iloc[1]=고가, iloc[2]=저가, iloc[3]=종가, iloc[4]=거래량
try:
    kospi = stock.get_index_ohlcv_by_date("20250303", "20250307", "1001")
    print("KOSPI index OHLCV:")
    print(kospi)
    for idx in kospi.index:
        d = idx.strftime("%Y-%m-%d")
        row = kospi.loc[idx]
        if d not in result:
            result[d] = {}
        result[d]["KOSPI_pykrx"] = {
            "open":  float(row.iloc[0]),
            "high":  float(row.iloc[1]),
            "low":   float(row.iloc[2]),
            "close": float(row.iloc[3]),
        }
except Exception as e:
    print(f"KOSPI index error: {e}")

try:
    kosdaq = stock.get_index_ohlcv_by_date("20250303", "20250307", "2001")
    print("KOSDAQ index OHLCV:")
    print(kosdaq)
    for idx in kosdaq.index:
        d = idx.strftime("%Y-%m-%d")
        row = kosdaq.loc[idx]
        if d not in result:
            result[d] = {}
        result[d]["KOSDAQ_pykrx"] = {
            "open":  float(row.iloc[0]),
            "high":  float(row.iloc[1]),
            "low":   float(row.iloc[2]),
            "close": float(row.iloc[3]),
        }
except Exception as e:
    print(f"KOSDAQ index error: {e}")

# 투자자 수급 - iloc 사용 (행/컬럼 인코딩 무관)
# 행 순서: 개인(0), 기관합계(1), ..., 외국인합계(-2), 전체(-1)
# 순매수 = 마지막 컬럼 (iloc[:, -1])
for date_str in ["20250305", "20250306"]:
    try:
        df = stock.get_market_trading_value_by_investor(date_str, date_str, "KOSPI")
        print(f"\n수급 {date_str}:")
        print(df)
        d = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        if d not in result:
            result[d] = {}

        if not df.empty:
            net_col = df.iloc[:, -1]  # 순매수 컬럼 (마지막)
            inv_map = {
                "individual":  int(net_col.iloc[0]),   # 개인 (행 0)
                "institution": int(net_col.iloc[1]),   # 기관합계 (행 1)
                "foreign":     int(net_col.iloc[-2]),  # 외국인합계 (행 -2, 마지막 전)
            }
            result[d]["investors"] = inv_map
            print(f"  수급 {d}: {inv_map}")
        else:
            print(f"  수급 데이터 없음: {date_str}")
    except Exception as e:
        print(f"  투자자 수급 {date_str} error: {e}")

with open("pykrx_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSaved to pykrx_data.json")
