"""
=============================================================
투자SNS 한국 시장 심리 지수 v3 (Korea Market Sentiment Index)
=============================================================

CNN Fear & Greed Index 방법론 (Z-score + CDF 정규화).
6개 지표 균등 가중치 (각 16.7%).

변경사항 v3:
- 정규화: min-max → Z-score(252일) + CDF 변환
- 지표6: 코스닥/코스피 비율 → 안전자산 수요 (주식 vs 채권 수익률)

0 = 극도의 공포 | 25 = 공포 | 50 = 중립 | 75 = 탐욕 | 100 = 극도의 탐욕
=============================================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# ============================================================
# 헬퍼: Z-score → CDF → 0~100 점수 (CNN 방식)
# ============================================================
def zscore_to_score(series: pd.Series, window: int = 252, min_periods: int = 60) -> pd.Series:
    """
    CNN F&G 방식:
    1. 252일 롤링 평균/표준편차로 Z-score 계산
    2. 정규분포 CDF로 0~1 변환
    3. 0~100 스케일
    """
    roll_mean = series.rolling(window, min_periods=min_periods).mean()
    roll_std  = series.rolling(window, min_periods=min_periods).std()
    z = (series - roll_mean) / roll_std.replace(0, np.nan)
    score = z.apply(lambda v: stats.norm.cdf(v) * 100 if not np.isnan(v) else np.nan)
    return score


# ============================================================
# 1. 데이터 수집
# ============================================================
def fetch_data(period="10y"):
    print("  코스피 (^KS11) ...")
    kospi  = yf.download("^KS11",    period=period, auto_adjust=True, progress=False)
    print("  코스닥 (^KQ11) ...")
    kosdaq = yf.download("^KQ11",    period=period, auto_adjust=True, progress=False)
    print("  KOSEF 국고채10년 (148070.KS) ...")
    bond   = yf.download("148070.KS", period=period, auto_adjust=True, progress=False)

    for df in [kospi, kosdaq, bond]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

    return kospi, kosdaq, bond


# ============================================================
# 2. 6개 지표
# ============================================================

def calc_1_volatility(kospi_df):
    """
    지표1: 변동성 (VKOSPI 대용)
    20일 역사적 변동성(연율화) → Z-score CDF
    역변환: 변동성 높으면 공포(낮은 점수)
    """
    ret    = kospi_df['Close'].pct_change()
    vol20  = ret.rolling(20).std() * np.sqrt(252) * 100
    raw    = zscore_to_score(vol20)
    return (100 - raw).rename("volatility")          # 역변환


def calc_2_momentum(kospi_df):
    """
    지표2: 시장 모멘텀 (125일 이평 대비 편차)
    CNN: S&P500 vs 125-day MA
    """
    ma125  = kospi_df['Close'].rolling(125).mean()
    dev    = (kospi_df['Close'] - ma125) / ma125 * 100
    return zscore_to_score(dev).rename("momentum")


def calc_3_price_strength(kospi_df):
    """
    지표3: 52주 고저 강도
    (현재가 - 52주저) / (52주고 - 52주저) → 0~100 직접 사용
    (CNN: 52주 신고가/신저가 종목 비율 대용)
    """
    hi52 = kospi_df['Close'].rolling(252).max()
    lo52 = kospi_df['Close'].rolling(252).min()
    raw  = (kospi_df['Close'] - lo52) / (hi52 - lo52) * 100
    # 이 지표는 이미 0~100이므로 Z-score 적용
    return zscore_to_score(raw).rename("price_strength")


def calc_4_volume(kospi_df):
    """
    지표4: 거래대금 모멘텀
    5일 거래량 / 20일 거래량 비율 → Z-score CDF
    + 하락장 패닉셀 보정
    """
    vol5  = kospi_df['Volume'].rolling(5).mean()
    vol20 = kospi_df['Volume'].rolling(20).mean()
    ratio = vol5 / vol20

    price_chg5 = kospi_df['Close'].pct_change(5)
    raw = zscore_to_score(ratio)

    # 패닉셀: 3% 이상 하락 + 거래량 폭증 → 점수 역전
    panic = (price_chg5 < -0.03) & (ratio > 1.3)
    raw[panic] = 100 - raw[panic]

    return raw.rename("volume")


def calc_5_breadth(kospi_df):
    """
    지표5: 시장 폭 (RSI 대용)
    RSI(14) → Z-score CDF
    """
    close = kospi_df['Close']
    delta = close.diff()
    gain  = delta.where(delta > 0, 0.0)
    loss  = -delta.where(delta < 0, 0.0)
    rsi   = 100 - (100 / (1 + gain.rolling(14).mean() / loss.rolling(14).mean()))
    return zscore_to_score(rsi).rename("breadth")


def calc_6_safe_haven(kospi_df, bond_df):
    """
    지표6: 안전자산 수요 (NEW v3)
    ────────────────────────────
    코스피 20일 수익률 vs KOSEF 국고채10년 ETF(148070.KS) 20일 수익률 비교
    주식 수익률 > 채권 수익률 → 탐욕
    채권 수익률 > 주식 수익률 → 공포

    CNN 대응: Safe Haven Demand (주식 vs 채권 상대 성과)
    """
    common_idx = kospi_df.index.intersection(bond_df.index)

    kospi_ret20 = kospi_df.loc[common_idx, 'Close'].pct_change(20) * 100
    bond_ret20  = bond_df.loc[common_idx, 'Close'].pct_change(20) * 100

    # 주식-채권 수익률 스프레드 (양수 = 탐욕, 음수 = 공포)
    spread = kospi_ret20 - bond_ret20
    return zscore_to_score(spread).rename("safe_haven")


# ============================================================
# 3. 최종 합산 (균등 가중치 1/6)
# ============================================================
def calculate_korea_sentiment_index(kospi_df, kosdaq_df, bond_df):
    scores = pd.DataFrame({
        'volatility':    calc_1_volatility(kospi_df),
        'momentum':      calc_2_momentum(kospi_df),
        'price_strength':calc_3_price_strength(kospi_df),
        'volume':        calc_4_volume(kospi_df),
        'breadth':       calc_5_breadth(kospi_df),
        'safe_haven':    calc_6_safe_haven(kospi_df, bond_df),
    })

    # 균등 가중치 (각 16.7%)
    scores['sentiment_index'] = scores[
        ['volatility','momentum','price_strength','volume','breadth','safe_haven']
    ].mean(axis=1).round(1)

    def grade(x):
        if x <= 20: return "극도의 공포"
        elif x <= 40: return "공포"
        elif x <= 60: return "중립"
        elif x <= 80: return "탐욕"
        else:         return "극도의 탐욕"

    scores['grade'] = scores['sentiment_index'].apply(grade)
    return scores


# ============================================================
# 4. 백테스트
# ============================================================
def backtest(kospi_df, scores_df):
    merged = scores_df.copy()
    merged['close']     = kospi_df['Close']
    merged['return_20d']= kospi_df['Close'].pct_change(20).shift(-20) * 100
    merged['return_60d']= kospi_df['Close'].pct_change(60).shift(-60) * 100
    merged = merged.dropna(subset=['sentiment_index','return_20d'])

    bins   = [0,20,40,60,80,100]
    labels = ['극도의공포(0-20)','공포(20-40)','중립(40-60)','탐욕(60-80)','극도의탐욕(80-100)']
    merged['zone'] = pd.cut(merged['sentiment_index'], bins=bins, labels=labels, include_lowest=True)

    print("="*70)
    print("📊 [v3] 한국 시장 심리 지수 - 10년 백테스트")
    print("    (Z-score CDF 정규화 / 균등가중치 / 안전자산수요 지표)")
    print("="*70)

    print("\n📊 구간별 향후 수익률 (20일 후)")
    print("-"*50)
    r20 = merged.groupby('zone', observed=True)['return_20d'].agg(['mean','median','count','std'])
    r20.columns = ['평균(%)','중앙값(%)','건수','표준편차(%)']
    print(r20.round(2).to_string())

    print("\n📊 구간별 향후 수익률 (60일 후)")
    print("-"*50)
    r60 = merged.dropna(subset=['return_60d']).groupby('zone', observed=True)['return_60d'].agg(['mean','median','count','std'])
    r60.columns = ['평균(%)','중앙값(%)','건수','표준편차(%)']
    print(r60.round(2).to_string())

    print("\n📊 구간별 수익 확률 (20일 후 양수)")
    for z in labels:
        d = merged[merged['zone']==z]['return_20d']
        if len(d): print(f"  {z}: {(d>0).mean()*100:.1f}% ({len(d)}건)")

    print("\n"+"="*70)
    print("공포에 사서 탐욕에 팔라")
    print("="*70)
    f = merged[merged['sentiment_index']<=30]['return_20d']
    n = merged[(merged['sentiment_index']>30)&(merged['sentiment_index']<70)]['return_20d']
    g = merged[merged['sentiment_index']>=70]['return_20d']
    print(f"  공포(<=30)  20일후 평균: {f.mean():.2f}%  승률:{(f>0).mean()*100:.1f}% ({len(f)}건)")
    print(f"  중립(30-70) 20일후 평균: {n.mean():.2f}%  승률:{(n>0).mean()*100:.1f}% ({len(n)}건)")
    print(f"  탐욕(>=70)  20일후 평균: {g.mean():.2f}%  승률:{(g>0).mean()*100:.1f}% ({len(g)}건)")
    corr = merged['sentiment_index'].corr(merged['return_20d'])
    print(f"\n  상관계수 (심리지수 vs 20일후): {corr:.3f}")
    print(f"  (음수 = 공포에 살수록 수익, 지수 정상)")

    return merged, r20


# ============================================================
# 5. 차트
# ============================================================
def plot_charts(kospi_df, scores_df, merged_df, bond_df):
    fig = plt.figure(figsize=(18, 26))
    fig.patch.set_facecolor('#0d0d0d')

    # ── Chart 1: 심리지수 10년 ──────────────────────────────
    ax1 = fig.add_subplot(4,1,1)
    ax1.set_facecolor('#1a1a2e')
    idx  = scores_df.dropna(subset=['sentiment_index']).index
    sent = scores_df.loc[idx,'sentiment_index']

    for lo,hi,col in [(0,20,'#ff4444'),(20,40,'#ff8c00'),(40,60,'#888'),(60,80,'#00cc66'),(80,100,'#00ff88')]:
        ax1.axhspan(lo, hi, alpha=0.12, color=col)

    ax1.plot(idx, sent, color='#00d4ff', lw=1.2, alpha=0.9, zorder=5)

    for lo,hi,col in [(0,20,'#ff4444'),(20,40,'#ff8c00'),(40,60,'#aaa'),(60,80,'#00cc66'),(80,100,'#00ff88')]:
        ax1.fill_between(idx, lo, sent,
                         where=(sent>=lo)&(sent<hi), alpha=0.28, color=col, zorder=4)

    for y,c,ls in [(20,'#f66','--'),(40,'#fa4',':'),(60,'#888',':'),(80,'#4f8','--')]:
        ax1.axhline(y=y, color=c, ls=ls, lw=0.8, alpha=0.6)

    lv   = sent.iloc[-1]; ld = sent.index[-1]
    grade_now = scores_df.loc[ld,'grade']
    ax1.annotate(f'현재: {lv:.0f} ({grade_now})',
                 xy=(ld,lv), xytext=(-80,18), textcoords='offset points',
                 color='white', fontsize=11, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='white', lw=1.5))

    ax1.set_xlim(idx[0], idx[-1]); ax1.set_ylim(0,100)
    ax1.set_ylabel('심리 지수', color='white', fontsize=11)
    ax1.set_title('한국 시장 심리 지수 v3 — 10년 (Z-score CDF / 균등가중)',
                  color='white', fontsize=14, fontweight='bold')
    ax1.tick_params(colors='white')
    for sp in ['top','right']: ax1.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax1.spines[sp].set_color('#444')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.grid(axis='y', color='#333', lw=0.5)

    patches = [mpatches.Patch(color=c, alpha=0.6, label=l) for c,l in [
        ('#ff4444','극도의공포(0-20)'),('#ff8c00','공포(20-40)'),
        ('#aaa','중립(40-60)'),('#00cc66','탐욕(60-80)'),('#00ff88','극도의탐욕(80-100)')]]
    ax1.legend(handles=patches, loc='upper left', fontsize=8,
               facecolor='#1a1a2e', edgecolor='#444', labelcolor='white', ncol=5)

    # ── Chart 2: 코스피 오버레이 ──────────────────────────────
    ax2 = fig.add_subplot(4,1,2)
    ax2.set_facecolor('#1a1a2e')
    ci   = kospi_df.index.intersection(scores_df.dropna(subset=['sentiment_index']).index)
    cl   = kospi_df.loc[ci,'Close']
    sc   = scores_df.loc[ci,'sentiment_index']
    ax2.plot(ci, cl, color='#fff', lw=1.0, alpha=0.75, zorder=3)
    ax2.fill_between(ci, cl.min()*0.95, cl.max()*1.05,
                     where=(sc<=30), alpha=0.22, color='#ff4444', zorder=2, label='공포구간')
    ax2.fill_between(ci, cl.min()*0.95, cl.max()*1.05,
                     where=(sc>=70), alpha=0.22, color='#00ff88', zorder=2, label='탐욕구간')
    ax2.set_xlim(ci[0], ci[-1])
    ax2.set_ylabel('코스피', color='white', fontsize=11)
    ax2.set_title('코스피 지수 (빨강=공포 <=30 / 녹색=탐욕 >=70)', color='white', fontsize=12)
    ax2.tick_params(colors='white')
    for sp in ['top','right']: ax2.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax2.spines[sp].set_color('#444')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.grid(color='#333', lw=0.5, alpha=0.5)
    ax2.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    # ── Chart 3: 6개 지표 개별 ───────────────────────────────
    ax3 = fig.add_subplot(4,1,3)
    ax3.set_facecolor('#1a1a2e')
    cols_info = {
        'volatility':     ('#ff6b6b','변동성(역)'),
        'momentum':       ('#ffd93d','모멘텀'),
        'price_strength': ('#6bcb77','주가강도'),
        'volume':         ('#4d96ff','거래대금'),
        'breadth':        ('#ff922b','시장폭(RSI)'),
        'safe_haven':     ('#cc5de8','안전자산수요(NEW)'),
    }
    for col,(color,label) in cols_info.items():
        if col in scores_df.columns:
            ax3.plot(scores_df.index, scores_df[col],
                     color=color, lw=0.8, alpha=0.8, label=label)
    ax3.axhline(50, color='#666', ls='--', lw=0.8, alpha=0.6)
    ax3.set_xlim(scores_df.index[0], scores_df.index[-1]); ax3.set_ylim(0,100)
    ax3.set_ylabel('지표 점수', color='white', fontsize=11)
    ax3.set_title('6개 지표 개별 추이 (Z-score CDF 정규화)', color='white', fontsize=12)
    ax3.tick_params(colors='white')
    for sp in ['top','right']: ax3.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax3.spines[sp].set_color('#444')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax3.xaxis.set_major_locator(mdates.YearLocator())
    ax3.grid(color='#333', lw=0.5, alpha=0.5)
    ax3.legend(loc='upper left', fontsize=8, facecolor='#1a1a2e',
               edgecolor='#444', labelcolor='white', ncol=3)

    # ── Chart 4: 구간별 수익률 바차트 ────────────────────────
    ax4 = fig.add_subplot(4,1,4)
    ax4.set_facecolor('#1a1a2e')
    zlabels_short = ['극도의공포\n(0-20)','공포\n(20-40)','중립\n(40-60)','탐욕\n(60-80)','극도의탐욕\n(80-100)']
    zlabels_orig  = ['극도의공포(0-20)','공포(20-40)','중립(40-60)','탐욕(60-80)','극도의탐욕(80-100)']
    m20=[]; m60=[]
    for z in zlabels_orig:
        d20 = merged_df[merged_df['zone']==z]['return_20d'].dropna()
        d60 = merged_df[merged_df['zone']==z]['return_60d'].dropna()
        m20.append(d20.mean() if len(d20) else 0)
        m60.append(d60.mean() if len(d60) else 0)

    x = np.arange(len(zlabels_short)); w = 0.35
    b1 = ax4.bar(x-w/2, m20, w, label='20일후', color=['#ff4444' if v<0 else '#00cc66' for v in m20], alpha=0.85, zorder=3)
    b2 = ax4.bar(x+w/2, m60, w, label='60일후', color=['#ff6666' if v<0 else '#44ff88' for v in m60], alpha=0.65, zorder=3)
    ax4.bar_label(b1, fmt='%.1f%%', color='white', fontsize=9, padding=3)
    ax4.bar_label(b2, fmt='%.1f%%', color='#ddd', fontsize=9, padding=3)
    ax4.axhline(0, color='white', lw=0.8, alpha=0.5)
    ax4.set_xticks(x); ax4.set_xticklabels(zlabels_short, color='white', fontsize=9)
    ax4.set_ylabel('평균 수익률 (%)', color='white', fontsize=11)
    ax4.set_title('심리 구간별 향후 평균 수익률', color='white', fontsize=12)
    ax4.tick_params(colors='white')
    for sp in ['top','right']: ax4.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax4.spines[sp].set_color('#444')
    ax4.grid(axis='y', color='#333', lw=0.5, alpha=0.5)
    ax4.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')

    plt.tight_layout(pad=3.0)
    out = "C:/Users/Mario/work/korea_sentiment_v3_chart.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#0d0d0d')
    plt.close()
    print(f"차트 저장: {out}")
    return out


# ============================================================
# 6. 실행
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("한국 시장 심리 지수 v3 - 10년 백테스트")
    print("Z-score CDF / 균등가중 / 안전자산수요")
    print("="*60)

    print("\n[1] 데이터 다운로드...")
    kospi, kosdaq, bond = fetch_data(period="10y")
    print(f"    코스피:{len(kospi)}일 / 코스닥:{len(kosdaq)}일 / 채권ETF:{len(bond)}일")

    # 채권 ETF 데이터 부족 시 경고
    if len(bond) < 200:
        print("    경고: 채권 ETF 데이터 부족 - 안전자산 지표 신뢰도 낮을 수 있음")

    print("\n[2] 심리 지수 계산...")
    scores = calculate_korea_sentiment_index(kospi, kosdaq, bond)
    scores.to_csv("C:/Users/Mario/work/korea_sentiment_v3.csv")

    latest = scores.dropna(subset=['sentiment_index']).iloc[-1]
    ldate  = scores.dropna(subset=['sentiment_index']).index[-1]

    print(f"\n📈 최신 심리 지수 [{ldate.strftime('%Y-%m-%d')}]")
    print(f"   종합: {latest['sentiment_index']:.1f} → {latest['grade']}")
    print(f"   ┌ 변동성(역):      {latest['volatility']:.1f}")
    print(f"   ├ 모멘텀:         {latest['momentum']:.1f}")
    print(f"   ├ 주가강도:       {latest['price_strength']:.1f}")
    print(f"   ├ 거래대금:       {latest['volume']:.1f}")
    print(f"   ├ 시장폭(RSI):    {latest['breadth']:.1f}")
    print(f"   └ 안전자산수요:   {latest['safe_haven']:.1f}  ← NEW")

    print("\n[3] 백테스트...")
    merged, result = backtest(kospi, scores)

    print("\n[4] 차트 생성...")
    chart_path = plot_charts(kospi, scores, merged, bond)

    print("\n완료!")
    print(f"   CSV:  korea_sentiment_v3.csv")
    print(f"   차트: {chart_path}")
