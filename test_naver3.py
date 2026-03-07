"""
심층 Naver Finance 테스트
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Referer': 'https://finance.naver.com/',
}

# 1. Market breadth from Naver sise main page
print("=== KOSPI Advancing/Declining Counts ===")
r = requests.get('https://finance.naver.com/sise/', headers=headers, timeout=15)
text = r.content.decode('euc-kr', errors='replace')

# Extract rising/falling counts using regex (numbers near 상승/하락 keywords)  
# Look for patterns like 상승:NNN 하락:NNN
rising_match = re.findall(r'상승.*?(\d{3,4})', text)
falling_match = re.findall(r'하락.*?(\d{3,4})', text)
print(f'Rising patterns: {rising_match[:5]}')
print(f'Falling patterns: {falling_match[:5]}')

# Also look for the overall market summary div
soup = BeautifulSoup(text, 'html.parser')

# Check for market breadth widget
divs = soup.find_all('div', {'class': True})
for div in divs:
    class_name = ' '.join(div.get('class', []))
    text_content = div.get_text(strip=True)
    if '상승' in text_content and '하락' in text_content and len(text_content) < 200:
        print(f'Breadth div ({class_name}): {text_content[:150]}')

# 2. Try mobile naver for better API access
print("\n=== Mobile Naver KOSPI Stats ===")
urls_mobile = [
    'https://m.stock.naver.com/api/index/KOSPI/basic',
    'https://m.stock.naver.com/api/index/KOSDAQ/basic',
]
for url in urls_mobile:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url}')
    if r.status_code == 200:
        import json
        try:
            data = r.json()
            print(f'  Keys: {list(data.keys())}')
            # Look for breadth data
            for k, v in data.items():
                if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
                    print(f'  {k}: {v}')
        except:
            print(f'  Raw: {r.text[:200]}')

# 3. Naver investor deal trend for CURRENT data (no date)
print("\n=== Investor Trend (no date param) ===")
r = requests.get('https://finance.naver.com/sise/investorDealTrendDay.naver', 
    params={'sosok': '0'}, headers=headers, timeout=10)
text = r.content.decode('euc-kr', errors='replace')
soup = BeautifulSoup(text, 'html.parser')

# Find table rows
for table in soup.find_all('table'):
    rows = table.find_all('tr')
    print(f'Table rows: {len(rows)}')
    for row in rows[:10]:
        cells = row.find_all(['td', 'th'])
        if cells:
            cell_texts = [c.get_text(strip=True) for c in cells]
            # Filter out empty rows
            non_empty = [t for t in cell_texts if t and t != '\xa0']
            if non_empty:
                print(f'  {non_empty[:8]}')

# 4. Try naver chart data for VKOSPI-like indices
print("\n=== VKOSPI alternatives ===")
# KRX VKOSPI in naver might be 'VKOSPI' or similar code
r = requests.get('https://finance.naver.com/sise/sise_index_day.naver',
    params={'code': 'VKOSPI'}, headers=headers, timeout=10)
text = r.content.decode('euc-kr', errors='replace')
soup = BeautifulSoup(text, 'html.parser')

# Find numbers that could be VKOSPI (10-50 range)
tds = soup.find_all('td')
nums = []
for td in tds:
    t = td.get_text(strip=True).replace(',', '').replace('%', '')
    try:
        val = float(t)
        if 5 < val < 100:
            nums.append(val)
    except:
        pass
print(f'Potential VKOSPI values (5-100): {nums[:10]}')

# 5. Try naver 파생상품 for put/call
print("\n=== Put/Call Ratio Sources ===")
urls_deriv = [
    'https://finance.naver.com/derivative/option.naver',
    'https://finance.naver.com/derivative/optionFutureStatistics.naver',
]
for url in urls_deriv:
    r = requests.get(url, headers=headers, timeout=10)
    print(f'{r.status_code}: {url}')
