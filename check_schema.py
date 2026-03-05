import requests
import json

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

# influencer_signals 테이블의 첫 번째 레코드 조회 (모든 컬럼 포함)
api_url = f"{url}/rest/v1/influencer_signals"
params = {
    "limit": "1"
}

print("influencer_signals 테이블 스키마 확인 중...")
response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:
    signals = response.json()
    if signals:
        print("사용 가능한 컬럼들:")
        for column in signals[0].keys():
            print(f"  - {column}")
        
        print("\n첫 번째 레코드 예시:")
        print(json.dumps(signals[0], ensure_ascii=False, indent=2))
    else:
        print("테이블에 데이터가 없습니다.")
else:
    print(f"에러: {response.status_code} - {response.text}")