"""
ECOS API 체계적 탐색 - 신용잔고, 예탁금 관련 stat codes
"""
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

api_key = "sample"

def ecos_table_list(keyword):
    """ECOS 통계표 목록 검색"""
    url = f"https://ecos.bok.or.kr/api/StatisticTableList/{api_key}/json/kr/1/100/{keyword}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'StatisticTableList' in data:
            return data['StatisticTableList'].get('row', [])
    except Exception as e:
        pass
    return []

def ecos_fetch(stat_code, period_type, start, end, item_code, max_count=100):
    """ECOS 통계 데이터 조회"""
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/{max_count}/{stat_code}/{period_type}/{start}/{end}/{item_code}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'StatisticSearch' in data:
            return data['StatisticSearch'].get('row', [])
    except:
        pass
    return []

def ecos_item_list(stat_code):
    """ECOS 통계 항목 목록"""
    url = f"https://ecos.bok.or.kr/api/StatisticItemList/{api_key}/json/kr/1/200/{stat_code}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'StatisticItemList' in data:
            return data['StatisticItemList'].get('row', [])
    except:
        pass
    return []

# 1. 주식 관련 자금
print("=== ECOS 자금순환 (902Y001) ===")
items = ecos_item_list("902Y001")
for item in items[:10]:
    print(f"  {item}")

# 2. 증시 관련
print("\n=== ECOS 증시 (검색) ===")
keywords = ["증시", "증권", "주식시장", "융자잔", "예탁금", "신용공여", "거래소"]
for kw in keywords:
    results = ecos_table_list(kw)
    if results:
        print(f"\n'{kw}':")
        for r in results[:5]:
            print(f"  {r.get('STAT_CODE','?')} | {r.get('STAT_NAME','?')} | {r.get('CYCLE','?')}")

# 3. Try the 주식시장 related tables directly
print("\n=== 직접 탐색 ===")
# Try stat codes that might contain stock market data
test_codes = [
    "040Y002",  # 증권시장 관련 통계
    "040Y005",
    "040Y010", 
    "200Y002",  # 주식시장 관련
    "S63Y002",
    "063Y001",  # 증권 통계
    "063Y002",
    "063Y010",
    "904Y001",  # 주식
    "701Y056",
]

for code in test_codes:
    items = ecos_item_list(code)
    if items:
        print(f"\n{code}: {len(items)} items")
        for item in items[:3]:
            print(f"  {item}")
        # Try to fetch some data
        if items:
            item_code = items[0].get('ITEM_CODE', '')
            rows = ecos_fetch(code, 'M', '202401', '202601', item_code, 5)
            if rows:
                print(f"  Sample data: {rows[:2]}")

# 4. Try the Securities Finance data
print("\n=== Securities finance codes ===")
more_codes = [
    "402Y037",  # 금리 관련
    "817Y002",  # 채권 관련
    "040Y007",
    "040Y008",  
]
for code in more_codes:
    items = ecos_item_list(code)
    if items:
        print(f"{code}: {[i.get('ITEM_NAME','?') for i in items[:5]]}")
