"""v5 심리지수 진단 — 2025년 1~2월 지표별 점수 분석"""
import pandas as pd
import os

# CSV 로드
csv = r"C:\Users\Mario\work\korea-sentiment\korea_sentiment_v5.csv"
df = pd.read_csv(csv, index_col=0, parse_dates=True)

# 2025-01 ~ 2025-02 필터
mask = (df.index >= "2025-01-01") & (df.index <= "2025-02-28")
period = df[mask].copy()

cols = [
    'i01_momentum', 'i02_price_strength', 'i03_breadth_rsi',
    'i04_volatility', 'i05_safe_haven', 'i06_credit_spread',
    'i07_put_call_proxy', 'i08_foreign_flow', 'i09_trading_volume',
    'i10_kosdaq_kospi', 'sentiment_raw', 'sentiment_index', 'grade'
]
period = period[cols]

print("=" * 100)
print("2025년 1~2월 심리지수 v5 — 지표별 일별 점수")
print("=" * 100)
print(f"\n{'날짜':<12} {'모멘텀':>6} {'주가강':>6} {'RSI':>6} {'변동성':>6} {'안전자':>6} "
      f"{'크레딧':>6} {'풋콜':>6} {'외국인':>6} {'거래량':>6} {'코닥':>6} "
      f"{'RAW':>6} {'스무딩':>6} {'등급'}")
print("-" * 100)

for date, row in period.iterrows():
    print(f"{date.strftime('%Y-%m-%d'):<12} "
          f"{row['i01_momentum']:>6.1f} "
          f"{row['i02_price_strength']:>6.1f} "
          f"{row['i03_breadth_rsi']:>6.1f} "
          f"{row['i04_volatility']:>6.1f} "
          f"{row['i05_safe_haven']:>6.1f} "
          f"{row['i06_credit_spread']:>6.1f} "
          f"{row['i07_put_call_proxy']:>6.1f} "
          f"{row['i08_foreign_flow']:>6.1f} "
          f"{row['i09_trading_volume']:>6.1f} "
          f"{row['i10_kosdaq_kospi']:>6.1f} "
          f"{row['sentiment_raw']:>6.1f} "
          f"{row['sentiment_index']:>6.1f} "
          f"{row['grade']}")

print("\n" + "=" * 100)
print("📊 구간 평균 & 범위")
print("=" * 100)

ind_names = {
    'i01_momentum': '모멘텀',
    'i02_price_strength': '주가강도',
    'i03_breadth_rsi': '시장폭RSI',
    'i04_volatility': '변동성',
    'i05_safe_haven': '안전자산수요',
    'i06_credit_spread': '크레딧스프레드',
    'i07_put_call_proxy': '풋/콜proxy',
    'i08_foreign_flow': '외국인수급',
    'i09_trading_volume': '거래대금',
    'i10_kosdaq_kospi': '코스닥/코스피',
}

print(f"\n{'지표':<18} {'평균':>7} {'최소':>7} {'최대':>7} {'중앙값':>7}  판정")
print("-" * 65)

drag_list = []
for col, name in ind_names.items():
    avg = period[col].mean()
    mn  = period[col].min()
    mx  = period[col].max()
    med = period[col].median()
    verdict = "🔴 발목" if avg < 50 else ("🟡 중립" if avg < 65 else "🟢 상승")
    if avg < 50:
        drag_list.append((name, avg))
    print(f"{name:<18} {avg:>7.1f} {mn:>7.1f} {mx:>7.1f} {med:>7.1f}  {verdict}")

print(f"\n{'종합(RAW)':<18} {period['sentiment_raw'].mean():>7.1f} "
      f"{period['sentiment_raw'].min():>7.1f} {period['sentiment_raw'].max():>7.1f}")
print(f"{'종합(스무딩)':<18} {period['sentiment_index'].mean():>7.1f} "
      f"{period['sentiment_index'].min():>7.1f} {period['sentiment_index'].max():>7.1f}")

print("\n" + "=" * 100)
print("🚨 점수 끌어내리는 지표 (평균 < 50)")
print("=" * 100)
drag_list.sort(key=lambda x: x[1])
for name, avg in drag_list:
    print(f"  ❌ {name}: 평균 {avg:.1f}점 (50점 미달)")

# 각 지표별 하위 날짜 찾기
print("\n" + "=" * 100)
print("📉 랠리 기간 중 가장 낮은 날 TOP3 (각 지표)")
print("=" * 100)
for col, name in ind_names.items():
    worst = period[col].nsmallest(3)
    parts = [d.strftime("%m/%d") + "=" + f"{v:.0f}" for d, v in worst.items()]
    print(f"  {name}: {', '.join(parts)}")

# 코스피 수익률과 비교
print("\n" + "=" * 100)
print("📈 2025 1~2월 코스피 vs 심리지수 괴리")
print("=" * 100)
import yfinance as yf
kospi = yf.download("^KS11", start="2024-12-31", end="2025-03-01", auto_adjust=True, progress=False)
if hasattr(kospi.columns, 'droplevel'):
    kospi.columns = kospi.columns.droplevel(1)
kospi_period = kospi[mask].copy() if len(kospi[mask]) > 0 else kospi.loc["2025-01-01":"2025-02-28"]

if len(kospi_period) > 0:
    start_price = kospi_period['Close'].iloc[0]
    end_price   = kospi_period['Close'].iloc[-1]
    peak_price  = kospi_period['Close'].max()
    print(f"  코스피 시작: {start_price:,.0f} → 종료: {end_price:,.0f} → 최고: {peak_price:,.0f}")
    print(f"  구간 수익률: {(end_price/start_price-1)*100:+.1f}%  /  최고점 대비: {(peak_price/start_price-1)*100:+.1f}%")
    print(f"  심리지수 평균: {period['sentiment_index'].mean():.1f}점 (랠리 기간 중 탐욕 찍은 날: "
          f"{(period['sentiment_index'] >= 70).sum()}일)")
