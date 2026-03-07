"""
Alternative data sources for missing indicators
- 52주 신고가/신저가: yfinance top KOSPI stocks
- 시장폭: yfinance breadth
- 신용잔고/고객예탁금: ECOS with correct codes
- 풋/콜: proxy via VIX or vol ratio
"""
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ================================================================
# 1. ECOS with correct codes for financial data
# ================================================================
print("=== ECOS 금융통계 탐색 ===")

api_key = "sample"

# Try 증권 거래동향 from ECOS
# Known stat codes for securities markets
ecos_codes_to_try = [
    # 주식 관련
    ("902Y001", "Q", "20230101", "20251201"),  # 자금순환
    # 신용거래 융자잔고 - try these
    ("402Y002", "M", "202301", "202601"),  # 금리
    ("042Y031", "M", "202301", "202601"),  # 일반은행
]

for stat_code, period, start, end in ecos_codes_to_try:
    url = f"https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/20/{stat_code}"
    r = requests.get(url, timeout=10)
    try:
        data = r.json()
        if 'StatisticItemList' in data:
            items = data['StatisticItemList'].get('row', [])
            if items:
                print(f"\n{stat_code} items: {items[:3]}")
    except Exception as e:
        print(f"Error {stat_code}: {e}")

# ================================================================
# 2. 52주 신고가/신저가 from yfinance (top KOSPI stocks)
# ================================================================
print("\n=== 52주 신고가/신저가 (yfinance) ===")

# Top KOSPI stocks
KOSPI_TICKERS = [
    '005930.KS',  # Samsung
    '000660.KS',  # SK Hynix
    '207940.KS',  # Samsung Bio
    '005380.KS',  # Hyundai Motor
    '051910.KS',  # LG Chem
    '035420.KS',  # NAVER
    '006400.KS',  # Samsung SDI
    '373220.KS',  # LG Energy
    '000270.KS',  # Kia
    '068270.KS',  # Celltrion
    '105560.KS',  # KB Financial
    '055550.KS',  # Shinhan Financial  
    '012330.KS',  # Hyundai Mobis
    '028260.KS',  # Samsung C&T
    '066570.KS',  # LG Electronics
    '003550.KS',  # LG Corp
    '096770.KS',  # SK Innovation
    '017670.KS',  # SK Telecom
    '030200.KS',  # KT Corp
    '009150.KS',  # Samsung Electro-Mech
]

print(f"Downloading {len(KOSPI_TICKERS)} stocks...")
df = yf.download(KOSPI_TICKERS, period='1y', progress=False, auto_adjust=True)
print(f"Shape: {df.shape}")

if not df.empty:
    close = df['Close']
    print(f"Close shape: {close.shape}")
    
    latest = close.iloc[-1]
    high_52w = close.rolling(252, min_periods=200).max().iloc[-1]
    low_52w = close.rolling(252, min_periods=200).min().iloc[-1]
    
    # Near 52-week high: within 5%
    near_high = ((latest / high_52w) >= 0.95).sum()
    near_low = ((latest / low_52w) <= 1.05).sum()
    total = latest.count()
    
    print(f"\n52주 신고가 근접: {near_high}/{total}")
    print(f"52주 신저가 근접: {near_low}/{total}")
    print(f"신고가/신저가 비율: {near_high/(near_low+1):.2f}")
    
    # Market breadth: stocks above 200-day MA
    ma200 = close.rolling(200).mean().iloc[-1]
    above_ma200 = (latest > ma200).sum()
    total_valid = (ma200.notna() & latest.notna()).sum()
    print(f"\n200일 이평 위: {above_ma200}/{total_valid}")

# ================================================================
# 3. 풋/콜 비율 proxy via KOSPI200 options in yfinance
# ================================================================
print("\n=== 풋/콜 비율 proxy ===")
# Try to get options data via yfinance
try:
    k200 = yf.Ticker("^KS200")
    opts = k200.options
    print(f"KS200 options expiries: {opts[:3] if opts else 'NONE'}")
except Exception as e:
    print(f"KS200 options: {e}")

# Use VIX as global fear proxy
try:
    vix = yf.download("^VIX", period="90d", progress=False, auto_adjust=True)
    if not vix.empty:
        print(f"VIX latest: {vix['Close'].iloc[-1]:.2f}")
except Exception as e:
    print(f"VIX: {e}")

# VKOSPI from naver - check the AJAX endpoint
print("\n=== VKOSPI alternatives ===")
headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.naver.com/'}

# Try KRX VKOSPI through their chart API
urls = [
    'https://fchart.stock.naver.com/sise.nhn?symbol=VKOSPI&timeframe=day&count=60&requestType=0',
    'https://fchart.stock.naver.com/sise.nhn?symbol=VKOSPI&timeframe=day&count=60',
]
for url in urls:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url[:70]}')
    if r.status_code == 200 and len(r.content) > 100:
        print(f'  Size: {len(r.content)}, Content: {r.text[:300]}')

# 4. Naver finance chart API for indices
urls2 = [
    'https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=10&requestType=0',
    'https://fchart.stock.naver.com/sise.nhn?symbol=VKOSPI&timeframe=day&count=5&requestType=0',
]
for url in urls2:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url[:70]}')
    if r.status_code == 200:
        print(f'  {r.text[:200]}')
