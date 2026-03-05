import requests
import json
from datetime import datetime, timedelta

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 최근 3개월 날짜 계산 (2025-12-05)
three_months_ago = "2025-12-05"

stocks = [
    {"name": "삼성전자", "query": "삼성전자"},
    {"name": "테슬라", "query": "테슬라"},
    {"name": "엔비디아", "query": "엔비디아"}
]

all_data = {}

print("=== 유튜버 컨센서스 데이터 수집 ===")
print(f"기간: {three_months_ago} 이후")
print()

for stock in stocks:
    stock_name = stock["name"]
    query = stock["query"]
    
    print(f"{stock_name} 데이터 수집 중...")
    
    # API 요청
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {
        "stock": f"like.*{query}*",
        "published_at": f"gte.{three_months_ago}",
        "select": "*"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_data[stock_name] = data
            print(f"   OK - {len(data)}개 시그널 수집 완료")
        else:
            print(f"   ERROR - API 오류: {response.status_code}")
            print(f"   오류 메시지: {response.text}")
            all_data[stock_name] = []
    
    except Exception as e:
        print(f"   ERROR - 요청 실패: {str(e)}")
        all_data[stock_name] = []

print()
print("=== 데이터 수집 완료 ===")

# 데이터 저장
with open("C:\\Users\\Mario\\work\\consensus_raw_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("파일 저장 완료: consensus_raw_data.json")

# 데이터 요약
print()
print("=== 수집된 데이터 요약 ===")
for stock_name, data in all_data.items():
    print(f"{stock_name}: {len(data)}개")
    
    if len(data) > 0:
        # 시그널 타입별 개수
        signal_types = {}
        influencers = set()
        
        for signal in data:
            signal_type = signal.get("signal_type", "UNKNOWN")
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            influencer_name = signal.get("influencer_name", "")
            if influencer_name:
                influencers.add(influencer_name)
        
        print(f"   시그널 타입: {dict(signal_types)}")
        print(f"   유튜버 수: {len(influencers)}명")
        print()