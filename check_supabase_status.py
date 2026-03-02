#!/usr/bin/env python3
"""
Supabase influencer_signals 테이블 현황 조회
"""
import requests
import json

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

def check_table_status():
    """influencer_signals 테이블 상태 확인"""
    try:
        # 전체 개수 확인
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=count",
            headers={**headers, "Prefer": "count=exact"}
        )
        
        if response.status_code == 200:
            count = response.headers.get('content-range', '').split('/')[-1]
            print(f"influencer_signals 총 개수: {count}개")
        else:
            print(f"총 개수 조회 실패: {response.status_code}")
        
        # Speaker별 분포 확인
        response2 = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=speaker_id,speakers(name)&limit=1000",
            headers=headers
        )
        
        if response2.status_code == 200:
            signals = response2.json()
            speaker_counts = {}
            for signal in signals:
                speaker_name = signal.get('speakers', {}).get('name', 'Unknown')
                speaker_counts[speaker_name] = speaker_counts.get(speaker_name, 0) + 1
            
            print("\n=== Speaker별 시그널 분포 ===")
            for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{speaker}: {count}개")
        else:
            print(f"Speaker별 분포 조회 실패: {response2.status_code}")
            
    except Exception as e:
        print(f"조회 중 오류: {e}")

def check_signals_data_status():
    """signals_data.json 파일 분석"""
    try:
        with open('signals_data.json', 'r', encoding='utf-8') as f:
            signals_data = json.load(f)
        
        print(f"\n=== signals_data.json 분석 ===")
        print(f"총 시그널 개수: {len(signals_data)}개")
        
        # Speaker별 분포
        speaker_counts = {}
        for signal in signals_data:
            speaker_name = signal.get('speakers', {}).get('name', 'Unknown')
            speaker_counts[speaker_name] = speaker_counts.get(speaker_name, 0) + 1
        
        print("\n=== signals_data.json Speaker별 분포 ===")
        for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{speaker}: {count}개")
            
    except Exception as e:
        print(f"signals_data.json 분석 중 오류: {e}")

if __name__ == "__main__":
    print("=== Supabase 상태 점검 ===\n")
    check_table_status()
    check_signals_data_status()