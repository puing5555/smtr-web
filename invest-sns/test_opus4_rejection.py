#!/usr/bin/env python3
"""Opus 4 거부 테스트 스크립트"""
import requests
import json
import time

BASE_URL = "http://localhost:8901"

def test_rejection_and_opus4():
    print("=== Opus 4 거부 & 재분석 테스트 ===")
    
    # 1. 시그널 데이터 가져오기
    print("\n1. 시그널 데이터 가져오기")
    response = requests.get(f"{BASE_URL}/api/signals")
    signals = response.json()
    
    if not signals:
        print("[ERROR] 시그널 데이터가 없습니다.")
        return
    
    # 첫 번째 시그널 선택
    test_signal = signals[0]
    signal_id = test_signal['video_id'] + '_' + test_signal['asset']
    print(f"테스트 시그널: {test_signal['asset']} - {test_signal['signal_type']}")
    print(f"Signal ID: {signal_id}")
    
    # 2. 시그널 거부하기
    print("\n2. 시그널 거부하기 (Opus 4 재검증 트리거)")
    reject_data = {
        "id": signal_id,
        "status": "rejected",
        "reason": "테스트 거부 - 시그널 내용이 모호함",
        "time": "2026-02-22 19:30:00"
    }
    
    response = requests.post(f"{BASE_URL}/api/review", 
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(reject_data))
    
    if response.status_code == 200:
        print("[OK] 시그널 거부 성공 - Opus 4 분석 트리거됨")
    else:
        print(f"[FAIL] 시그널 거부 실패: {response.status_code}")
        return
    
    # 3. Opus 4 분석 상태 모니터링
    print("\n3. Opus 4 분석 상태 모니터링")
    for i in range(12):  # 60초간 모니터링 (5초 간격)
        response = requests.get(f"{BASE_URL}/api/opus4-analysis")
        analysis_data = response.json()
        
        if signal_id in analysis_data:
            status = analysis_data[signal_id].get('status', 'unknown')
            print(f"[{i*5:2d}s] 분석 상태: {status}")
            
            if status == 'completed':
                print("\n[OK] Opus 4 분석 완료!")
                analysis = analysis_data[signal_id]
                print(f"- Sonnet 시그널 정확도: {analysis.get('sonnet_signal_correct', 'N/A')}")
                print(f"- 거부 사유 타당성: {analysis.get('rejection_valid', 'N/A')}")
                if 'analysis' in analysis:
                    print(f"- 상세 분석: {analysis['analysis'][:100]}...")
                if 'prompt_improvement' in analysis:
                    print(f"- 프롬프트 개선 제안: {analysis['prompt_improvement'][:100]}...")
                break
            elif status == 'analyzing':
                time.sleep(5)
                continue
            else:
                print(f"[ERROR] 예상치 못한 상태: {status}")
                break
        else:
            print(f"[{i*5:2d}s] 분석 데이터 없음")
            time.sleep(5)
    else:
        print("[TIMEOUT] 분석이 60초 내에 완료되지 않음")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_rejection_and_opus4()