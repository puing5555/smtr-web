import requests, json, re

headers_pc = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://finance.naver.com/',
    'Accept-Charset': 'euc-kr'
}

# 네이버 시장 시세 페이지
url = 'https://finance.naver.com/sise/'
r = requests.get(url, headers=headers_pc, timeout=10)
if r.status_code == 200:
    text = r.content.decode('euc-kr', errors='replace')
    # 상승/하락 패턴 찾기
    # <dt>상승</dt><dd>xxx</dd>
    dt_dd = re.findall(r'<dt>(상승|하락|보합)</dt>\s*<dd[^>]*>(\d+)', text)
    print('dt/dd 패턴:', dt_dd[:10])
    
    # span 패턴
    span_pattern = re.findall(r'>(상승|하락|보합)<[^>]+>\s*(\d+)', text)
    print('span 패턴:', span_pattern[:10])
    
    # 숫자 조합 패턴 
    combined = re.findall(r'(상승|하락|보합)[^<\d]{0,20}(\d{2,3})', text)
    print('combined:', combined[:10])
    
    # HTML 일부 출력
    idx = text.find('상승')
    if idx > 0:
        print('\n상승 컨텍스트:', text[idx-100:idx+200])

print()

# 네이버 금융 KOSPI 요약 API
url2 = 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI'
r2 = requests.get(url2, headers=headers_pc, timeout=10)
if r2.status_code == 200:
    text2 = r2.content.decode('euc-kr', errors='replace')
    # 상승/하락 찾기
    dt_dd2 = re.findall(r'(상승|하락|보합)\D{1,20}(\d{3,})', text2)
    print('KOSPI 페이지:', dt_dd2[:10])
    idx2 = text2.find('상승')
    if idx2 > 0:
        print('\n상승 컨텍스트2:', text2[idx2-50:idx2+200])
