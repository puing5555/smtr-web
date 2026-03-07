"""
KOFIA 신용잔고 + 고객예탁금 API 테스트
패턴: https://freesis.kofia.or.kr/meta/getMetaDataList.do
서비스 ID: STATSCU0100000070 (신용공여 잔고 추이)
        STATSCU0100000060 (증시자금추이 - 투자자예탁금)
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
    'Referer': 'https://freesis.kofia.or.kr/stat/FreeSIS.do?parentDivId=MSIS10000000000000&serviceId=STATSCU0100000070',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Origin': 'https://freesis.kofia.or.kr',
})

API_URL = 'https://freesis.kofia.or.kr/meta/getMetaDataList.do'

def fetch_kofia(obj_nm, start_date='20150101', end_date='20260307', period='D'):
    payload = {
        "dmSearch": {
            "tmpV40": "9999",
            "tmpV41": "1",
            "tmpV1": period,
            "tmpV45": start_date,
            "tmpV46": end_date,
            "OBJ_NM": obj_nm
        }
    }
    r = session.post(API_URL, json=payload, timeout=30)
    print(f"  Status: {r.status_code}, Size: {len(r.content)}")
    try:
        return r.json()
    except:
        print(f"  Error parsing JSON: {r.text[:200]}")
        return None

# Test different serviceId + BO patterns
service_ids = [
    "STATSCU0100000070BO",  # 신용공여 잔고 추이
    "STATSCU0100000020BO",  # Another stock service
    "STATSCU0100000030BO",  # Another stock service
    "STATSCU0100000060BO",  # 증시자금추이 (confirmed working)
]

for sid in service_ids:
    print(f"\n=== Testing {sid} ===")
    data = fetch_kofia(sid)
    if data and isinstance(data, dict):
        print(f"  Keys: {list(data.keys())}")
        if 'ds1' in data:
            items = data['ds1']
            print(f"  Records: {len(items)}")
            if items:
                print(f"  First: {items[0]}")
                print(f"  Last: {items[-1]}")
        elif 'errorMsg' in data or 'error' in data:
            print(f"  Error: {data.get('errorMsg', data.get('error', ''))}")
    else:
        print(f"  No valid data")

# Now process the confirmed data sources
print("\n\n=== Processing 투자자예탁금 (10 years) ===")
data_deposit = fetch_kofia("STATSCU0100000060BO")
if data_deposit and 'ds1' in data_deposit:
    items = data_deposit['ds1']
    print(f"Records: {len(items)}")
    # TMPV2 = 투자자예탁금 (in 만원, divide by 100 for 백만원)
    df_deposit = pd.DataFrame(items)
    df_deposit['date'] = pd.to_datetime(df_deposit['TMPV1'], format='%Y%m%d')
    df_deposit['deposit_bil'] = df_deposit['TMPV2'] / 100000  # convert to 억원
    df_deposit = df_deposit.sort_values('date')
    print(df_deposit[['date', 'deposit_bil']].tail(5).to_string())
    print(f"\nMin: {df_deposit['deposit_bil'].min():.0f}억, Max: {df_deposit['deposit_bil'].max():.0f}억")
    
    # Save to CSV
    df_deposit[['date', 'deposit_bil']].to_csv('C:/Users/Mario/work/kofia_deposit.csv', index=False)
    print("Saved to kofia_deposit.csv")

print("\n=== Processing 신용공여잔고 ===")
data_credit = fetch_kofia("STATSCU0100000070BO")
if data_credit and isinstance(data_credit, dict) and 'ds1' in data_credit:
    items = data_credit['ds1']
    print(f"Records: {len(items)}")
    if items:
        print(f"Columns: {list(items[0].keys())}")
        df_credit = pd.DataFrame(items)
        df_credit['date'] = pd.to_datetime(df_credit['TMPV1'], format='%Y%m%d')
        df_credit = df_credit.sort_values('date')
        print(df_credit.tail(5).to_string())
        df_credit.to_csv('C:/Users/Mario/work/kofia_credit.csv', index=False)
        print("Saved to kofia_credit.csv")
