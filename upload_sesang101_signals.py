#!/usr/bin/env python3
"""
세상학개론 시그널을 Supabase influencer_signals 테이블에 업로드
"""
import requests
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

SESANG_SPEAKER_ID = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c'

def load_signals_data():
    """signals_data.json에서 세상학개론 시그널만 로드"""
    try:
        with open('signals_data.json', 'r', encoding='utf-8') as f:
            all_signals = json.load(f)
        
        # 세상학개론 시그널만 필터링
        sesang_signals = [s for s in all_signals if s.get('speaker_id') == SESANG_SPEAKER_ID]
        print(f"전체 {len(all_signals)}개 중 세상학개론 시그널 {len(sesang_signals)}개 발견")
        return sesang_signals
    except Exception as e:
        print(f"시그널 데이터 로드 실패: {e}")
        return []

def check_existing_signals(video_ids: List[str]) -> Set[tuple]:
    """기존 influencer_signals에서 중복 체크 (video_id + stock 조합)"""
    existing = set()
    
    try:
        if not video_ids:
            return existing
            
        # video_ids를 UUID 리스트로 변환
        video_uuid_filter = ",".join([f'"{vid}"' for vid in video_ids if vid])
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=video_id,stock&video_id=in.({video_uuid_filter})",
            headers=headers
        )
        
        if response.status_code == 200:
            signals = response.json()
            existing = {(s['video_id'], s['stock']) for s in signals}
            print(f"기존 시그널 중복 체크: {len(existing)}개 조합 확인됨")
        else:
            print(f"기존 시그널 조회 실패: {response.status_code}")
    
    except Exception as e:
        print(f"기존 시그널 조회 중 오류: {e}")
    
    return existing

def convert_to_influencer_signal(signal_data: dict) -> dict:
    """signals_data 형식을 influencer_signals 테이블 형식으로 변환"""
    # UUID 생성
    signal_id = str(uuid.uuid4())
    
    # 필수 필드 매핑
    converted = {
        "id": signal_id,
        "video_id": signal_data.get('video_id'),
        "speaker_id": signal_data.get('speaker_id'),
        "stock": signal_data.get('stock'),
        "ticker": signal_data.get('ticker'),
        "market": signal_data.get('market', 'KR'),
        "mention_type": signal_data.get('mention_type', '언급'),
        "signal": signal_data.get('signal', '중립'),  # 이미 한글 형식
        "confidence": signal_data.get('confidence', 'medium'),
        "timestamp": None,  # TODO: 영상에서 타임스탬프 추출 필요
        "key_quote": signal_data.get('key_quote'),
        "reasoning": signal_data.get('reasoning'),
        "review_status": 'pending',  # 모든 시그널은 검토 대기
        "pipeline_version": 'V9.1',
        "created_at": datetime.utcnow().isoformat() + 'Z'
    }
    
    return converted

def insert_signals(signals: List[dict]) -> bool:
    """influencer_signals 테이블에 시그널 일괄 삽입"""
    if not signals:
        return True
        
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/influencer_signals",
            headers=headers,
            json=signals
        )
        
        if response.status_code in [200, 201]:
            print(f"[SUCCESS] {len(signals)}개 시그널 업로드 완료")
            return True
        else:
            print(f"[ERROR] 시그널 업로드 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"시그널 업로드 중 오류: {e}")
        return False

def main():
    print("=== 세상학개론 시그널 Supabase 업로드 ===\n")
    
    # 1. 시그널 데이터 로드
    print("1. 시그널 데이터 로드 중...")
    sesang_signals = load_signals_data()
    if not sesang_signals:
        print("세상학개론 시그널을 찾을 수 없습니다.")
        return
    
    # 2. 기존 시그널 중복 체크
    print("2. 기존 시그널 중복 체크 중...")
    video_ids = [s.get('video_id') for s in sesang_signals if s.get('video_id')]
    existing_combinations = check_existing_signals(video_ids)
    
    # 3. 중복되지 않은 시그널만 필터링
    new_signals = []
    skipped_count = 0
    
    for signal in sesang_signals:
        video_id = signal.get('video_id')
        stock = signal.get('stock')
        
        if (video_id, stock) in existing_combinations:
            print(f"[SKIP] 중복: {stock} (video: {video_id[:8]}...)")
            skipped_count += 1
        else:
            converted = convert_to_influencer_signal(signal)
            new_signals.append(converted)
            print(f"[NEW] {stock}: {signal.get('signal')} - {signal.get('key_quote')[:50]}...")
    
    print(f"\n총 {len(sesang_signals)}개 중 {skipped_count}개 중복 스킵, {len(new_signals)}개 신규 업로드")
    
    # 4. 신규 시그널 업로드
    if new_signals:
        print("3. 신규 시그널 업로드 중...")
        success = insert_signals(new_signals)
        if success:
            print(f"[COMPLETE] {len(new_signals)}개 세상학개론 시그널 업로드 완료!")
        else:
            print("[FAILED] 시그널 업로드 실패")
    else:
        print("[INFO] 업로드할 신규 시그널이 없습니다.")

if __name__ == "__main__":
    main()