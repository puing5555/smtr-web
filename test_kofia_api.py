"""
KOFIA API 직접 테스트
URL: https://freesis.kofia.or.kr/meta/getMetaDataList.do
"""
import requests
import json
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Referer': 'https://freesis.kofia.or.kr/stat/FreeSIS.do?parentDivId=MSIS10000000000000&serviceId=STATSCU0100000060',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Origin': 'https://freesis.kofia.or.kr',
})

API_URL = 'https://freesis.kofia.or.kr/meta/getMetaDataList.do'

def fetch_kofia(obj_nm, start_date, end_date, period='D', max_rows='9999'):
    """
    KOFIA API 데이터 조회
    obj_nm: 서비스 ID + 'BO' (예: STATSCU0100000060BO)
    start_date: YYYYMMDD
    end_date: YYYYMMDD
    period: D=일, M=월, Y=년
    """
    payload = {
        "dmSearch": {
            "tmpV40": max_rows,
            "tmpV41": "1",
            "tmpV1": period,
            "tmpV45": start_date,
            "tmpV46": end_date,
            "OBJ_NM": obj_nm
        }
    }
    r = session.post(API_URL, json=payload, timeout=30)
    print(f"Status: {r.status_code}, Size: {len(r.content)}")
    try:
        data = r.json()
        return data
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {r.text[:500]}")
        return None

# 1. 증시자금추이 (투자자예탁금) - 10년 데이터
print("=== 1. 투자자예탁금 (증시자금추이) ===")
data = fetch_kofia("STATSCU0100000060BO", "20150101", "20260307")

if data:
    print(f"Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
    if isinstance(data, dict):
        for key in data.keys():
            val = data[key]
            if isinstance(val, list):
                print(f"  {key}: {len(val)} items")
                if val:
                    print(f"  First item: {val[0]}")
                    print(f"  Last item: {val[-1]}")
            elif isinstance(val, dict):
                print(f"  {key}: {val}")
            else:
                print(f"  {key}: {val}")

# 2. Try 신용공여현황 (신용잔고)
print("\n=== 2. 신용공여현황 ===")
# Need to find the correct obj_nm
# From the menu: STATSCU0100000060 is 증시자금추이
# 신용공여현황 might be another code
# Let's try to find it by navigating
data2 = fetch_kofia("STATSCU0200000010BO", "20150101", "20260307")
if data2:
    print(f"Keys: {list(data2.keys()) if isinstance(data2, dict) else type(data2)}")

# 3. Try to get the menu data to find 신용공여현황 code
print("\n=== 3. Menu data for correct codes ===")
r_menu = session.get('https://freesis.kofia.or.kr/meta/getMenuData.do', timeout=15)
print(f"Menu status: {r_menu.status_code}")
if r_menu.status_code == 200:
    try:
        menu = r_menu.json()
        menu_str = json.dumps(menu, ensure_ascii=False)
        # Search for 신용 related codes
        import re
        codes = re.findall(r'"serviceId"\s*:\s*"([^"]+)"[^}]*"menuNm"\s*:\s*"([^"]+)"', menu_str)
        print(f"Found {len(codes)} service IDs")
        for code, name in codes[:20]:
            print(f"  {code}: {name}")
    except Exception as e:
        print(f"Menu parse error: {e}")
        print(f"Menu raw: {r_menu.text[:1000]}")
