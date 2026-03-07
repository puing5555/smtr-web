import requests, json

api_key = 'sample'

# 721Y001 전체 item 목록 조회 (D=일별 있는 것만)
# 월별로 아이템 코드 브루트포스 검색
# ECOS 공식 회사채 코드: 
# stat_code = 817Y002 = 채권시가평가 수익률
# 또는 stat_code = 721Y001

# 공개된 자료에서 회사채 AA- 코드를 찾아보자
# 한국은행 통계 코드 검색
search_url = f'https://ecos.bok.or.kr/api/StatisticWord/{api_key}/json/kr/1/10/회사채'
r = requests.get(search_url, timeout=10)
print('회사채 검색:', r.text[:500])

print()
# 직접 알려진 코드들 시도
known_codes = [
    ('817Y002', 'AA3', '817Y002-AA3'),
    ('817Y002', 'BBB3', '817Y002-BBB3'),
    ('817Y002', 'AA-3', '817Y002-AA-3'),
    ('817Y002', 'BBB-3', '817Y002-BBB-3'),
]

for stat_code, item_code, label in known_codes:
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/3/{stat_code}/M/202501/202502/{item_code}'
    r = requests.get(url, timeout=5)
    data = r.json()
    if 'StatisticSearch' in data and data['StatisticSearch'].get('list_total_count', 0) > 0:
        rows = data['StatisticSearch']['row']
        print(f'HIT {label}: {rows[0].get("ITEM_NAME1","")}, val={rows[0].get("DATA_VALUE","")}')
    else:
        print(f'MISS {label}: {data.get("RESULT", {}).get("CODE", "")}')
