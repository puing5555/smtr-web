#!/usr/bin/env python3
"""
세상학개론 87개 시그널을 Supabase influencer_signals 테이블에 업로드하는 스크립트
"""
import requests
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

def test_connection():
    """Supabase 연결 테스트"""
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        print(f"연결 테스트: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"연결 실패: {e}")
        return False

def get_speaker_id():
    """세상학개론 채널(이효석)의 speaker_id 확인"""
    try:
        # speakers 테이블에서 이효석 찾기
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/speakers?select=*&name=eq.이효석",
            headers=headers
        )
        
        if response.status_code == 200:
            speakers = response.json()
            if speakers:
                print(f"이효석 speaker 정보: {speakers[0]}")
                return speakers[0]['id']
            else:
                print("이효석 speaker를 찾을 수 없습니다.")
                # 채널명으로도 검색해보기
                response2 = requests.get(
                    f"{SUPABASE_URL}/rest/v1/speakers?select=*&channel_name=ilike.*세상학개론*",
                    headers=headers
                )
                if response2.status_code == 200:
                    speakers2 = response2.json()
                    if speakers2:
                        print(f"세상학개론 채널 speaker 정보: {speakers2[0]}")
                        return speakers2[0]['id']
                
                return None
        else:
            print(f"Speaker 조회 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Speaker 조회 중 오류: {e}")
        return None

def check_videos_exist(video_ids: List[str]) -> Dict[str, str]:
    """YouTube ID로 videos 테이블에서 video_id(UUID) 확인"""
    video_id_mapping = {}
    
    try:
        for youtube_id in video_ids:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/videos?select=id,youtube_id&youtube_id=eq.{youtube_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                videos = response.json()
                if videos:
                    video_id_mapping[youtube_id] = videos[0]['id']
                    print(f"[OK] YouTube ID {youtube_id} -> Video UUID {videos[0]['id']}")
                else:
                    print(f"[MISSING] YouTube ID {youtube_id} 없음")
            else:
                print(f"Video 조회 실패: {response.status_code}")
        
        return video_id_mapping
    except Exception as e:
        print(f"Video 조회 중 오류: {e}")
        return {}

def check_existing_signals(video_ids: List[str]) -> List[tuple]:
    """기존 시그널 중복 체크 (video_id + stock 조합)"""
    existing = []
    
    try:
        # video_ids를 UUID 리스트로 변환
        video_uuid_filter = ",".join([f'"{vid}"' for vid in video_ids if vid])
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=video_id,stock&video_id=in.({video_uuid_filter})",
            headers=headers
        )
        
        if response.status_code == 200:
            signals = response.json()
            existing = [(s['video_id'], s['stock']) for s in signals]
            print(f"기존 시그널 {len(existing)}개 확인됨")
        else:
            print(f"기존 시그널 조회 실패: {response.status_code}")
    
    except Exception as e:
        print(f"기존 시그널 조회 중 오류: {e}")
    
    return existing

def convert_signal_format(signal: str) -> str:
    """시그널을 한글 5단계로 변환"""
    signal_mapping = {
        'STRONG_BUY': '매수',
        'BUY': '긍정', 
        'POSITIVE': '긍정',
        'HOLD': '중립',
        'NEUTRAL': '중립',
        'CONCERN': '경계',
        'SELL': '매도',
        'STRONG_SELL': '매도'
    }
    
    return signal_mapping.get(signal.upper(), '중립')

def main():
    print("=== 세상학개론 시그널 업로드 스크립트 ===\n")
    
    # 1. 연결 테스트
    print("1. Supabase 연결 테스트...")
    if not test_connection():
        print("Supabase 연결 실패!")
        return
    print("[OK] 연결 성공\n")
    
    # 2. Speaker ID 확인
    print("2. 세상학개론 Speaker ID 확인...")
    speaker_id = get_speaker_id()
    if not speaker_id:
        print("Speaker ID를 찾을 수 없습니다!")
        return
    print(f"[OK] Speaker ID: {speaker_id}\n")
    
    # 3. sesang101_supabase_upload.json 파일 찾기
    print("3. 시그널 데이터 파일 확인...")
    try:
        with open('sesang101_supabase_upload.json', 'r', encoding='utf-8') as f:
            signals_data = json.load(f)
        print(f"[OK] 시그널 데이터 {len(signals_data)}개 로드됨")
    except FileNotFoundError:
        print("[ERROR] sesang101_supabase_upload.json 파일을 찾을 수 없습니다.")
        print("현재 디렉토리의 파일들:")
        import os
        for file in os.listdir('.'):
            if 'json' in file:
                print(f"  - {file}")
        return
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return

if __name__ == "__main__":
    main()