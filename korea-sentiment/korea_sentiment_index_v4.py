"""
=============================================================
투자SNS 한국 시장 심리 지수 v4 (Korea Market Sentiment Index)
=============================================================

변경사항 (v4 vs v2):
1. 변동성 지표 재설계: 방향 보정 추가
   - 변동성 점수 = 역변환점수 * 0.5 + 방향보정 * 0.5
   - 방향보정 = 코스피 20일 수익률 0~100 정규화
   - 저변동+상승=탐욕(70~80) / 저변동+하락=위험(30~40) /
     고변동+하락=공포(0~20) / 고변동+상승=과열(60~70)
2. RSI → Wilder RSI (ewm alpha=1/14, min_periods=14)
3. 가중치 조정:
   - 변동성: 20% → 10% (신뢰도↓)
   - 모멘텀: 20% → 25% (신뢰도 최상)
   - 주가강도: 20% → 20% (유지)
   - 거래대금: 15% → 15% (유지)
   - 시장폭RSI: 15% → 15% (유지)
   - 코스닥/코스피(안전자산수요): 10% → 15%
4. 스무딩: 5일 이동평균 적용 (raw + smoothed 둘 다 저장)

0 = 극도의 공포 | 25 = 공포 | 50 = 중립 | 75 = 탐욕 | 100 = 극도의 탐욕
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
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 1. 데이터 수집
# ============================================================

def fetch_data(period="10y"):
    """한국 시장 데이터 수집 (Yahoo Finance 기반)"""
    print("  코스피 다운로드...")
    kospi = yf.download("^KS11", period=period, auto_adjust=True, progress=False)
    print("  코스닥 다운로드...")
    kosdaq = yf.download("^KQ11", period=period, auto_adjust=True, progress=False)

    if isinstance(kospi.columns, pd.MultiIndex):
        kospi.columns = kospi.columns.droplevel(1)
    if isinstance(kosdaq.columns, pd.MultiIndex):
        kosdaq.columns = kosdaq.columns.droplevel(1)

    return kospi, kosdaq


# ============================================================
# 2. 6개 지표 계산
# ============================================================

def calc_indicator_1_volatility(kospi_df, lookback=20):
    """
    지표 1: 변동성 지수 (v4 — 방향 보정 추가)
    ─────────────────────────────────────────
    변동성 점수 = 역변환점수 * 0.5 + 방향보정 * 0.5

    역변환점수: 변동성 높을수록 0(공포), 낮을수록 100(탐욕)
    방향보정: 코스피 20일 수익률 → expanding 정규화 → 0~100
    
    결과:
    - 저변동 + 상승 = 탐욕 (70~80점)
    - 저변동 + 하락 = 위험 (30~40점)
    - 고변동 + 하락 = 공포 (0~20점)
    - 고변동 + 상승 = 과열 (60~70점)
    """
    returns = kospi_df['Close'].pct_change()
    vol_20d = returns.rolling(lookback).std() * np.sqrt(252) * 100

    # 역변환 점수 (변동성 낮을수록 높은 점수)
    vol_min = vol_20d.expanding(min_periods=60).min()
    vol_max = vol_20d.expanding(min_periods=60).max()
    inv_vol_score = 100 - ((vol_20d - vol_min) / (vol_max - vol_min) * 100)
    inv_vol_score = inv_vol_score.clip(0, 100)

    # 방향 보정: 20일 수익률 → expanding 정규화
    ret_20d = kospi_df['Close'].pct_change(lookback) * 100
    ret_min = ret_20d.expanding(min_periods=60).min()
    ret_max = ret_20d.expanding(min_periods=60).max()
    direction_score = (ret_20d - ret_min) / (ret_max - ret_min) * 100
    direction_score = direction_score.clip(0, 100)

    # 최종 결합: 0.5 / 0.5
    score = inv_vol_score * 0.5 + direction_score * 0.5
    return score.clip(0, 100).rename("volatility_score")


def calc_indicator_2_momentum(kospi_df):
    """
    지표 2: 시장 모멘텀
    (현재가 - 125일 이평) / 125일 이평 * 100
    """
    ma_125 = kospi_df['Close'].rolling(125).mean()
    deviation = ((kospi_df['Close'] - ma_125) / ma_125 * 100)

    rolling_min = deviation.expanding(min_periods=60).min()
    rolling_max = deviation.expanding(min_periods=60).max()

    score = (deviation - rolling_min) / (rolling_max - rolling_min) * 100
    return score.clip(0, 100).rename("momentum_score")


def calc_indicator_3_price_strength(kospi_df):
    """
    지표 3: 주가 강도 (52주 범위 내 현재가 위치)
    """
    high_52w = kospi_df['Close'].rolling(252).max()
    low_52w = kospi_df['Close'].rolling(252).min()

    score = (kospi_df['Close'] - low_52w) / (high_52w - low_52w) * 100
    return score.clip(0, 100).rename("price_strength_score")


def calc_indicator_4_volume(kospi_df, short=5, long_period=20):
    """
    지표 4: 거래대금 비율 (5일 / 20일 평균)
    """
    vol_short = kospi_df['Volume'].rolling(short).mean()
    vol_long = kospi_df['Volume'].rolling(long_period).mean()
    ratio = vol_short / vol_long

    price_change_5d = kospi_df['Close'].pct_change(short)
    base_score = (ratio - 0.5) / (2.0 - 0.5) * 100

    # 패닉셀 보정
    panic_mask = (price_change_5d < -0.03) & (ratio > 1.3)
    base_score[panic_mask] = 100 - base_score[panic_mask]

    return base_score.clip(0, 100).rename("volume_score")


def calc_indicator_5_breadth(kospi_df):
    """
    지표 5: 시장 폭 — Wilder RSI (v4 변경)
    ─────────────────────────────────────
    ewm(alpha=1/14) 방식으로 변경
    단순 rolling mean → 지수가중이동평균(Wilder 방식)
    """
    close = kospi_df['Close']
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # ✅ Wilder RSI (ewm, alpha=1/14)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-9)  # div by zero 방지
    rsi = 100 - (100 / (1 + rs))

    return rsi.clip(0, 100).rename("breadth_score")


def calc_indicator_6_safe_asset(kospi_df, kosdaq_df):
    """
    지표 6: 안전자산 수요 (코스닥/코스피 상대강도)
    ─────────────────────────────────────────────
    코스닥은 성장주/소형주 중심 → 위험선호 바로미터
    - ratio > MA60 → 위험선호(탐욕)
    - ratio < MA60 → 안전자산 선호(공포)
    """
    common_idx = kospi_df.index.intersection(kosdaq_df.index)
    ratio = kosdaq_df.loc[common_idx, 'Close'] / kospi_df.loc[common_idx, 'Close']
    ratio_ma = ratio.rolling(60).mean()

    deviation = (ratio - ratio_ma) / ratio_ma * 100

    rolling_min = deviation.expanding(min_periods=60).min()
    rolling_max = deviation.expanding(min_periods=60).max()

    score = (deviation - rolling_min) / (rolling_max - rolling_min) * 100
    return score.clip(0, 100).rename("safe_asset_score")


# ============================================================
# 3. 최종 합산 (v4 가중치 + 스무딩)
# ============================================================

def calculate_korea_sentiment_index(kospi_df, kosdaq_df):
    """
    한국 시장 심리 지수 v4

    가중치 (v4):
    - 변동성(방향보정):  10%  ← v2 20% → 신뢰도 낮아 다운
    - 시장 모멘텀:       25%  ← v2 20% → 가장 신뢰, 업
    - 주가 강도(52주):   20%  ← 유지
    - 거래대금:          15%  ← 유지
    - 시장 폭(Wilder RSI): 15%  ← Wilder 방식으로 개선
    - 안전자산수요:      15%  ← v2 10% → 업

    스무딩: 5일 이동평균 (raw + smoothed 둘 다 저장)
    """
    weights = {
        'volatility':      0.10,
        'momentum':        0.25,
        'price_strength':  0.20,
        'volume':          0.15,
        'breadth':         0.15,
        'safe_asset':      0.15,
    }

    scores = pd.DataFrame({
        'volatility':     calc_indicator_1_volatility(kospi_df),
        'momentum':       calc_indicator_2_momentum(kospi_df),
        'price_strength': calc_indicator_3_price_strength(kospi_df),
        'volume':         calc_indicator_4_volume(kospi_df),
        'breadth':        calc_indicator_5_breadth(kospi_df),
        'safe_asset':     calc_indicator_6_safe_asset(kospi_df, kosdaq_df),
    })

    sentiment_raw = (
        scores['volatility']     * weights['volatility']     +
        scores['momentum']       * weights['momentum']       +
        scores['price_strength'] * weights['price_strength'] +
        scores['volume']         * weights['volume']         +
        scores['breadth']        * weights['breadth']        +
        scores['safe_asset']     * weights['safe_asset']
    )

    # ✅ 5일 스무딩 (원본 + 스무딩 둘 다 저장)
    scores['sentiment_raw']      = sentiment_raw.round(1)
    scores['sentiment_index']    = sentiment_raw.rolling(5, min_periods=1).mean().round(1)

    def grade(x):
        if pd.isna(x):    return "N/A"
        if x <= 20:       return "극도의 공포"
        elif x <= 40:     return "공포"
        elif x <= 60:     return "중립"
        elif x <= 80:     return "탐욕"
        else:             return "극도의 탐욕"

    scores['grade'] = scores['sentiment_index'].apply(grade)
    return scores


# ============================================================
# 4. 백테스트
# ============================================================

def backtest(kospi_df, scores_df):
    merged = scores_df.copy()
    merged['close'] = kospi_df['Close']
    merged['return_20d'] = kospi_df['Close'].pct_change(20).shift(-20) * 100
    merged['return_60d'] = kospi_df['Close'].pct_change(60).shift(-60) * 100
    merged = merged.dropna(subset=['sentiment_index', 'return_20d'])

    bins   = [0, 20, 40, 60, 80, 100]
    labels = ['극도의 공포(0-20)', '공포(20-40)', '중립(40-60)', '탐욕(60-80)', '극도의 탐욕(80-100)']
    merged['zone'] = pd.cut(merged['sentiment_index'], bins=bins, labels=labels, include_lowest=True)

    print("=" * 70)
    print("📊 [v4] 한국 시장 심리 지수 — 10년 백테스트 결과")
    print("    (Wilder RSI / 방향보정 변동성 / 5일 스무딩)")
    print("=" * 70)

    print("\n📊 구간별 향후 수익률 (20일 후)")
    print("-" * 50)
    result_20d = merged.groupby('zone', observed=True)['return_20d'].agg(['mean', 'median', 'count', 'std'])
    result_20d.columns = ['평균수익률(%)', '중앙값(%)', '데이터수', '표준편차(%)']
    print(result_20d.round(2).to_string())

    print("\n📊 구간별 향후 수익률 (60일 후)")
    print("-" * 50)
    merged_60 = merged.dropna(subset=['return_60d'])
    result_60d = merged_60.groupby('zone', observed=True)['return_60d'].agg(['mean', 'median', 'count', 'std'])
    result_60d.columns = ['평균수익률(%)', '중앙값(%)', '데이터수', '표준편차(%)']
    print(result_60d.round(2).to_string())

    print("\n📊 구간별 수익 확률 (20일 후 양수 확률)")
    print("-" * 50)
    for zone in labels:
        zone_data = merged[merged['zone'] == zone]['return_20d']
        if len(zone_data) > 0:
            win_rate = (zone_data > 0).sum() / len(zone_data) * 100
            print(f"  {zone}: {win_rate:.1f}% ({len(zone_data)}건)")

    print("\n" + "=" * 70)
    print("🎯 핵심 요약: '공포에 사서 탐욕에 팔라'")
    print("=" * 70)
    fear_ret    = merged[merged['sentiment_index'] <= 30]['return_20d']
    neutral_ret = merged[(merged['sentiment_index'] > 30) & (merged['sentiment_index'] < 70)]['return_20d']
    greed_ret   = merged[merged['sentiment_index'] >= 70]['return_20d']

    print(f"  공포(≤30)  → 20일 후 평균: {fear_ret.mean():.2f}%  "
          f"(승률: {(fear_ret > 0).mean()*100:.1f}%, {len(fear_ret)}건)")
    print(f"  중립(30-70)→ 20일 후 평균: {neutral_ret.mean():.2f}%  "
          f"(승률: {(neutral_ret > 0).mean()*100:.1f}%, {len(neutral_ret)}건)")
    print(f"  탐욕(≥70)  → 20일 후 평균: {greed_ret.mean():.2f}%  "
          f"(승률: {(greed_ret > 0).mean()*100:.1f}%, {len(greed_ret)}건)")

    corr_20 = merged['sentiment_index'].corr(merged['return_20d'])
    corr_60 = merged['sentiment_index'].corr(merged['return_60d'].dropna())
    print(f"\n  심리지수 vs 20일후 수익률 상관계수: {corr_20:.3f}")
    print(f"  심리지수 vs 60일후 수익률 상관계수: {corr_60:.3f}")
    print(f"  (음수 = 공포에 살수록 수익 → 지수 정상 작동)")

    return merged, result_20d


# ============================================================
# 5. 차트 생성 (5 패널)
# ============================================================

def plot_charts(kospi_df, scores_df, merged_df, last_val=None, latest_grade=None):
    fig = plt.figure(figsize=(18, 30))
    fig.patch.set_facecolor('#0d0d0d')

    gs = fig.add_gridspec(5, 1, hspace=0.45, top=0.96, bottom=0.04)

    # ─────────────────────────────────────────
    # Chart 1: 심리지수 (스무딩 vs RAW)
    # ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#1a1a2e')

    idx       = scores_df.index
    sentiment = scores_df['sentiment_index']    # smoothed
    sentiment_raw = scores_df['sentiment_raw']  # raw

    # 배경 컬러밴드
    ax1.axhspan(0,  20, alpha=0.15, color='#ff4444')
    ax1.axhspan(20, 40, alpha=0.10, color='#ff8c00')
    ax1.axhspan(40, 60, alpha=0.08, color='#888888')
    ax1.axhspan(60, 80, alpha=0.10, color='#00cc66')
    ax1.axhspan(80, 100, alpha=0.15, color='#00ff88')

    # RAW (흐림)
    ax1.plot(idx, sentiment_raw, color='#4488aa', linewidth=0.6, alpha=0.5, label='RAW (일별)')
    # 스무딩 (메인)
    ax1.plot(idx, sentiment, color='#00d4ff', linewidth=1.5, alpha=0.95, label='5일 스무딩', zorder=5)

    # 색상 채우기
    for lo, hi, col in [(0, 20, '#ff4444'), (20, 40, '#ff8c00'), (40, 60, '#aaaaaa'),
                        (60, 80, '#00cc66'), (80, 100, '#00ff88')]:
        ax1.fill_between(idx, lo, sentiment,
                         where=(sentiment >= lo) & (sentiment < hi),
                         alpha=0.25, color=col, zorder=4)

    for y, c, ls in [(20, '#ff6666', '--'), (40, '#ffaa44', ':'),
                     (60, '#888888', ':'), (80, '#44ff88', '--')]:
        ax1.axhline(y=y, color=c, linestyle=ls, linewidth=0.8, alpha=0.6)

    # 최신값
    _last_val  = sentiment.dropna().iloc[-1]
    raw_val    = sentiment_raw.dropna().iloc[-1]
    last_date  = sentiment.dropna().index[-1]
    if last_val is None:
        last_val = _last_val
    if latest_grade is None:
        def _grade(x):
            if x <= 20: return "극도의 공포"
            elif x <= 40: return "공포"
            elif x <= 60: return "중립"
            elif x <= 80: return "탐욕"
            else: return "극도의 탐욕"
        latest_grade = _grade(last_val)
    ax1.annotate(
        f'현재: {_last_val:.0f} (RAW: {raw_val:.0f})',
        xy=(last_date, _last_val),
        xytext=(-80, 15), textcoords='offset points',
        color='white', fontsize=11, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='white', lw=1.5)
    )

    ax1.set_xlim(idx[0], idx[-1])
    ax1.set_ylim(0, 100)
    ax1.set_ylabel('심리 지수', color='white', fontsize=11)
    ax1.set_title('한국 시장 심리 지수 v4 — 10년 추이 (5일 스무딩 + RAW)', 
                  color='white', fontsize=14, fontweight='bold', pad=10)
    ax1.tick_params(colors='white')
    for sp in ['bottom', 'left']:
        ax1.spines[sp].set_color('#444')
    for sp in ['top', 'right']:
        ax1.spines[sp].set_visible(False)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.grid(axis='y', color='#333', linewidth=0.5)

    legend_patches = [
        mpatches.Patch(color='#ff4444', alpha=0.6, label='극도의 공포 (0-20)'),
        mpatches.Patch(color='#ff8c00', alpha=0.6, label='공포 (20-40)'),
        mpatches.Patch(color='#aaaaaa', alpha=0.6, label='중립 (40-60)'),
        mpatches.Patch(color='#00cc66', alpha=0.6, label='탐욕 (60-80)'),
        mpatches.Patch(color='#00ff88', alpha=0.6, label='극도의 탐욕 (80-100)'),
    ]
    from matplotlib.lines import Line2D
    legend_lines = [
        Line2D([0], [0], color='#00d4ff', linewidth=2, label='5일 스무딩'),
        Line2D([0], [0], color='#4488aa', linewidth=1, alpha=0.5, label='RAW'),
    ]
    ax1.legend(handles=legend_patches + legend_lines, loc='upper left', fontsize=8,
               facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', ncol=4)

    # ─────────────────────────────────────────
    # Chart 2: 코스피 + 공포/탐욕 오버레이
    # ─────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#1a1a2e')

    common = kospi_df.index.intersection(scores_df.index)
    close  = kospi_df.loc[common, 'Close']
    sent_c = scores_df.loc[common, 'sentiment_index']

    ax2.plot(common, close, color='#ffffff', linewidth=1.0, alpha=0.8, zorder=3)
    ax2.fill_between(common, close.min()*0.95, close.max()*1.05,
                     where=(sent_c <= 30), alpha=0.25, color='#ff4444', zorder=2, label='공포구간(≤30)')
    ax2.fill_between(common, close.min()*0.95, close.max()*1.05,
                     where=(sent_c >= 70), alpha=0.25, color='#00ff88', zorder=2, label='탐욕구간(≥70)')

    ax2.set_xlim(common[0], common[-1])
    ax2.set_ylabel('코스피', color='white', fontsize=11)
    ax2.set_title('코스피 지수 (빨강=공포 ≤30, 녹색=탐욕 ≥70)', color='white', fontsize=12)
    ax2.tick_params(colors='white')
    for sp in ['bottom', 'left']:
        ax2.spines[sp].set_color('#444')
    for sp in ['top', 'right']:
        ax2.spines[sp].set_visible(False)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.grid(color='#333', linewidth=0.5, alpha=0.5)
    ax2.legend(loc='upper left', fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    # ─────────────────────────────────────────
    # Chart 3: 6개 지표 개별 추이
    # ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor('#1a1a2e')

    indicator_cols = {
        'volatility':     ('#ff6b6b', f'변동성(10%)'),
        'momentum':       ('#ffd93d', f'모멘텀(25%)'),
        'price_strength': ('#6bcb77', f'주가강도(20%)'),
        'volume':         ('#4d96ff', f'거래대금(15%)'),
        'breadth':        ('#ff922b', f'시장폭RSI(15%)'),
        'safe_asset':     ('#cc5de8', f'안전자산수요(15%)'),
    }

    for col, (color, label) in indicator_cols.items():
        if col in scores_df.columns:
            ax3.plot(scores_df.index, scores_df[col], color=color,
                     linewidth=0.8, alpha=0.8, label=label)

    ax3.axhline(y=50, color='#666', linestyle='--', linewidth=0.8, alpha=0.6)
    ax3.set_xlim(scores_df.index[0], scores_df.index[-1])
    ax3.set_ylim(0, 100)
    ax3.set_ylabel('지표 점수', color='white', fontsize=11)
    ax3.set_title('6개 지표 개별 추이 (v4 가중치 표시)', color='white', fontsize=12)
    ax3.tick_params(colors='white')
    for sp in ['bottom', 'left']:
        ax3.spines[sp].set_color('#444')
    for sp in ['top', 'right']:
        ax3.spines[sp].set_visible(False)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax3.xaxis.set_major_locator(mdates.YearLocator())
    ax3.grid(color='#333', linewidth=0.5, alpha=0.5)
    ax3.legend(loc='upper left', fontsize=8, facecolor='#1a1a2e',
               edgecolor='#444', labelcolor='white', ncol=3)

    # ─────────────────────────────────────────
    # Chart 4: 구간별 수익률 바차트
    # ─────────────────────────────────────────
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor('#1a1a2e')

    if merged_df is not None and 'zone' in merged_df.columns:
        zone_labels_orig = ['극도의 공포(0-20)', '공포(20-40)', '중립(40-60)', '탐욕(60-80)', '극도의 탐욕(80-100)']
        zone_labels_disp = ['극도의 공포\n(0-20)', '공포\n(20-40)', '중립\n(40-60)', '탐욕\n(60-80)', '극도의 탐욕\n(80-100)']

        means_20, means_60, counts = [], [], []
        for z in zone_labels_orig:
            d20 = merged_df[merged_df['zone'] == z]['return_20d'].dropna()
            d60 = merged_df[merged_df['zone'] == z]['return_60d'].dropna()
            means_20.append(d20.mean() if len(d20) > 0 else 0)
            means_60.append(d60.mean() if len(d60) > 0 else 0)
            counts.append(len(d20))

        x = np.arange(len(zone_labels_disp))
        width = 0.35
        colors_20 = ['#ff4444' if v < 0 else '#00cc66' for v in means_20]
        colors_60 = ['#ff6666' if v < 0 else '#44ff88' for v in means_60]

        bars1 = ax4.bar(x - width/2, means_20, width, label='20일 후', color=colors_20, alpha=0.85, zorder=3)
        bars2 = ax4.bar(x + width/2, means_60, width, label='60일 후', color=colors_60, alpha=0.65, zorder=3)
        ax4.bar_label(bars1, fmt='%.1f%%', color='white', fontsize=9, padding=3)
        ax4.bar_label(bars2, fmt='%.1f%%', color='#dddddd', fontsize=9, padding=3)

        # 데이터 수 표시
        for i, cnt in enumerate(counts):
            ax4.text(x[i], -2.5, f'n={cnt}', ha='center', va='top', color='#aaaaaa', fontsize=8)

        ax4.axhline(y=0, color='white', linewidth=0.8, alpha=0.5)
        ax4.set_xticks(x)
        ax4.set_xticklabels(zone_labels_disp, color='white', fontsize=9)
        ax4.set_ylabel('평균 수익률 (%)', color='white', fontsize=11)
        ax4.set_title('심리 구간별 향후 평균 수익률 (20일 / 60일)', color='white', fontsize=12)
        ax4.tick_params(colors='white')
        for sp in ['bottom', 'left']:
            ax4.spines[sp].set_color('#444')
        for sp in ['top', 'right']:
            ax4.spines[sp].set_visible(False)
        ax4.grid(axis='y', color='#333', linewidth=0.5, alpha=0.5)
        ax4.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    # ─────────────────────────────────────────
    # Chart 5: 최근 60일 돋보기 (RAW vs 스무딩)
    # ─────────────────────────────────────────
    ax5 = fig.add_subplot(gs[4])
    ax5.set_facecolor('#1a1a2e')

    recent_60 = scores_df.tail(60)
    ax5.plot(recent_60.index, recent_60['sentiment_raw'],
             color='#4488aa', linewidth=1.0, alpha=0.6, label='RAW', zorder=3)
    ax5.plot(recent_60.index, recent_60['sentiment_index'],
             color='#00d4ff', linewidth=2.0, alpha=0.95, label='5일 스무딩', zorder=5)

    for lo, hi, col in [(0, 20, '#ff4444'), (20, 40, '#ff8c00'), (40, 60, '#aaaaaa'),
                        (60, 80, '#00cc66'), (80, 100, '#00ff88')]:
        ax5.fill_between(recent_60.index, lo, recent_60['sentiment_index'],
                         where=(recent_60['sentiment_index'] >= lo) & (recent_60['sentiment_index'] < hi),
                         alpha=0.3, color=col, zorder=4)

    for y, c, ls in [(20, '#ff6666', '--'), (40, '#ffaa44', ':'),
                     (60, '#888888', ':'), (80, '#44ff88', '--')]:
        ax5.axhline(y=y, color=c, linestyle=ls, linewidth=0.8, alpha=0.6)

    # 날짜별 레이블
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax5.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax5.get_xticklabels(), rotation=30, ha='right')

    ax5.set_xlim(recent_60.index[0], recent_60.index[-1])
    ax5.set_ylim(0, 100)
    ax5.set_ylabel('심리 지수', color='white', fontsize=11)
    ax5.set_title(f'최근 60일 확대 — RAW vs 5일 스무딩 (최신: {last_val:.0f}점 / {latest_grade})',
                  color='white', fontsize=12)
    ax5.tick_params(colors='white')
    for sp in ['bottom', 'left']:
        ax5.spines[sp].set_color('#444')
    for sp in ['top', 'right']:
        ax5.spines[sp].set_visible(False)
    ax5.grid(color='#333', linewidth=0.5, alpha=0.5)
    ax5.legend(loc='upper left', fontsize=9, facecolor='#1a1a2e',
               edgecolor='#444', labelcolor='white')

    output_path = "C:/Users/Mario/work/korea_sentiment_v4_chart.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0d0d0d')
    plt.close()
    print(f"✅ 차트 저장: {output_path}")
    return output_path


# ============================================================
# 6. 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("한국 시장 심리 지수 v4 - 10년 백테스트")
    print("변동성 방향보정 | Wilder RSI | 새 가중치 | 5일 스무딩")
    print("=" * 65)

    print("\n[1] 데이터 다운로드...")
    kospi, kosdaq = fetch_data(period="10y")
    print(f"    코스피: {len(kospi)}일 / 코스닥: {len(kosdaq)}일")

    print("\n[2] 심리 지수 계산...")
    scores = calculate_korea_sentiment_index(kospi, kosdaq)
    scores.to_csv("C:/Users/Mario/work/korea_sentiment_v4.csv")

    # 최신 수치
    latest     = scores.dropna(subset=['sentiment_index']).iloc[-1]
    last_date  = scores.dropna(subset=['sentiment_index']).index[-1]
    last_val   = latest['sentiment_index']
    latest_grade = latest['grade']

    print(f"\n📈 최신 심리 지수 [{last_date.strftime('%Y-%m-%d')}]")
    print(f"   ● 종합 (5일 스무딩): {last_val:.1f} → {latest_grade}")
    print(f"   ● RAW (당일):        {latest['sentiment_raw']:.1f}")
    print(f"   ├ 변동성(방향보정):  {latest['volatility']:.1f}  (가중 10%)")
    print(f"   ├ 모멘텀:            {latest['momentum']:.1f}  (가중 25%)")
    print(f"   ├ 주가강도:          {latest['price_strength']:.1f}  (가중 20%)")
    print(f"   ├ 거래대금:          {latest['volume']:.1f}  (가중 15%)")
    print(f"   ├ 시장폭(Wilder RSI):{latest['breadth']:.1f}  (가중 15%)")
    print(f"   └ 안전자산수요:      {latest['safe_asset']:.1f}  (가중 15%)")

    print("\n[3] 백테스트...")
    merged, result = backtest(kospi, scores)

    print("\n[4] 차트 생성...")
    chart_path = plot_charts(kospi, scores, merged, last_val=last_val, latest_grade=latest_grade)

    print("\n✅ 완료!")
    print(f"   CSV: korea_sentiment_v4.csv")
    print(f"   차트: {chart_path}")
