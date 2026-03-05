import requests
import json
import random
from collections import Counter, defaultdict

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

# 스피커 정보 조회
print("스피커 정보 조회 중...")
speaker_url = f"{url}/rest/v1/speakers"
speaker_response = requests.get(speaker_url, headers=headers, params={"select": "id,name"})
speaker_map = {}
if speaker_response.status_code == 200:
    speakers = speaker_response.json()
    speaker_map = {s['id']: s['name'] for s in speakers}

# 매수 시그널 10개만 먼저 조회해서 분석
api_url = f"{url}/rest/v1/influencer_signals"
params = {
    "signal": "eq.매수",
    "select": "id,speaker_id,video_id,stock,signal,key_quote,timestamp,confidence,created_at",
    "order": "created_at.desc",
    "limit": "20"
}

print("매수 시그널 20개 샘플 조회 중...")
response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:
    buy_signals = response.json()
    
    print(f"\n=== 실제 매수 시그널 사례 분석 ===")
    
    for i, signal in enumerate(buy_signals):
        speaker_name = speaker_map.get(signal['speaker_id'], 'Unknown')
        print(f"\n{i+1}. [{speaker_name}] {signal['stock']}")
        print(f"    발언: {signal['key_quote']}")
        print(f"    신뢰도: {signal['confidence']}")
        print(f"    타임스탬프: {signal['timestamp']}")
        
        # 키워드 분석
        quote = signal['key_quote'].lower()
        
        # 더 포괄적인 매수 키워드들
        strong_buy_patterns = [
            '사야', '매수', '담아', '사들여', '비중', '추천', 
            '올려', '늘려', '증가', '확대', '가져가', '잡아',
            '기회', '타이밍', '진입', '포지션', '살 만', '살만',
            '저가', '바닥', '싸게', '할인', '좋은 가격'
        ]
        
        negative_patterns = [
            '안 사', '사지 마', '피해', '위험', '주의', '경계',
            '매도', '팔아', '줄여', '감소', '축소', '빼라'
        ]
        
        found_buy_patterns = [p for p in strong_buy_patterns if p in quote]
        found_negative_patterns = [p for p in negative_patterns if p in quote]
        
        print(f"    매수 패턴: {found_buy_patterns}")
        print(f"    부정 패턴: {found_negative_patterns}")
        
        # 분류
        if found_buy_patterns and not found_negative_patterns:
            classification = "진짜 매수 가능성 높음"
        elif found_negative_patterns:
            classification = "부정적/매도 성향"
        else:
            classification = "애매/단순긍정"
            
        print(f"    분류: {classification}")

else:
    print(f"에러: {response.status_code} - {response.text}")