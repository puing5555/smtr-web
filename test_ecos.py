"""
ECOS API 테스트 - 추가 지표 탐색
신용잔고, 고객예탁금, 외국인 순매수 등
"""
import requests
import json
import pandas as pd

api_key = "sample"

def ecos_fetch(stat_code, period_type, start, end, item_code, max_count=10):
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/{max_count}/{stat_code}/{period_type}/{start}/{end}/{item_code}"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if 'StatisticSearch' in data:
            rows = data['StatisticSearch'].get('row', [])
            return rows
        else:
            return data  # error info
    except Exception as e:
        return {'error': str(e)}

def search_stats(keyword):
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/100/902Y001/M/202401/202601/0"
    # Use StatisticTableList instead
    url2 = f"https://ecos.bok.or.kr/api/StatisticTableList/{api_key}/json/kr/1/100/{keyword}"
    r = requests.get(url2, timeout=15)
    try:
        data = r.json()
        if 'StatisticTableList' in data:
            return data['StatisticTableList'].get('row', [])
    except:
        pass
    return []

# 1. 투자자예탁금 검색
print("=== 1. 고객예탁금/투자자예탁금 ===")
for kw in ['예탁금', '신용', '융자잔', '위탁']:
    results = search_stats(kw)
    if results:
        for r in results[:5]:
            print(f"  {r.get('STAT_CODE', '')} | {r.get('STAT_NAME', '')} | {r.get('CYCLE', '')}")
    else:
        print(f"  '{kw}': no results")

# 2. 증권 관련 통계 탐색
print("\n=== 2. 증권시장 통계 ===")
for kw in ['증권', '주식', '코스피', '파생']:
    results = search_stats(kw)
    if results:
        for r in results[:3]:
            print(f"  {r.get('STAT_CODE', '')} | {r.get('STAT_NAME', '')} | {r.get('CYCLE', '')}")

# 3. Try known ECOS code for stock market
print("\n=== 3. ECOS 주식시장 직접 테스트 ===")
known_codes = [
    # 자금순환
    ('902Y001', 'Q', '20230101', '20260101', '0', '주식 관련'),
    # 통화금융 - 예금은행
    ('101Y002', 'M', '202301', '202601', '0', '예금은행'),
]

# Test StatisticItemList for known stat codes
for stat_code, _, _, _, _, desc in known_codes[:2]:
    url = f"https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/100/{stat_code}"
    r = requests.get(url, timeout=10)
    try:
        data = r.json()
        if 'StatisticItemList' in data:
            items = data['StatisticItemList'].get('row', [])
            print(f"\n{stat_code} ({desc}) items:")
            for item in items[:5]:
                print(f"  {item}")
    except Exception as e:
        print(f"Error {stat_code}: {e}")

# 4. Try ECOS 단기금융 - 콜금리, 신용거래
print("\n=== 4. 단기금융 ===")
url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/10/817Y002/D/20260101/20260306/010300000"
r = requests.get(url, timeout=10)
data = r.json()
if 'StatisticSearch' in data:
    rows = data['StatisticSearch'].get('row', [])
    if rows:
        print(f"AA- daily bond data: {rows[-3:]}")
    else:
        print("No rows returned")
        
# 5. Try FSS API for margin balance
print("\n=== 5. FSS/금융감독원 API ===")
urls_fss = [
    'https://openapi.fss.or.kr/openapi/service/SecDis/getStoMarMar',
    'https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo',
]
for url in urls_fss:
    try:
        r = requests.get(url, timeout=10)
        print(f'{r.status_code}: {url}')
    except Exception as e:
        print(f'Error: {url}: {e}')
