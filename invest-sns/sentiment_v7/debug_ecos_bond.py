import requests, json

api_key = 'sample'

# 817Y002 아이템 목록
print('=== 817Y002 ===')
url = f'https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/10/817Y002'
r = requests.get(url, timeout=10)
data = r.json()
print(data.get('RESULT', data.get('StatisticItemList', {}).get('list_total_count', '?')))
items = data.get('StatisticItemList', {}).get('row', [])
for item in items:
    print(item.get('ITEM_CODE'), item.get('ITEM_NAME'), item.get('CYCLE'))

# 721Y001에서 숫자 코드 범위 탐색
print('\n=== 721Y001 코드 범위 탐색 ===')
# item code들이 어디까지 있나 확인
for prefix in ['40', '50', '60', '70']:
    for suffix in ['00000', '10000', '20000', '30000', '40000', '50000', '60000']:
        code = prefix + suffix
        url2 = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/2/721Y001/M/202601/202602/{code}'
        r2 = requests.get(url2, timeout=5)
        d2 = r2.json()
        if 'StatisticSearch' in d2 and d2['StatisticSearch'].get('list_total_count', 0) > 0:
            rows = d2['StatisticSearch']['row']
            name = rows[0].get('ITEM_NAME1', '')
            val = rows[0].get('DATA_VALUE', '')
            print(f'HIT: {code} = {name} -> {val}')

# 한국은행 회사채 금리 공개 페이지 확인
print('\n=== 한국은행 ECOS 시장금리 ===')
# 시장금리(일) - 회사채
for code in ['0AA3', '0BBB3', 'AA3Y', 'BBB3Y', '1320000', '1330000', '1340000']:
    url3 = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/2/722Y001/D/20260201/20260306/{code}'
    r3 = requests.get(url3, timeout=5)
    d3 = r3.json()
    if 'StatisticSearch' in d3 and d3['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = d3['StatisticSearch']['row']
        name = rows[0].get('ITEM_NAME1', '')
        val = rows[0].get('DATA_VALUE', '')
        print(f'HIT: 722Y001/{code} = {name} -> {val}')
