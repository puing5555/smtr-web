import requests, json

api_key = 'sample'

# 721Y001 아이템 목록에서 회사채 찾기
# sample은 최대 10건이므로 다른 방법 필요
# ECOS 웹에서 회사채 AA- 코드 확인: 
# stat_code = 817Y002 (기업금융지표), 721Y001 (시장금리)
# 회사채 3년 AA- : 4020000, BBB- : 4030000 이라는 정보도 있음

test_codes = [
    ('721Y001', '4020000', '회사채3년AA-예상1'),
    ('721Y001', '4030000', '회사채3년BBB-예상1'),
    ('721Y001', '4040000', '코드4040000'),
    ('721Y001', '4050000', '코드4050000'),
    ('721Y001', '4060000', '코드4060000'),
    ('721Y001', '6010000', '회사채예상'),
    ('721Y001', '6020000', '회사채예상2'),
    ('817Y002', '0AA3', '817Y002-AA3'),
    ('817Y002', '0BBB3', '817Y002-BBB3'),
]

for stat_code, item_code, label in test_codes:
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/3/{stat_code}/M/202501/202502/{item_code}'
    r = requests.get(url, timeout=5)
    data = r.json()
    if 'StatisticSearch' in data and data['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = data['StatisticSearch']['row']
        print(f'HIT {label}: {stat_code}/{item_code} -> item_name={rows[0].get("ITEM_NAME1","")}, val={rows[0].get("DATA_VALUE","")}')
    else:
        result = data.get('RESULT', {}).get('CODE', 'unknown')
        # print(f'MISS {label}: {result}')
