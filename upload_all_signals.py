#!/usr/bin/env python3
"""
signals_data.json의 모든 시그널을 Supabase influencer_signals 테이블에 업로드
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

def load_all_signals_data():
    """signals_data.json에서 모든 시그널 로드"""
    try:
        with open('signals_data.json', 'r', encoding='utf-8') as f:
            all_signals = json.load(f)
        
        print(f"signals_data.json에서 {len(all_signals)}개 시그널 로드됨")
        return all_signals
    except Exception as e:
        print(f"시그널 데이터 로드 실패: {e}")
        return []

def check_existing_signals_by_id(signal_ids: List[str]) -> Set[str]:
    """기존 influencer_signals에서 ID 기반 중복 체크"""
    existing_ids = set()
    
    try:
        if not signal_ids:
            return existing_ids
            
        # 배치 단위로 확인 (URL 길이 제한 때문)
        batch_size = 50
        for i in range(0, len(signal_ids), batch_size):
            batch_ids = signal_ids[i:i+batch_size]
            id_filter = ",".join([f'"{sid}"' for sid in batch_ids])
            
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id&id=in.({id_filter})",
                headers=headers
            )
            
            if response.status_code == 200:
                signals = response.json()
                batch_existing = {s['id'] for s in signals}
                existing_ids.update(batch_existing)
                print(f"배치 {i//batch_size + 1}: {len(batch_existing)}개 기존 ID 확인")
            else:
                print(f"기존 시그널 조회 실패: {response.status_code}")
    
    except Exception as e:
        print(f"기존 시그널 조회 중 오류: {e}")
    
    return existing_ids

def convert_to_influencer_signal(signal_data: dict) -> dict:
    """signals_data 형식을 influencer_signals 테이블 형식으로 변환"""
    
    # 기존 ID가 있으면 그대로 사용, 없으면 새로 생성
    signal_id = signal_data.get('id', str(uuid.uuid4()))
    
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

def insert_signals_batch(signals: List[dict]) -> bool:
    """influencer_signals 테이블에 시그널 배치 삽입"""
    if not signals:
        return True
        
    try:
        # 배치 크기 제한 (너무 크면 API 제한에 걸림)
        batch_size = 100
        total_success = 0
        
        for i in range(0, len(signals), batch_size):
            batch = signals[i:i+batch_size]
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/influencer_signals",
                headers=headers,
                json=batch
            )
            
            if response.status_code in [200, 201]:
                total_success += len(batch)
                print(f"배치 {i//batch_size + 1}: {len(batch)}개 업로드 성공")
            else:
                print(f"배치 {i//batch_size + 1} 업로드 실패: {response.status_code}")
                print(f"응답: {response.text[:200]}...")
                return False
        
        print(f"[SUCCESS] 총 {total_success}개 시그널 업로드 완료")
        return True
        
    except Exception as e:
        print(f"시그널 업로드 중 오류: {e}")
        return False

def main():
    print("=== signals_data.json 전체 시그널 Supabase 업로드 ===\n")
    
    # 1. 모든 시그널 데이터 로드
    print("1. 시그널 데이터 로드 중...")
    all_signals = load_all_signals_data()
    if not all_signals:
        print("시그널을 찾을 수 없습니다.")
        return
    
    # 2. 기존 시그널 ID 기반 중복 체크
    print("2. 기존 시그널 중복 체크 중...")
    signal_ids = [s.get('id') for s in all_signals if s.get('id')]
    existing_ids = check_existing_signals_by_id(signal_ids)
    
    # 3. 중복되지 않은 시그널만 필터링
    new_signals = []
    skipped_count = 0
    
    for signal in all_signals:
        signal_id = signal.get('id')
        
        if signal_id in existing_ids:
            speaker_name = signal.get('speakers', {}).get('name', 'Unknown')
            print(f"[SKIP] 중복: {speaker_name} - {signal.get('stock')} ({signal_id[:8]}...)")
            skipped_count += 1
        else:
            converted = convert_to_influencer_signal(signal)
            new_signals.append(converted)
            speaker_name = signal.get('speakers', {}).get('name', 'Unknown')
            print(f"[NEW] {speaker_name} - {signal.get('stock')}: {signal.get('signal')}")
    
    print(f"\n총 {len(all_signals)}개 중 {skipped_count}개 중복 스킵, {len(new_signals)}개 신규 업로드")
    
    # 4. 신규 시그널 업로드
    if new_signals:
        print("3. 신규 시그널 업로드 중...")
        success = insert_signals_batch(new_signals)
        if success:
            print(f"[COMPLETE] {len(new_signals)}개 시그널 업로드 완료!")
            print("\n=== Speaker별 업로드 요약 ===")
            speaker_counts = {}
            for signal in new_signals:
                # signals_data에서 speaker 정보 찾기
                orig_signal = next((s for s in all_signals if s.get('id') == signal['id']), {})
                speaker_name = orig_signal.get('speakers', {}).get('name', 'Unknown')
                speaker_counts[speaker_name] = speaker_counts.get(speaker_name, 0) + 1
            
            for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{speaker}: {count}개")
        else:
            print("[FAILED] 시그널 업로드 실패")
    else:
        print("[INFO] 업로드할 신규 시그널이 없습니다. (모든 시그널이 이미 존재)")

if __name__ == "__main__":
    main()