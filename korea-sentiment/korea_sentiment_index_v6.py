"""
=============================================================
투자SNS 한국 시장 심리 지수 v6 (Korea Market Sentiment Index)
=============================================================

v5 → v6 변경사항:
  ❌ 삭제: i07 풋/콜 proxy (ETF 거래량 비율로 풋콜 측정 불가)
  🔧 수정: i02 주가강도 — 52주(252일) → 60일 고저 위치 (단기 랠리 반영)
  🔧 수정: i01 모멘텀 — 125일 MA → 50일 MA (반응속도 2.5배 향상)
  ✅ 유지: 나머지 7개 지표 동일

9개 지표 (각 11.1% = 1/9):
#  지표              데이터 소스              가중치
1  모멘텀 (50일MA)  ^KS11 vs 50일 MA         11.1%  [수정]
2  주가강도 (60일)  ^KS11 60일 hi/lo 위치    11.1%  [수정]
3  시장폭 RSI       ^KS11 Wilder RSI          11.1%
4  변동성           ^KS11 역사적변동성+방향   11.1%
5  안전자산수요     ^KS11 vs 국고채ETF        11.1%
6  크레딧 스프레드  국고채 vs 주식ETF 괴리    11.1%
7  외국인수급proxy  USD/KRW 역방향            11.1%
8  거래대금         ^KS11 Volume 5일/20일     11.1%
9  코스닥/코스피    ^KQ11/^KS11 상대강도      11.1%

정규화: expanding Z-score CDF
스무딩: 5일 이동평균
=============================================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy.stats import norm
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 1. 데이터 수집
# ============================================================

def fetch_data(period="10y"):
    tickers = {
        'kospi':    '^KS11',
        'kosdaq':   '^KQ11',
        'bond10y':  '114820.KS',
        'kodex200': '069500.KS',
        'usdkrw':   'KRW=X',
    }
    data = {}
    for key, ticker in tickers.items():
        print(f"  {key} ({ticker})...")
        try:
            d = yf.download(ticker, period=period, auto_adjust=True, progress=False)
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.droplevel(1)
            data[key] = d
            print(f"    → {len(d)}일")
        except Exception as e:
            print(f"    → ERROR: {e}")
            data[key] = pd.DataFrame()
    return data


# ============================================================
# 2. 정규화 (expanding Z-score CDF)
# ============================================================

def expanding_zscore_cdf(series, min_periods=60):
    mu  = series.expanding(min_periods=min_periods).mean()
    sig = series.expanding(min_periods=min_periods).std()
    z   = (series - mu) / (sig + 1e-9)
    cdf = pd.Series(norm.cdf(z), index=series.index) * 100
    return cdf.clip(0, 100)


# ============================================================
# 3. 9개 지표 계산
# ============================================================

def i01_momentum(data):
    """지표 1: 시장 모멘텀 — KOSPI vs 50일 MA (v6: 125→50일)"""
    close = data['kospi']['Close']
    ma50  = close.rolling(50).mean()
    dev   = (close - ma50) / ma50 * 100
    return expanding_zscore_cdf(dev).rename("i01_momentum")


def i02_price_strength(data):
    """지표 2: 주가 강도 — 60일 hi/lo 위치 (v6: 252→60일)"""
    close  = data['kospi']['Close']
    hi_60d = close.rolling(60).max()
    lo_60d = close.rolling(60).min()
    pos    = (close - lo_60d) / (hi_60d - lo_60d + 1e-9) * 100
    return expanding_zscore_cdf(pos).rename("i02_price_strength")


def i03_breadth_rsi(data):
    """지표 3: 시장폭 — Wilder RSI (14일)"""
    close = data['kospi']['Close']
    delta = close.diff()
    gain  = delta.where(delta > 0, 0.0)
    loss  = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rsi = 100 - (100 / (1 + avg_gain / (avg_loss + 1e-9)))
    return rsi.clip(0, 100).rename("i03_breadth_rsi")


def i04_volatility(data, lookback=20):
    """지표 4: 변동성 — 역변환(변동성)*0.5 + 방향(20일수익률)*0.5"""
    close = data['kospi']['Close']
    ret   = close.pct_change()
    vol   = ret.rolling(lookback).std() * np.sqrt(252) * 100
    inv_vol    = 100 - expanding_zscore_cdf(vol)
    ret20      = close.pct_change(lookback) * 100
    dir_score  = expanding_zscore_cdf(ret20)
    return (inv_vol * 0.5 + dir_score * 0.5).clip(0, 100).rename("i04_volatility")


def i05_safe_haven(data):
    """지표 5: 안전자산 수요 — KOSPI vs 국고채ETF 20일 수익률 스프레드"""
    kospi_close = data['kospi']['Close']
    bond_close  = data['bond10y']['Close']

    if bond_close.empty:
        print("    [i05] 국고채 ETF 없음, 모멘텀 대용")
        ret20 = kospi_close.pct_change(20) * 100
        return expanding_zscore_cdf(ret20).rename("i05_safe_haven")

    idx = kospi_close.index.intersection(bond_close.index)
    spread = (kospi_close.loc[idx].pct_change(20) - bond_close.loc[idx].pct_change(20)) * 100
    return expanding_zscore_cdf(spread).reindex(kospi_close.index).rename("i05_safe_haven")


def i06_credit_spread(data):
    """지표 6: 크레딧 스프레드 — KODEX200 vs 국고채ETF 상대 모멘텀"""
    k200  = data['kodex200']['Close']
    bond  = data['bond10y']['Close']

    if k200.empty or bond.empty:
        print("    [i06] ETF 없음, 주가강도 대용")
        return i02_price_strength(data).rename("i06_credit_spread")

    idx = k200.index.intersection(bond.index)
    k200_mom = (k200.loc[idx] - k200.loc[idx].rolling(20).mean()) / k200.loc[idx].rolling(20).mean() * 100
    bond_mom = (bond.loc[idx] - bond.loc[idx].rolling(20).mean()) / bond.loc[idx].rolling(20).mean() * 100
    spread = k200_mom - bond_mom
    return expanding_zscore_cdf(spread).reindex(data['kospi']['Close'].index).rename("i06_credit_spread")


def i07_foreign_flow(data):
    """지표 7: 외국인수급 proxy — USD/KRW 역방향 (원화강세=탐욕)"""
    usdkrw = data['usdkrw']['Close']
    kospi  = data['kospi']['Close']

    if usdkrw.empty:
        print("    [i07] USD/KRW 없음, 모멘텀 대용")
        return i01_momentum(data).rename("i07_foreign_flow")

    idx = usdkrw.index.intersection(kospi.index)
    inv_usd = -usdkrw.loc[idx].pct_change(20) * 100
    return expanding_zscore_cdf(inv_usd).reindex(kospi.index).rename("i07_foreign_flow")


def i08_trading_volume(data):
    """지표 8: 거래대금 — 5일/20일 거래량 비율 + 패닉셀 보정"""
    vol   = data['kospi']['Volume']
    close = data['kospi']['Close']
    v5    = vol.rolling(5).mean()
    v20   = vol.rolling(20).mean()
    ratio = (v5 / (v20 + 1e-9))
    base  = expanding_zscore_cdf((ratio - 1) * 100)
    panic = (close.pct_change(5) < -0.03) & (ratio > 1.3)
    base[panic] = 100 - base[panic]
    return base.clip(0, 100).rename("i08_trading_volume")


def i09_kosdaq_kospi(data):
    """지표 9: 코스닥/코스피 상대강도 — 투기심리 바로미터"""
    kospi  = data['kospi']['Close']
    kosdaq = data['kosdaq']['Close']
    idx    = kospi.index.intersection(kosdaq.index)
    ratio  = kosdaq.loc[idx] / kospi.loc[idx]
    dev    = (ratio - ratio.rolling(60).mean()) / ratio.rolling(60).mean() * 100
    return expanding_zscore_cdf(dev).reindex(kospi.index).rename("i09_kosdaq_kospi")


# ============================================================
# 4. 최종 합산 (9개 균등 11.1%)
# ============================================================

def calculate_v6(data):
    print("  지표 1: 모멘텀 (50일MA)...")
    s1 = i01_momentum(data)
    print("  지표 2: 주가강도 (60일)...")
    s2 = i02_price_strength(data)
    print("  지표 3: 시장폭 RSI...")
    s3 = i03_breadth_rsi(data)
    print("  지표 4: 변동성...")
    s4 = i04_volatility(data)
    print("  지표 5: 안전자산수요...")
    s5 = i05_safe_haven(data)
    print("  지표 6: 크레딧 스프레드...")
    s6 = i06_credit_spread(data)
    print("  지표 7: 외국인수급 proxy...")
    s7 = i07_foreign_flow(data)
    print("  지표 8: 거래대금...")
    s8 = i08_trading_volume(data)
    print("  지표 9: 코스닥/코스피...")
    s9 = i09_kosdaq_kospi(data)

    df = pd.DataFrame({
        'i01_momentum':       s1,
        'i02_price_strength': s2,
        'i03_breadth_rsi':    s3,
        'i04_volatility':     s4,
        'i05_safe_haven':     s5,
        'i06_credit_spread':  s6,
        'i07_foreign_flow':   s7,
        'i08_trading_volume': s8,
        'i09_kosdaq_kospi':   s9,
    })

    # 9개 균등 평균 (각 1/9 = 11.1%)
    raw = df.mean(axis=1)
    df['sentiment_raw']   = raw.round(1)
    df['sentiment_index'] = raw.rolling(5, min_periods=1).mean().round(1)

    def grade(x):
        if pd.isna(x):  return "N/A"
        if x <= 20:     return "극도의 공포"
        elif x <= 40:   return "공포"
        elif x <= 60:   return "중립"
        elif x <= 80:   return "탐욕"
        else:           return "극도의 탐욕"

    df['grade'] = df['sentiment_index'].apply(grade)
    return df


# ============================================================
# 5. 2025년 1~2월 구간 진단 출력
# ============================================================

def print_period_analysis(scores_df):
    mask = (scores_df.index >= "2025-01-01") & (scores_df.index <= "2025-02-28")
    period = scores_df[mask].copy()

    print("\n" + "=" * 100)
    print("📊 2025년 1~2월 지표별 일별 점수 (v6)")
    print("=" * 100)
    print(f"{'날짜':<12} {'모멘텀':>6} {'주가강':>6} {'RSI':>6} {'변동성':>6} {'안전자':>6} "
          f"{'크레딧':>6} {'외국인':>6} {'거래량':>6} {'코닥':>6} "
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
              f"{row['i07_foreign_flow']:>6.1f} "
              f"{row['i08_trading_volume']:>6.1f} "
              f"{row['i09_kosdaq_kospi']:>6.1f} "
              f"{row['sentiment_raw']:>6.1f} "
              f"{row['sentiment_index']:>6.1f} "
              f"{row['grade']}")

    print("\n" + "=" * 100)
    print("📊 구간 평균 & 범위 (v6 vs v5 비교)")
    print("=" * 100)
    ind_names = {
        'i01_momentum':       '모멘텀(50일)',
        'i02_price_strength': '주가강도(60일)',
        'i03_breadth_rsi':    '시장폭RSI',
        'i04_volatility':     '변동성',
        'i05_safe_haven':     '안전자산수요',
        'i06_credit_spread':  '크레딧스프레드',
        'i07_foreign_flow':   '외국인수급',
        'i08_trading_volume': '거래대금',
        'i09_kosdaq_kospi':   '코스닥/코스피',
    }
    v5_avg = {
        'i01_momentum': 41.6, 'i02_price_strength': 25.5,  # v5 기준
    }
    print(f"\n{'지표':<18} {'평균':>7} {'최소':>7} {'최대':>7} {'중앙값':>7}  판정")
    print("-" * 65)
    for col, name in ind_names.items():
        avg = period[col].mean()
        mn  = period[col].min()
        mx  = period[col].max()
        med = period[col].median()
        verdict = "🔴 발목" if avg < 50 else ("🟡 중립" if avg < 65 else "🟢 상승")
        print(f"{name:<18} {avg:>7.1f} {mn:>7.1f} {mx:>7.1f} {med:>7.1f}  {verdict}")

    print(f"\n{'종합(RAW)':<18} {period['sentiment_raw'].mean():>7.1f} "
          f"{period['sentiment_raw'].min():>7.1f} {period['sentiment_raw'].max():>7.1f}")
    print(f"{'종합(스무딩)':<18} {period['sentiment_index'].mean():>7.1f} "
          f"{period['sentiment_index'].min():>7.1f} {period['sentiment_index'].max():>7.1f}")
    print(f"\n  v5 기준 최고점: 63.3 (2025-02-18) → v6 최고점: {period['sentiment_index'].max():.1f} ({period['sentiment_index'].idxmax().strftime('%Y-%m-%d')})")
    print(f"  극도의 탐욕(80+) 달성일수: {(period['sentiment_index'] >= 80).sum()}일")
    print(f"  탐욕(60+) 달성일수: {(period['sentiment_index'] >= 60).sum()}일")


# ============================================================
# 6. 백테스트
# ============================================================

def backtest(kospi_df, scores_df):
    merged = scores_df.copy()
    merged['close']      = kospi_df['Close']
    merged['return_20d'] = kospi_df['Close'].pct_change(20).shift(-20) * 100
    merged['return_60d'] = kospi_df['Close'].pct_change(60).shift(-60) * 100
    merged = merged.dropna(subset=['sentiment_index', 'return_20d'])

    bins   = [0, 20, 40, 60, 80, 100]
    labels = ['극도의 공포(0-20)', '공포(20-40)', '중립(40-60)', '탐욕(60-80)', '극도의 탐욕(80-100)']
    merged['zone'] = pd.cut(merged['sentiment_index'], bins=bins, labels=labels, include_lowest=True)

    print("\n" + "=" * 72)
    print("📊 [v6] 한국 시장 심리 지수 — 10년 백테스트 결과")
    print("    (9개 지표 균등 11.1% / Z-score CDF 정규화 / 5일 스무딩)")
    print("=" * 72)

    print("\n📊 구간별 향후 수익률 (20일 후)")
    print("-" * 55)
    result_20d = merged.groupby('zone', observed=True)['return_20d'].agg(['mean', 'median', 'count', 'std'])
    result_20d.columns = ['평균수익률(%)', '중앙값(%)', '데이터수', '표준편차(%)']
    print(result_20d.round(2).to_string())

    print("\n📊 구간별 향후 수익률 (60일 후)")
    print("-" * 55)
    merged_60 = merged.dropna(subset=['return_60d'])
    result_60d = merged_60.groupby('zone', observed=True)['return_60d'].agg(['mean', 'median', 'count', 'std'])
    result_60d.columns = ['평균수익률(%)', '중앙값(%)', '데이터수', '표준편차(%)']
    print(result_60d.round(2).to_string())

    print("\n📊 구간별 수익 확률 (20일 후)")
    print("-" * 55)
    for zone in labels:
        d = merged[merged['zone'] == zone]['return_20d']
        if len(d) > 0:
            wr = (d > 0).sum() / len(d) * 100
            print(f"  {zone}: {wr:.1f}% ({len(d)}건)")

    print("\n" + "=" * 72)
    print("🎯 핵심: '공포에 사서 탐욕에 팔라'")
    print("=" * 72)
    fear    = merged[merged['sentiment_index'] <= 30]['return_20d']
    neutral = merged[(merged['sentiment_index'] > 30) & (merged['sentiment_index'] < 70)]['return_20d']
    greed   = merged[merged['sentiment_index'] >= 70]['return_20d']

    print(f"  공포(≤30)  → 20일 후 평균: {fear.mean():.2f}%  (승률: {(fear>0).mean()*100:.1f}%, {len(fear)}건)")
    print(f"  중립(30-70)→ 20일 후 평균: {neutral.mean():.2f}%  (승률: {(neutral>0).mean()*100:.1f}%, {len(neutral)}건)")
    print(f"  탐욕(≥70)  → 20일 후 평균: {greed.mean():.2f}%  (승률: {(greed>0).mean()*100:.1f}%, {len(greed)}건)")

    corr_20 = merged['sentiment_index'].corr(merged['return_20d'])
    corr_60 = merged['sentiment_index'].corr(merged['return_60d'].dropna())
    print(f"\n  심리지수 vs 20일후 수익률 상관계수: {corr_20:.3f}")
    print(f"  심리지수 vs 60일후 수익률 상관계수: {corr_60:.3f}")
    print(f"  (음수 = 역발상 지표 정상 작동)")

    return merged, result_20d


# ============================================================
# 7. 차트 (5 패널)
# ============================================================

def plot_charts(kospi_df, scores_df, merged_df):
    last_val   = scores_df['sentiment_index'].dropna().iloc[-1]
    raw_val    = scores_df['sentiment_raw'].dropna().iloc[-1]
    last_date  = scores_df['sentiment_index'].dropna().index[-1]

    def _grade(x):
        if x <= 20:  return "극도의 공포"
        elif x <= 40: return "공포"
        elif x <= 60: return "중립"
        elif x <= 80: return "탐욕"
        else:         return "극도의 탐욕"
    grade = _grade(last_val)

    COLORS = {
        'bg': '#0d0d0d', 'panel': '#1a1a2e',
        'line': '#00d4ff', 'raw': '#4488aa',
        'white': '#ffffff', 'grid': '#333333',
    }

    fig = plt.figure(figsize=(20, 32))
    fig.patch.set_facecolor(COLORS['bg'])
    gs = fig.add_gridspec(5, 1, hspace=0.45, top=0.96, bottom=0.04)

    def style_ax(ax, title, ylabel):
        ax.set_facecolor(COLORS['panel'])
        ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=8)
        ax.set_ylabel(ylabel, color='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=8)
        for sp in ['bottom', 'left']:  ax.spines[sp].set_color('#444')
        for sp in ['top', 'right']:    ax.spines[sp].set_visible(False)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.grid(color=COLORS['grid'], linewidth=0.5, alpha=0.5)

    def bg_bands(ax):
        for lo, hi, col in [(0,20,'#ff4444'), (20,40,'#ff8c00'),
                             (40,60,'#888888'), (60,80,'#00cc66'), (80,100,'#00ff88')]:
            ax.axhspan(lo, hi, alpha=0.12, color=col)

    # ── Chart 1: 10년 추이 ──
    ax1 = fig.add_subplot(gs[0])
    style_ax(ax1, f'한국 시장 심리 지수 v6 — 10년 추이 | 현재: {last_val:.0f}점 ({grade})', '심리 지수')
    bg_bands(ax1)
    idx  = scores_df.index
    sent = scores_df['sentiment_index']
    sent_raw = scores_df['sentiment_raw']
    ax1.plot(idx, sent_raw, color=COLORS['raw'], lw=0.6, alpha=0.45, label='RAW')
    ax1.plot(idx, sent,     color=COLORS['line'], lw=1.5, alpha=0.95, zorder=5, label='5일 스무딩')
    for lo, hi, col in [(0,20,'#ff4444'), (20,40,'#ff8c00'), (40,60,'#aaaaaa'),
                        (60,80,'#00cc66'), (80,100,'#00ff88')]:
        ax1.fill_between(idx, lo, sent, where=(sent>=lo)&(sent<hi), alpha=0.22, color=col, zorder=4)
    for y, c, ls in [(20,'#ff6666','--'), (40,'#ffaa44',':'), (60,'#888',':'), (80,'#44ff88','--')]:
        ax1.axhline(y=y, color=c, ls=ls, lw=0.7, alpha=0.55)
    ax1.annotate(
        f'현재: {last_val:.0f} (RAW: {raw_val:.0f})',
        xy=(last_date, last_val), xytext=(-90, 20), textcoords='offset points',
        color='white', fontsize=11, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='white', lw=1.5)
    )
    ax1.set_xlim(idx[0], idx[-1]); ax1.set_ylim(0, 100)
    legend_patches = [
        mpatches.Patch(color='#ff4444', alpha=0.6, label='극도의 공포 (0-20)'),
        mpatches.Patch(color='#ff8c00', alpha=0.6, label='공포 (20-40)'),
        mpatches.Patch(color='#aaaaaa', alpha=0.6, label='중립 (40-60)'),
        mpatches.Patch(color='#00cc66', alpha=0.6, label='탐욕 (60-80)'),
        mpatches.Patch(color='#00ff88', alpha=0.6, label='극도의 탐욕 (80-100)'),
        Line2D([0],[0], color=COLORS['line'], lw=2, label='5일 스무딩'),
        Line2D([0],[0], color=COLORS['raw'], lw=1, alpha=0.5, label='RAW'),
    ]
    ax1.legend(handles=legend_patches, loc='upper left', fontsize=7.5,
               facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', ncol=4)

    # ── Chart 2: 코스피 오버레이 ──
    ax2 = fig.add_subplot(gs[1])
    style_ax(ax2, '코스피 지수 오버레이 (빨강=공포≤30 / 녹색=탐욕≥70)', '코스피')
    comm = kospi_df.index.intersection(scores_df.index)
    cls  = kospi_df.loc[comm, 'Close']
    sc   = scores_df.loc[comm, 'sentiment_index']
    ylo, yhi = cls.min()*0.95, cls.max()*1.05
    ax2.plot(comm, cls, color='#ddd', lw=0.9, alpha=0.85, zorder=3)
    ax2.fill_between(comm, ylo, yhi, where=(sc<=30), alpha=0.22, color='#ff4444', zorder=2, label='공포(≤30)')
    ax2.fill_between(comm, ylo, yhi, where=(sc>=70), alpha=0.22, color='#00ff88', zorder=2, label='탐욕(≥70)')
    ax2.set_xlim(comm[0], comm[-1])
    ax2.legend(loc='upper left', fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())

    # ── Chart 3: 9개 지표 추이 ──
    ax3 = fig.add_subplot(gs[2])
    style_ax(ax3, '9개 지표 개별 추이 (각 11.1%) — v6: 풋/콜 삭제, 모멘텀 50일, 주가강도 60일', '지표 점수 (0-100)')
    ind_map = {
        'i01_momentum':       ('#ffd93d', '모멘텀(50일)'),
        'i02_price_strength': ('#6bcb77', '주가강도(60일)'),
        'i03_breadth_rsi':    ('#ff922b', '시장폭RSI'),
        'i04_volatility':     ('#ff6b6b', '변동성'),
        'i05_safe_haven':     ('#4d96ff', '안전자산수요'),
        'i06_credit_spread':  ('#f06595', '크레딧스프레드'),
        'i07_foreign_flow':   ('#74c0fc', '외국인수급'),
        'i08_trading_volume': ('#cc5de8', '거래대금'),
        'i09_kosdaq_kospi':   ('#20c997', '코스닥/코스피'),
    }
    for col, (clr, lbl) in ind_map.items():
        if col in scores_df.columns:
            ax3.plot(scores_df.index, scores_df[col], color=clr, lw=0.75, alpha=0.8, label=lbl)
    ax3.axhline(y=50, color='#666', ls='--', lw=0.8, alpha=0.6)
    ax3.set_xlim(scores_df.index[0], scores_df.index[-1]); ax3.set_ylim(0, 100)
    ax3.legend(loc='upper left', fontsize=7.5, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', ncol=5)

    # ── Chart 4: 백테스트 바차트 ──
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor(COLORS['panel'])
    ax4.set_title('심리 구간별 향후 수익률 (20일 / 60일)', color='white', fontsize=12, fontweight='bold', pad=8)
    if merged_df is not None and 'zone' in merged_df.columns:
        zlabels_orig = ['극도의 공포(0-20)', '공포(20-40)', '중립(40-60)', '탐욕(60-80)', '극도의 탐욕(80-100)']
        zlabels_disp = ['극도의 공포\n(0-20)', '공포\n(20-40)', '중립\n(40-60)', '탐욕\n(60-80)', '극도의 탐욕\n(80-100)']
        m20, m60, ns = [], [], []
        for z in zlabels_orig:
            d20 = merged_df[merged_df['zone']==z]['return_20d'].dropna()
            d60 = merged_df[merged_df['zone']==z]['return_60d'].dropna()
            m20.append(d20.mean() if len(d20)>0 else 0)
            m60.append(d60.mean() if len(d60)>0 else 0)
            ns.append(len(d20))
        x = np.arange(len(zlabels_disp)); w = 0.35
        c20 = ['#ff4444' if v<0 else '#00cc66' for v in m20]
        c60 = ['#ff7777' if v<0 else '#44ff88' for v in m60]
        b1 = ax4.bar(x-w/2, m20, w, label='20일 후', color=c20, alpha=0.85, zorder=3)
        b2 = ax4.bar(x+w/2, m60, w, label='60일 후', color=c60, alpha=0.65, zorder=3)
        ax4.bar_label(b1, fmt='%.1f%%', color='white', fontsize=9, padding=3)
        ax4.bar_label(b2, fmt='%.1f%%', color='#ddd', fontsize=9, padding=3)
        for i, n in enumerate(ns):
            ax4.text(x[i], min(m20[i], m60[i], 0)-0.3, f'n={n}',
                     ha='center', va='top', color='#aaa', fontsize=8)
        ax4.axhline(y=0, color='white', lw=0.8, alpha=0.5)
        ax4.set_xticks(x); ax4.set_xticklabels(zlabels_disp, color='white', fontsize=9)
        ax4.set_ylabel('평균 수익률 (%)', color='white', fontsize=10)
        ax4.tick_params(colors='white')
        for sp in ['bottom','left']:  ax4.spines[sp].set_color('#444')
        for sp in ['top','right']:    ax4.spines[sp].set_visible(False)
        ax4.grid(axis='y', color='#333', lw=0.5, alpha=0.5)
        ax4.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    # ── Chart 5: 최근 60일 확대 ──
    ax5 = fig.add_subplot(gs[4])
    style_ax(ax5, f'최근 60일 확대 — 현재 {last_val:.0f}점 ({grade})', '심리 지수')
    bg_bands(ax5)
    r60 = scores_df.tail(60)
    ax5.plot(r60.index, r60['sentiment_raw'],   color=COLORS['raw'],  lw=1.0, alpha=0.55, label='RAW')
    ax5.plot(r60.index, r60['sentiment_index'], color=COLORS['line'], lw=2.2, alpha=0.95, zorder=5, label='5일 스무딩')
    for lo, hi, col in [(0,20,'#ff4444'), (20,40,'#ff8c00'), (40,60,'#aaaaaa'),
                        (60,80,'#00cc66'), (80,100,'#00ff88')]:
        ax5.fill_between(r60.index, lo, r60['sentiment_index'],
                         where=(r60['sentiment_index']>=lo)&(r60['sentiment_index']<hi),
                         alpha=0.28, color=col, zorder=4)
    for y, c, ls in [(20,'#ff6666','--'), (40,'#ffaa44',':'), (60,'#888',':'), (80,'#44ff88','--')]:
        ax5.axhline(y=y, color=c, ls=ls, lw=0.8, alpha=0.6)
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax5.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax5.get_xticklabels(), rotation=30, ha='right')
    ax5.set_xlim(r60.index[0], r60.index[-1]); ax5.set_ylim(0, 100)
    ax5.legend(loc='upper left', fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    plt.suptitle(
        f'한국 시장 심리 지수 v6  |  {last_date.strftime("%Y-%m-%d")} 기준  |'
        f'  현재: {last_val:.0f}점 → {grade}',
        color='white', fontsize=14, fontweight='bold', y=0.985
    )
    out = "C:/Users/Mario/work/korea-sentiment/korea_sentiment_v6_chart.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print(f"✅ 차트 저장: {out}")
    return out


# ============================================================
# 8. 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 68)
    print("한국 시장 심리 지수 v6")
    print("  수정: 모멘텀 125일→50일 / 주가강도 52주→60일 / 풋콜 삭제")
    print("  9개 지표 균등 11.1% / Z-score CDF / 5일 스무딩")
    print("=" * 68)

    print("\n[1] 데이터 다운로드...")
    data = fetch_data(period="10y")
    print(f"    코스피: {len(data['kospi'])}일 / 코스닥: {len(data['kosdaq'])}일")

    print("\n[2] 지표 계산...")
    scores = calculate_v6(data)
    csv_path = "C:/Users/Mario/work/korea-sentiment/korea_sentiment_v6.csv"
    scores.to_csv(csv_path)
    print(f"    CSV 저장: {csv_path}")

    # 최신 점수
    latest    = scores.dropna(subset=['sentiment_index']).iloc[-1]
    last_date = scores.dropna(subset=['sentiment_index']).index[-1]

    print(f"\n📈 최신 심리 지수 v6 [{last_date.strftime('%Y-%m-%d')}]")
    print(f"   ● 종합 (5일 스무딩): {latest['sentiment_index']:.1f} → {latest['grade']}")
    print(f"   ● RAW (당일):        {latest['sentiment_raw']:.1f}")
    print(f"   ──────────────────────────────────────────────")
    ind_labels = {
        'i01_momentum':       '모멘텀 (50일MA) [수정]',
        'i02_price_strength': '주가강도 (60일) [수정]',
        'i03_breadth_rsi':    '시장폭 RSI',
        'i04_volatility':     '변동성',
        'i05_safe_haven':     '안전자산수요',
        'i06_credit_spread':  '크레딧 스프레드',
        'i07_foreign_flow':   '외국인수급 proxy',
        'i08_trading_volume': '거래대금',
        'i09_kosdaq_kospi':   '코스닥/코스피',
    }
    for col, lbl in ind_labels.items():
        val = latest.get(col, float('nan'))
        print(f"   {lbl:35s}: {val:.1f}")

    print("\n[3] 2025년 1~2월 구간 분석...")
    print_period_analysis(scores)

    print("\n[4] 백테스트...")
    merged, result = backtest(data['kospi'], scores)

    print("\n[5] 차트 생성...")
    chart_path = plot_charts(data['kospi'], scores, merged)

    print("\n✅ 완료!")
    print(f"   CSV: {csv_path}")
    print(f"   차트: {chart_path}")
