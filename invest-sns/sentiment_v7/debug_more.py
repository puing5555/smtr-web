import requests, json
import yfinance as yf
from datetime import datetime, timedelta

print('=== VKOSPI yfinance 시도 ===')
# VKOSPI ticker 찾기
for ticker in ['^VKOSPI', 'VKOSPI', '^VIX.KS', '180721.KS']:
    try:
        df = yf.download(ticker, period='5d', progress=False)
        if not df.empty:
            print(f'HIT: {ticker} -> {df.tail(2)}')
        else:
            print(f'빈 데이터: {ticker}')
    except Exception as e:
        print(f'오류 {ticker}: {e}')

print()
print('=== ECOS 월별 회사채 금리 (올바른 코드) ===')
# 721Y001 통계 - 회사채 3년 AA-, BBB- 코드 찾기
# 공개된 ECOS 문서에서의 코드: 
# 회사채(AA-,3년): 4020000, 4060100 이라는 정보 있음
api_key = 'sample'
for stat, item, label in [
    ('721Y001', '4020000', '4020000'),
    ('721Y001', '4030000', '4030000'),
    ('721Y001', '4040000', '4040000'), 
    ('721Y001', '4050000', '4050000'),
    ('721Y001', '4060000', '4060000'),
    ('721Y001', '4070000', '4070000'),
    ('721Y001', '4080000', '4080000'),
    ('721Y001', '4090000', '4090000'),
    ('721Y001', '6010000', '6010000'),
    ('721Y001', '6020000', '6020000'),
    ('721Y001', '6030000', '6030000'),
    ('721Y001', '6040000', '6040000'),
]:
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/2/{stat}/M/202501/202502/{item}'
    r = requests.get(url, timeout=5)
    data = r.json()
    if 'StatisticSearch' in data and data['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = data['StatisticSearch']['row']
        name = rows[0].get('ITEM_NAME1', '')
        val = rows[0].get('DATA_VALUE', '')
        print(f'{stat}/{item} ({label}): {name} = {val}')

print()
print('=== 네이버 모바일 시장폭 ===')
headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)', 'Referer': 'https://m.stock.naver.com/'}
urls = [
    'https://m.stock.naver.com/api/index/KOSPI/nhn-rising-falling',
    'https://m.stock.naver.com/api/marketindex/KOSPI/stock-count',
    'https://m.stock.naver.com/api/marketindex/rising-count?marketType=KOSPI',
]
for u in urls:
    r = requests.get(u, headers=headers, timeout=5)
    print(f'{u[-50:]}: {r.status_code} {r.text[:200]}')
