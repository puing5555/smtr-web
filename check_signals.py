import requests
import json
from collections import Counter

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

# 모든 시그널 타입 조회
api_url = f"{url}/rest/v1/influencer_signals"
params = {
    "select": "signal"
}

print("모든 시그널 타입 확인 중...")
response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:
    signals = response.json()
    signal_types = [s['signal'] for s in signals]
    signal_counts = Counter(signal_types)
    
    print(f"전체 시그널 개수: {len(signals)}")
    print("\n시그널 타입별 개수:")
    for signal_type, count in signal_counts.most_common():
        print(f"  {signal_type}: {count}개")
        
    # 매수 관련 시그널 찾기
    buy_related = ['매수', '강력매수', 'BUY', 'STRONG_BUY', '긍정', '강한긍정']
    found_buy_types = [s for s in signal_counts.keys() if any(keyword in s for keyword in buy_related)]
    
    print(f"\n매수 관련으로 추정되는 시그널 타입: {found_buy_types}")
    
else:
    print(f"에러: {response.status_code} - {response.text}")