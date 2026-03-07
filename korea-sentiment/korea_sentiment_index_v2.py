"""
=============================================================
투자SNS 한국 시장 심리 지수 v2 (Korea Market Sentiment Index)
=============================================================

변경사항 (v2):
- 정규화 방식: rolling(252) → expanding() (전체 기간 누적)
- 6번째 지표 추가: 코스닥/코스피 상대강도

CNN Fear & Greed Index 방법론을 한국 시장에 맞게 변형.
6개 지표를 각각 0~100으로 정규화 → 가중평균 → 최종 점수.

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

    # MultiIndex 컬럼 → 단순 컬럼
    if isinstance(kospi.columns, pd.MultiIndex):
        kospi.columns = kospi.columns.droplevel(1)
    if isinstance(kosdaq.columns, pd.MultiIndex):
        kosdaq.columns = kosdaq.columns.droplevel(1)

    return kospi, kosdaq


# ============================================================
# 2. 6개 지표 계산 (expanding 정규화 적용)
# ============================================================

def calc_indicator_1_volatility(kospi_df, lookback=20):
    """
    지표 1: 변동성 지수 (VKOSPI 대용)
    정규화: expanding() — 전체 기간 누적 min/max 사용
    역변환: 변동성 높으면 0(공포), 낮으면 100(탐욕)
    """
    returns = kospi_df['Close'].pct_change()
    vol_20d = returns.rolling(lookback).std() * np.sqrt(252) * 100

    # ✅ expanding: 전체 누적 기간 min/max
    rolling_min = vol_20d.expanding(min_periods=60).min()
    rolling_max = vol_20d.expanding(min_periods=60).max()

    score = 100 - ((vol_20d - rolling_min) / (rolling_max - rolling_min) * 100)
    return score.clip(0, 100).rename("volatility_score")


def calc_indicator_2_momentum(kospi_df):
    """
    지표 2: 시장 모멘텀
    계산: (현재가 - 125일 이평) / 125일 이평 * 100
    정규화: expanding() 전체 누적
    """
    ma_125 = kospi_df['Close'].rolling(125).mean()
    deviation = ((kospi_df['Close'] - ma_125) / ma_125 * 100)

    # ✅ expanding
    rolling_min = deviation.expanding(min_periods=60).min()
    rolling_max = deviation.expanding(min_periods=60).max()

    score = (deviation - rolling_min) / (rolling_max - rolling_min) * 100
    return score.clip(0, 100).rename("momentum_score")


def calc_indicator_3_price_strength(kospi_df):
    """
    지표 3: 주가 강도 (52주 신고가 vs 신저가)
    (이 지표는 이미 고정 252일 롤링 → 변경 없음, 원래 방식 유지)
    """
    high_52w = kospi_df['Close'].rolling(252).max()
    low_52w = kospi_df['Close'].rolling(252).min()

    score = (kospi_df['Close'] - low_52w) / (high_52w - low_52w) * 100
    return score.clip(0, 100).rename("price_strength_score")


def calc_indicator_4_volume(kospi_df, short=5, long_period=20):
    """
    지표 4: 거래대금 비율
    정규화: expanding() 전체 누적
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
    지표 5: 시장 폭 (RSI 대용)
    정규화: expanding() 전체 누적
    """
    close = kospi_df['Close']
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.clip(0, 100).rename("breadth_score")


def calc_indicator_6_kosdaq_kospi_ratio(kospi_df, kosdaq_df):
    """
    지표 6: 코스닥/코스피 상대강도 (NEW)
    ─────────────────────────────────────
    원리: 코스닥은 성장주/소형주 중심 → 투기심리 바로미터
    - ratio가 60일 이동평균 위 → 투기과열 = 탐욕
    - ratio가 60일 이동평균 아래 → 위험회피 = 공포

    계산:
      ratio = 코스닥 / 코스피
      signal = (ratio - ratio_ma60) / ratio_ma60 * 100  (ma 대비 편차 %)
    정규화: expanding() 전체 누적
    """
    # 공통 인덱스로 정렬
    common_idx = kospi_df.index.intersection(kosdaq_df.index)
    ratio = kosdaq_df.loc[common_idx, 'Close'] / kospi_df.loc[common_idx, 'Close']
    ratio_ma = ratio.rolling(60).mean()

    # MA 대비 편차 (%)
    deviation = (ratio - ratio_ma) / ratio_ma * 100

    # ✅ expanding 정규화
    rolling_min = deviation.expanding(min_periods=60).min()
    rolling_max = deviation.expanding(min_periods=60).max()

    score = (deviation - rolling_min) / (rolling_max - rolling_min) * 100
    return score.clip(0, 100).rename("kosdaq_ratio_score")


# ============================================================
# 3. 최종 합산 (가중평균) — 6개 지표
# ============================================================

def calculate_korea_sentiment_index(kospi_df, kosdaq_df):
    """
    한국 시장 심리 지수 계산 (v2 — 6개 지표)

    가중치:
    - 변동성(VKOSPI 대용): 20%
    - 시장 모멘텀: 20%
    - 주가 강도(52주): 20%
    - 거래대금: 15%
    - 시장 폭(RSI): 15%
    - 코스닥/코스피 상대강도: 10%  ← NEW
    """
    weights = {
        'volatility': 0.20,
        'momentum': 0.20,
        'price_strength': 0.20,
        'volume': 0.15,
        'breadth': 0.15,
        'kosdaq_ratio': 0.10,
    }

    scores = pd.DataFrame({
        'volatility': calc_indicator_1_volatility(kospi_df),
        'momentum': calc_indicator_2_momentum(kospi_df),
        'price_strength': calc_indicator_3_price_strength(kospi_df),
        'volume': calc_indicator_4_volume(kospi_df),
        'breadth': calc_indicator_5_breadth(kospi_df),
        'kosdaq_ratio': calc_indicator_6_kosdaq_kospi_ratio(kospi_df, kosdaq_df),
    })

    sentiment = (
        scores['volatility'] * weights['volatility'] +
        scores['momentum'] * weights['momentum'] +
        scores['price_strength'] * weights['price_strength'] +
        scores['volume'] * weights['volume'] +
        scores['breadth'] * weights['breadth'] +
        scores['kosdaq_ratio'] * weights['kosdaq_ratio']
    )

    scores['sentiment_index'] = sentiment.round(1)

    def grade(x):
        if x <= 20: return "극도의 공포"
        elif x <= 40: return "공포"
        elif x <= 60: return "중립"
        elif x <= 80: return "탐욕"
        else: return "극도의 탐욕"

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

    bins = [0, 20, 40, 60, 80, 100]
    labels = ['극도의 공포(0-20)', '공포(20-40)', '중립(40-60)', '탐욕(60-80)', '극도의 탐욕(80-100)']
    merged['zone'] = pd.cut(merged['sentiment_index'], bins=bins, labels=labels, include_lowest=True)

    print("=" * 70)
    print("📊 [v2] 한국 시장 심리 지수 — 10년 백테스트 결과")
    print("    (정규화: expanding / 6개 지표)")
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
    print("🎯 핵심: '공포에 사서 탐욕에 팔라'")
    print("=" * 70)
    fear_returns = merged[merged['sentiment_index'] <= 30]['return_20d']
    neutral_returns = merged[(merged['sentiment_index'] > 30) & (merged['sentiment_index'] < 70)]['return_20d']
    greed_returns = merged[merged['sentiment_index'] >= 70]['return_20d']

    print(f"  공포(≤30)  → 20일 후 평균: {fear_returns.mean():.2f}%  (승률: {(fear_returns > 0).mean()*100:.1f}%, {len(fear_returns)}건)")
    print(f"  중립(30-70)→ 20일 후 평균: {neutral_returns.mean():.2f}%  (승률: {(neutral_returns > 0).mean()*100:.1f}%, {len(neutral_returns)}건)")
    print(f"  탐욕(≥70)  → 20일 후 평균: {greed_returns.mean():.2f}%  (승률: {(greed_returns > 0).mean()*100:.1f}%, {len(greed_returns)}건)")

    corr_20 = merged['sentiment_index'].corr(merged['return_20d'])
    print(f"\n  심리지수 vs 20일후 수익률 상관계수: {corr_20:.3f}")
    print(f"  (음수 = 공포에 살수록 수익 → 지수 정상 작동)")

    return merged, result_20d


# ============================================================
# 5. 차트 생성
# ============================================================

def plot_charts(kospi_df, scores_df, merged_df):
    fig = plt.figure(figsize=(18, 24))
    fig.patch.set_facecolor('#0d0d0d')

    # ─────────────────────────────────────────
    # Chart 1: 심리지수 10년 추이 (상단 큰 차트)
    # ─────────────────────────────────────────
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.set_facecolor('#1a1a2e')

    idx = scores_df.index
    sentiment = scores_df['sentiment_index']

    # 배경 컬러밴드
    ax1.axhspan(0, 20, alpha=0.15, color='#ff4444', label='극도의 공포')
    ax1.axhspan(20, 40, alpha=0.10, color='#ff8c00')
    ax1.axhspan(40, 60, alpha=0.08, color='#888888')
    ax1.axhspan(60, 80, alpha=0.10, color='#00cc66')
    ax1.axhspan(80, 100, alpha=0.15, color='#00ff88', label='극도의 탐욕')

    # 심리 지수 선
    ax1.plot(idx, sentiment, color='#00d4ff', linewidth=1.2, alpha=0.9, zorder=5)

    # 색상 채우기 (구간별)
    for lo, hi, col in [(0, 20, '#ff4444'), (20, 40, '#ff8c00'), (40, 60, '#aaaaaa'),
                        (60, 80, '#00cc66'), (80, 100, '#00ff88')]:
        ax1.fill_between(idx, lo, sentiment, where=(sentiment >= lo) & (sentiment < hi),
                         alpha=0.3, color=col, zorder=4)

    # 수평선
    for y, c, ls in [(20, '#ff6666', '--'), (40, '#ffaa44', ':'),
                     (60, '#888888', ':'), (80, '#44ff88', '--')]:
        ax1.axhline(y=y, color=c, linestyle=ls, linewidth=0.8, alpha=0.6)

    # 최신값 표시
    last_val = sentiment.dropna().iloc[-1]
    last_date = sentiment.dropna().index[-1]
    ax1.annotate(f'현재: {last_val:.0f}', xy=(last_date, last_val),
                 xytext=(-60, 15), textcoords='offset points',
                 color='white', fontsize=11, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='white', lw=1.5))

    ax1.set_xlim(idx[0], idx[-1])
    ax1.set_ylim(0, 100)
    ax1.set_ylabel('심리 지수', color='white', fontsize=11)
    ax1.set_title('한국 시장 심리 지수 v2 — 10년 추이 (expanding 정규화)', 
                  color='white', fontsize=14, fontweight='bold', pad=10)
    ax1.tick_params(colors='white')
    ax1.spines['bottom'].set_color('#444')
    ax1.spines['left'].set_color('#444')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.grid(axis='y', color='#333', linewidth=0.5)

    # 등급 범례
    legend_patches = [
        mpatches.Patch(color='#ff4444', alpha=0.6, label='극도의 공포 (0-20)'),
        mpatches.Patch(color='#ff8c00', alpha=0.6, label='공포 (20-40)'),
        mpatches.Patch(color='#aaaaaa', alpha=0.6, label='중립 (40-60)'),
        mpatches.Patch(color='#00cc66', alpha=0.6, label='탐욕 (60-80)'),
        mpatches.Patch(color='#00ff88', alpha=0.6, label='극도의 탐욕 (80-100)'),
    ]
    ax1.legend(handles=legend_patches, loc='upper left', fontsize=8,
               facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', ncol=5)

    # ─────────────────────────────────────────
    # Chart 2: 코스피 지수 오버레이
    # ─────────────────────────────────────────
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.set_facecolor('#1a1a2e')

    common = kospi_df.index.intersection(scores_df.index)
    close = kospi_df.loc[common, 'Close']
    sent_common = scores_df.loc[common, 'sentiment_index']

    # 코스피 선
    ax2.plot(common, close, color='#ffffff', linewidth=1.0, alpha=0.7, zorder=3)

    # 공포 구간 강조 (빨간 배경)
    ax2.fill_between(common, close.min() * 0.95, close.max() * 1.05,
                     where=(sent_common <= 30), alpha=0.25, color='#ff4444', zorder=2)
    ax2.fill_between(common, close.min() * 0.95, close.max() * 1.05,
                     where=(sent_common >= 70), alpha=0.25, color='#00ff88', zorder=2)

    ax2.set_xlim(common[0], common[-1])
    ax2.set_ylabel('코스피', color='white', fontsize=11)
    ax2.set_title('코스피 지수 (빨강=공포구간, 녹색=탐욕구간)', color='white', fontsize=12)
    ax2.tick_params(colors='white')
    ax2.spines['bottom'].set_color('#444')
    ax2.spines['left'].set_color('#444')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.grid(color='#333', linewidth=0.5, alpha=0.5)

    # ─────────────────────────────────────────
    # Chart 3: 6개 지표 개별 추이
    # ─────────────────────────────────────────
    ax3 = fig.add_subplot(4, 1, 3)
    ax3.set_facecolor('#1a1a2e')

    indicator_cols = {
        'volatility': ('#ff6b6b', '변동성'),
        'momentum': ('#ffd93d', '모멘텀'),
        'price_strength': ('#6bcb77', '주가강도'),
        'volume': ('#4d96ff', '거래대금'),
        'breadth': ('#ff922b', '시장폭(RSI)'),
        'kosdaq_ratio': ('#cc5de8', '코스닥/코스피 (NEW)'),
    }

    for col, (color, label) in indicator_cols.items():
        if col in scores_df.columns:
            ax3.plot(scores_df.index, scores_df[col], color=color, linewidth=0.8,
                     alpha=0.8, label=label)

    ax3.axhline(y=50, color='#666', linestyle='--', linewidth=0.8, alpha=0.6)
    ax3.set_xlim(scores_df.index[0], scores_df.index[-1])
    ax3.set_ylim(0, 100)
    ax3.set_ylabel('지표 점수', color='white', fontsize=11)
    ax3.set_title('6개 지표 개별 추이', color='white', fontsize=12)
    ax3.tick_params(colors='white')
    ax3.spines['bottom'].set_color('#444')
    ax3.spines['left'].set_color('#444')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax3.xaxis.set_major_locator(mdates.YearLocator())
    ax3.grid(color='#333', linewidth=0.5, alpha=0.5)
    ax3.legend(loc='upper left', fontsize=8, facecolor='#1a1a2e',
               edgecolor='#444', labelcolor='white', ncol=3)

    # ─────────────────────────────────────────
    # Chart 4: 구간별 수익률 바차트
    # ─────────────────────────────────────────
    ax4 = fig.add_subplot(4, 1, 4)
    ax4.set_facecolor('#1a1a2e')

    if merged_df is not None and 'zone' in merged_df.columns:
        labels = ['극도의 공포\n(0-20)', '공포\n(20-40)', '중립\n(40-60)', '탐욕\n(60-80)', '극도의 탐욕\n(80-100)']
        zone_labels_orig = ['극도의 공포(0-20)', '공포(20-40)', '중립(40-60)', '탐욕(60-80)', '극도의 탐욕(80-100)']
        
        means_20 = []
        means_60 = []
        for z in zone_labels_orig:
            d20 = merged_df[merged_df['zone'] == z]['return_20d'].dropna()
            d60 = merged_df[merged_df['zone'] == z]['return_60d'].dropna()
            means_20.append(d20.mean() if len(d20) > 0 else 0)
            means_60.append(d60.mean() if len(d60) > 0 else 0)

        x = np.arange(len(labels))
        width = 0.35
        colors_bar_20 = ['#ff4444' if v < 0 else '#00cc66' for v in means_20]
        colors_bar_60 = ['#ff6666' if v < 0 else '#44ff88' for v in means_60]

        bars1 = ax4.bar(x - width/2, means_20, width, label='20일 후 수익률', color=colors_bar_20, alpha=0.85, zorder=3)
        bars2 = ax4.bar(x + width/2, means_60, width, label='60일 후 수익률', color=colors_bar_60, alpha=0.65, zorder=3)

        ax4.bar_label(bars1, fmt='%.1f%%', color='white', fontsize=9, padding=3)
        ax4.bar_label(bars2, fmt='%.1f%%', color='#dddddd', fontsize=9, padding=3)

        ax4.axhline(y=0, color='white', linewidth=0.8, alpha=0.5)
        ax4.set_xticks(x)
        ax4.set_xticklabels(labels, color='white', fontsize=9)
        ax4.set_ylabel('평균 수익률 (%)', color='white', fontsize=11)
        ax4.set_title('심리 구간별 향후 평균 수익률 (20일 / 60일)', color='white', fontsize=12)
        ax4.tick_params(colors='white')
        ax4.spines['bottom'].set_color('#444')
        ax4.spines['left'].set_color('#444')
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.grid(axis='y', color='#333', linewidth=0.5, alpha=0.5)
        ax4.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    plt.tight_layout(pad=3.0)
    output_path = "C:/Users/Mario/work/korea_sentiment_v2_chart.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0d0d0d')
    plt.close()
    print(f"✅ 차트 저장: {output_path}")
    return output_path


# ============================================================
# 6. 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("한국 시장 심리 지수 v2 - 10년 백테스트")
    print("정규화: expanding() | 지표: 6개")
    print("=" * 60)

    print("\n[1] 데이터 다운로드...")
    kospi, kosdaq = fetch_data(period="10y")
    print(f"    코스피: {len(kospi)}일 / 코스닥: {len(kosdaq)}일")

    print("\n[2] 심리 지수 계산...")
    scores = calculate_korea_sentiment_index(kospi, kosdaq)
    scores.to_csv("C:/Users/Mario/work/korea_sentiment_v2.csv")

    # 최신 수치
    latest = scores.dropna(subset=['sentiment_index']).iloc[-1]
    last_date = scores.dropna(subset=['sentiment_index']).index[-1]
    print(f"\n📈 최신 심리 지수 [{last_date.strftime('%Y-%m-%d')}]")
    print(f"   ● 종합: {latest['sentiment_index']:.1f} → {latest['grade']}")
    print(f"   ├ 변동성:        {latest['volatility']:.1f}")
    print(f"   ├ 모멘텀:        {latest['momentum']:.1f}")
    print(f"   ├ 주가강도:      {latest['price_strength']:.1f}")
    print(f"   ├ 거래대금:      {latest['volume']:.1f}")
    print(f"   ├ 시장폭(RSI):   {latest['breadth']:.1f}")
    print(f"   └ 코스닥/코스피: {latest['kosdaq_ratio']:.1f}  ← NEW")

    print("\n[3] 백테스트...")
    merged, result = backtest(kospi, scores)

    print("\n[4] 차트 생성...")
    chart_path = plot_charts(kospi, scores, merged)

    print("\n✅ 완료!")
    print(f"   CSV: korea_sentiment_v2.csv")
    print(f"   차트: {chart_path}")
