import requests, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Origin': 'https://finance.naver.com',
    'Referer': 'https://finance.naver.com/',
}

# 1. 네이버 시장 통계 API (새 버전)
print('=== 네이버 시장 통계 API ===')
for path in [
    'https://m.stock.naver.com/api/index/KOSPI/quotations',
    'https://m.stock.naver.com/api/index/KOSPI/groups/stock-count',
    'https://m.stock.naver.com/api/index/KOSPI/count',
]:
    r = requests.get(path, headers=headers, timeout=5)
    print(f'{path[-50:]}: {r.status_code} {r.text[:200]}')
    print()

# 2. 네이버 금융 API v2
print('=== 네이버 금융 v2 ===')
for path in [
    'https://polling.finance.naver.com/api/realtime/domestic/index/KOSPI',
    'https://stock.pstatic.net/stock-index/api/v1/KOSPI/days',
    'https://finance.naver.com/sise/sisedata.naver?code=KOSPI',
]:
    r = requests.get(path, headers=headers, timeout=5)
    print(f'{path[-60:]}: {r.status_code} {r.text[:300]}')
    print()

# 3. 네이버 코스피 상세 - 상승/하락 포함
print('=== 네이버 코스피 상세 HTML ===')
r3 = requests.get('https://finance.naver.com/sise/sise_index_detail.naver?code=KOSPI',
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.naver.com/'}, timeout=10)
if r3.status_code == 200:
    text = r3.content.decode('euc-kr', errors='replace')
    # 상승/하락/보합 찾기
    matches = re.findall(r'(상승|하락|보합)[^<]{0,30}(\d{2,3})', text)
    print('상승/하락:', matches[:10])
    
    # 더 넓은 탐색
    for keyword in ['상승종목', '하락종목', '상승 종목', '하락 종목', 'adv', 'dec', 'rising', 'falling']:
        idx = text.find(keyword)
        if idx > 0:
            print(f'{keyword} 컨텍스트:', text[idx-50:idx+200])

# 4. FnGuide / 외부 API
print('\n=== FnGuide 시장 데이터 ===')
r4 = requests.get('https://www.fnguide.com/home/index',
    headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
print(f'status={r4.status_code}')
