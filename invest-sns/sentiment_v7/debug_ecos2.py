import requests, json

api_key = 'sample'

# 721Y001의 회사채 코드 찾기 - page 2-9
for page in range(1, 10):
    start = (page-1)*10 + 1
    end = page*10
    url = f'https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/10/721Y001'
    # Hmm, doesn't support pagination
    break

# 일별 시장금리 통계 - 다른 stat code
# 실제로 한국은행 ECOS에서 일별 회사채 금리 stat code
# 검색: https://ecos.bok.or.kr/api/StatisticSearch/sample/json/kr/1/10/722Y001/D/20250101/20250110/4060100
for stat_code in ['721Y001', '722Y001', '817Y002']:
    for item_code in ['4060100', '4060200', '5030000', '5040000', 'AA3', 'BBB3']:
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/3/{stat_code}/M/202501/202502/{item_code}'
        r = requests.get(url, timeout=5)
        data = r.json()
        if 'StatisticSearch' in data and data['StatisticSearch'].get('list_total_count', 0) > 0:
            rows = data['StatisticSearch']['row']
            print(f'HIT: {stat_code}/{item_code} -> {rows[0]}')
