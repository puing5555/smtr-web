import requests, json

api_key = 'sample'

# 722Y001 = 시장금리(일)
url = f'https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/10/722Y001'
r = requests.get(url, timeout=10)
data = r.json()
items = data.get('StatisticItemList', {}).get('row', [])
total = data.get('StatisticItemList', {}).get('list_total_count', 0)
print(f'총 {total}개 아이템')
for item in items:
    name = item.get('ITEM_NAME', '')
    code = item.get('ITEM_CODE', '')
    cycle = item.get('CYCLE', '')
    print(f'{code}: {name} ({cycle})')

print()
# 실제 데이터 조회 - 회사채 3년 AA-
# ECOS에서 회사채 코드: 5020000=CP91일, 4060100=회사채3년AA-, 4060200=회사채3년BBB-
for code, label in [('4060100', '회사채3년AA-'), ('4060200', '회사채3년BBB-'), ('5030000', '5030000'), ('5040000', '5040000')]:
    url2 = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/3/722Y001/D/20260201/20260306/{code}'
    r2 = requests.get(url2, timeout=10)
    print(f'{label}: {r2.text[:200]}')
    print()
