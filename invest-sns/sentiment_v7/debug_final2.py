import requests, json
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 817Y002 일별 데이터 범위 확인
print('=== ECOS 817Y002 데이터 범위 ===')
api_key = 'sample'
for code, label in [('010300000', 'AA-'), ('010320000', 'BBB-')]:
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/5/817Y002/D/20260201/20260307/{code}'
    r = requests.get(url, timeout=10)
    d = r.json()
    if 'StatisticSearch' in d and d['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = d['StatisticSearch']['row']
        print(f'{label}: 총 {len(rows)}건')
        for row in rows[-3:]:
            print(f'  {row.get("TIME")}: {row.get("DATA_VALUE")}')

# 2. yfinance 실현변동성 (VKOSPI 대체)
print('\n=== KOSPI 실현변동성 (VKOSPI 대체) ===')
ks = yf.download("^KS11", period="120d", progress=False, auto_adjust=True)
if not ks.empty:
    close = ks['Close'].squeeze()
    returns = close.pct_change().dropna()
    # 20일 실현변동성 (연율화)
    vol20 = returns.rolling(20).std() * np.sqrt(252) * 100
    current_vol = float(vol20.iloc[-1])
    ma50_vol = float(vol20.iloc[-50:].mean())
    print(f'현재 변동성: {current_vol:.2f}%, 50일 평균: {ma50_vol:.2f}%')
    diff = (current_vol - ma50_vol) / ma50_vol
    print(f'괴리율: {diff:.4f}')

# 3. yfinance 외국인 수급 대체 (코스피 ETF 자금흐름 프록시)
print('\n=== yfinance 사용 가능한 한국 ETF/지표 ===')
for ticker in ['069500.KS', '226490.KS', '^KS200', 'EWY']:
    try:
        df = yf.download(ticker, period='10d', progress=False, auto_adjust=True)
        if not df.empty:
            close = df['Close'].squeeze()
            print(f'{ticker}: 최신={float(close.iloc[-1]):.2f}, 기간={df.index[0].date()}~{df.index[-1].date()}')
    except Exception as e:
        print(f'{ticker}: 오류 {e}')

# 4. pykrx bond 모듈 테스트
print('\n=== pykrx bond ===')
try:
    from pykrx import bond
    print(dir(bond))
    # 채권 금리 조회
    df_bond = bond.get_otc_treasury_yields_in_bps('20260201', '20260306')
    print(df_bond)
except Exception as e:
    print(f'오류: {e}')

# 5. EWY (iShares MSCI South Korea ETF) 외국인 수급 프록시
print('\n=== EWY 외국인 수급 프록시 ===')
ewy = yf.download('EWY', period='30d', progress=False, auto_adjust=True)
if not ewy.empty:
    close_ewy = ewy['Close'].squeeze()
    ret5d = float((close_ewy.iloc[-1] / close_ewy.iloc[-5]) - 1) * 100
    print(f'EWY 5일 수익률: {ret5d:.2f}%')
