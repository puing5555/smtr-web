import requests, json

api_key = 'sample'

# 721Y001 전체 아이템 목록 (page by page, max 10 per request)
# sample 키는 최대 10건만 가능하므로 여러 번 시도
print('=== 721Y001 모든 아이템 탐색 ===')
stat_code = '721Y001'

# 전체 목록 조회
url = f'https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/10/{stat_code}'
r = requests.get(url, timeout=10)
data = r.json()
total = data.get('StatisticItemList', {}).get('list_total_count', 0)
print(f'총 {total}개 아이템')

items = data.get('StatisticItemList', {}).get('row', [])
for item in items:
    code = item.get('ITEM_CODE', '')
    name = item.get('ITEM_NAME', '')
    cycle = item.get('CYCLE', '')
    if 'M' in cycle or 'D' in cycle:
        print(f'{code}: {name} ({cycle})')

print('\n=== 각 항목 월별 데이터 확인 ===')
# 모든 item_code에 대해 월별 데이터 시도
for item in items:
    code = item.get('ITEM_CODE', '')
    name = item.get('ITEM_NAME', '')
    # 월별 데이터 시도
    url2 = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/3/{stat_code}/M/202501/202502/{code}'
    r2 = requests.get(url2, timeout=5)
    d2 = r2.json()
    if 'StatisticSearch' in d2 and d2['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = d2['StatisticSearch']['row']
        print(f'HIT M: {code} ({name}) = {rows[-1].get("DATA_VALUE","")} ({rows[-1].get("TIME","")})')

# 722Y001 아이템 목록
print('\n=== 722Y001 일별 금리 ===')
url3 = f'https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/10/722Y001'
r3 = requests.get(url3, timeout=10)
data3 = r3.json()
items3 = data3.get('StatisticItemList', {}).get('row', [])
for item in items3:
    code = item.get('ITEM_CODE', '')
    name = item.get('ITEM_NAME', '')
    cycle = item.get('CYCLE', '')
    print(f'{code}: {name} ({cycle})')
