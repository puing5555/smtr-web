import requests

api_key = 'sample'
# 817Y002에서 회사채 일별 코드 찾기
for code in ['010300000', '010310000', '010320000', '010330000', '010400000', '010410000', '010420000',
             '010500000', '010510000', '010520000', '010530000']:
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/2/817Y002/D/20260201/20260306/{code}'
    r = requests.get(url, timeout=5)
    d = r.json()
    if 'StatisticSearch' in d and d['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = d['StatisticSearch']['row']
        name = rows[0].get('ITEM_NAME1', '')
        val = rows[0].get('DATA_VALUE', '')
        print(f'817Y002/{code}: {name}: {val}')

# 721Y001 월별 회사채
print('\n=== 721Y001 회사채 월별 ===')
for code in ['7020000', '7030000']:
    url2 = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/5/721Y001/M/202501/202603/{code}'
    r2 = requests.get(url2, timeout=10)
    d2 = r2.json()
    if 'StatisticSearch' in d2 and d2['StatisticSearch'].get('list_total_count', 0) > 0:
        rows2 = d2['StatisticSearch']['row']
        name = rows2[0].get('ITEM_NAME1', '')
        print(f'{code} ({name}):')
        for row in rows2:
            print(f'  {row.get("TIME")}: {row.get("DATA_VALUE")}')
