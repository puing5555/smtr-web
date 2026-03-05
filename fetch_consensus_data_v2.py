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
    {"name": "삼성전자", "queries": ["삼성전자", "005930"]},
    {"name": "테슬라", "queries": ["테슬라", "TSLA"]},
    {"name": "엔비디아", "queries": ["엔비디아", "NVDA"]}
]

all_data = {}

print("=== 유튜버 컨센서스 데이터 수집 v2 ===")
print(f"기간: {three_months_ago} 이후")
print()

for stock in stocks:
    stock_name = stock["name"]
    queries = stock["queries"]
    
    print(f"{stock_name} 데이터 수집 중...")
    
    stock_signals = []
    
    for query in queries:
        # API 요청 - OR 조건으로 여러 쿼리 실행
        url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
        params = {
            "or": f"(stock.like.*{query}*,ticker.like.*{query}*)",
            "created_at": f"gte.{three_months_ago}",
            "select": "*"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                stock_signals.extend(data)
                print(f"   '{query}' 검색: {len(data)}개")
            else:
                print(f"   '{query}' 검색 오류: {response.status_code}")
                print(f"   오류 메시지: {response.text}")
        
        except Exception as e:
            print(f"   '{query}' 요청 실패: {str(e)}")
    
    # 중복 제거 (id 기준)
    seen_ids = set()
    unique_signals = []
    for signal in stock_signals:
        if signal['id'] not in seen_ids:
            unique_signals.append(signal)
            seen_ids.add(signal['id'])
    
    all_data[stock_name] = unique_signals
    print(f"   총 {len(unique_signals)}개 시그널 (중복 제거 후)")
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
    print(f"\n{stock_name}: {len(data)}개")
    
    if len(data) > 0:
        # 시그널 타입별 개수
        signal_types = {}
        influencers = set()
        
        for signal in data:
            signal_type = signal.get("signal", "UNKNOWN")
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            # speaker_id로 유튜버 식별
            speaker_id = signal.get("speaker_id", "")
            if speaker_id:
                influencers.add(speaker_id)
        
        print(f"   시그널 분포: {dict(signal_types)}")
        print(f"   유튜버 수: {len(influencers)}명")
        
        # 최근 데이터인지 확인
        recent_dates = []
        for signal in data[:5]:  # 최근 5개만
            created_at = signal.get("created_at", "")
            if created_at:
                recent_dates.append(created_at[:10])
        if recent_dates:
            print(f"   최근 날짜들: {', '.join(recent_dates)}")