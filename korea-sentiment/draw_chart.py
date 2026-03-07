import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import yfinance as yf

# 데이터 로드
df = pd.read_csv('korea_sentiment_index.csv', index_col=0, parse_dates=True)

kospi = yf.download('^KS11', period='10y', auto_adjust=True, progress=False)
if isinstance(kospi.columns, pd.MultiIndex):
    kospi.columns = kospi.columns.droplevel(1)

# 한글 폰트
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                gridspec_kw={'height_ratios': [2, 1], 'hspace': 0.05})
fig.patch.set_facecolor('#0D1117')
for ax in [ax1, ax2]:
    ax.set_facecolor('#0D1117')
    ax.tick_params(colors='#8B949E')
    for spine in ax.spines.values():
        spine.set_color('#30363D')

# 상단: 코스피
ax1.plot(kospi.index, kospi['Close'], color='#58A6FF', linewidth=1.5, zorder=3)
ax1.fill_between(kospi.index, kospi['Close'], kospi['Close'].min() * 0.95,
                 alpha=0.15, color='#58A6FF')
ax1.set_ylabel('코스피', color='#8B949E', fontsize=12)
ax1.yaxis.set_tick_params(labelcolor='#8B949E')
ax1.grid(axis='y', color='#21262D', linewidth=0.5)
ax1.set_title('한국 시장 심리 지수 vs 코스피 (10년)', color='#E6EDF3', fontsize=15, fontweight='bold', pad=15)

# 하단: 심리 지수 배경
idx = df.index
si = df['sentiment_index']

zones = [
    (0,  20,  '#EF4444', 0.25),
    (20, 40,  '#F97316', 0.20),
    (40, 60,  '#6B7280', 0.15),
    (60, 80,  '#86EFAC', 0.20),
    (80, 100, '#22C55E', 0.25),
]
for lo, hi, color, alpha in zones:
    ax2.axhspan(lo, hi, color=color, alpha=alpha, zorder=0)

ax2.plot(idx, si, color='#F0E68C', linewidth=1.8, zorder=3)
ax2.fill_between(idx, si, 0, alpha=0.2, color='#F0E68C', zorder=2)
ax2.set_ylim(0, 100)
ax2.set_ylabel('심리 지수', color='#8B949E', fontsize=12)
ax2.yaxis.set_tick_params(labelcolor='#8B949E')
ax2.grid(axis='y', color='#21262D', linewidth=0.5, zorder=1)
for y, color in [(20,'#EF4444'),(40,'#F97316'),(60,'#86EFAC'),(80,'#22C55E')]:
    ax2.axhline(y=y, color=color, linewidth=0.6, linestyle='--', alpha=0.6)

# 주요 이벤트
events = [
    ('2020-03-19', '코로나\n폭락', '#FF6B6B'),
    ('2022-10-01', '금리\n쇼크', '#FFB347'),
]
for date_str, label, color in events:
    d = pd.Timestamp(date_str)
    for ax in [ax1, ax2]:
        ax.axvline(x=d, color=color, linewidth=1.2, linestyle='--', alpha=0.8, zorder=4)
    ax1.text(d, kospi['Close'].max() * 0.96, label,
             color=color, fontsize=9, ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1117', edgecolor=color, alpha=0.8),
             zorder=5)

# 현재값 표시
last_si = si.iloc[-1]
last_date = si.index[-1]
grade = df['grade'].iloc[-1]
ax2.annotate(f'현재 {last_si:.1f} ({grade})',
             xy=(last_date, last_si),
             xytext=(-100, 25), textcoords='offset points',
             color='#F0E68C', fontsize=9, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#F0E68C', lw=1.2),
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#0D1117', edgecolor='#F0E68C', alpha=0.9),
             zorder=6)

# 범례
legend_items = [
    mpatches.Patch(color='#EF4444', alpha=0.6, label='극도의 공포 (0~20)'),
    mpatches.Patch(color='#F97316', alpha=0.6, label='공포 (20~40)'),
    mpatches.Patch(color='#6B7280', alpha=0.5, label='중립 (40~60)'),
    mpatches.Patch(color='#86EFAC', alpha=0.6, label='탐욕 (60~80)'),
    mpatches.Patch(color='#22C55E', alpha=0.6, label='극도의 탐욕 (80~100)'),
]
ax2.legend(handles=legend_items, loc='upper left', fontsize=8,
           facecolor='#161B22', edgecolor='#30363D',
           labelcolor='#8B949E', ncol=5)
ax2.tick_params(axis='x', colors='#8B949E', labelsize=9)

plt.savefig('korea_sentiment_chart.png', dpi=150, bbox_inches='tight',
            facecolor='#0D1117', edgecolor='none')
print('saved')
