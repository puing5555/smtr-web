import requests
import json
import random

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

# 매수 시그널 조회
api_url = f"{url}/rest/v1/influencer_signals"
params = {
    "signal_type": "eq.매수",
    "select": "id,speaker_id,stock,signal_type,key_quote,video_title,published_at",
    "order": "published_at.desc"
}

print("매수 시그널 데이터 조회 중...")
response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:
    buy_signals = response.json()
    print(f"총 매수 시그널 개수: {len(buy_signals)}")
    
    # 첫 5개 예시 출력
    print("\n첫 5개 예시:")
    for i, signal in enumerate(buy_signals[:5]):
        print(f"{i+1}. [speaker_id: {signal['speaker_id']}] {signal['stock']} - {signal['key_quote'][:50]}...")
    
    # JSON 파일로 저장
    with open('buy_signals.json', 'w', encoding='utf-8') as f:
        json.dump(buy_signals, f, ensure_ascii=False, indent=2)
    
    print(f"\n데이터를 buy_signals.json에 저장했습니다.")
else:
    print(f"에러: {response.status_code} - {response.text}")