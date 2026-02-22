#!/usr/bin/env python3
"""Opus 4 새 시그널 거부 테스트"""
import requests
import json
import time

BASE_URL = "http://localhost:8901"

def test_new_signal():
    print("=== 새 시그널 Opus 4 테스트 ===")
    
    # 시그널 데이터 가져오기
    response = requests.get(f"{BASE_URL}/api/signals")
    signals = response.json()
    
    # 두 번째 시그널 선택 (첫 번째는 이미 테스트했으니)
    test_signal = signals[1] if len(signals) > 1 else signals[0]
    signal_id = test_signal['video_id'] + '_' + test_signal['asset']
    
    print(f"테스트 시그널: {test_signal['asset']} - {test_signal['signal_type']}")
    print(f"내용: {test_signal.get('content', 'N/A')}")
    print(f"Signal ID: {signal_id}")
    
    # 시그널 거부하기
    reject_data = {
        "id": signal_id,
        "status": "rejected", 
        "reason": "시그널 근거가 불분명하고 타임스탬프가 부정확함",
        "time": "2026-02-22 19:40:00"
    }
    
    print(f"\n거부 중...")
    response = requests.post(f"{BASE_URL}/api/review",
                           headers={'Content-Type': 'application/json'}, 
                           data=json.dumps(reject_data))
    
    if response.status_code == 200:
        print("[OK] 시그널 거부 성공")
    else:
        print(f"[FAIL] 거부 실패: {response.status_code}")
        return
    
    # 분석 모니터링
    print(f"\nOpus 4 분석 모니터링...")
    for i in range(24):  # 120초간 모니터링
        response = requests.get(f"{BASE_URL}/api/opus4-analysis")
        analysis_data = response.json()
        
        if signal_id in analysis_data:
            status = analysis_data[signal_id].get('status', 'unknown')
            print(f"[{i*5:2d}s] 상태: {status}")
            
            if status == 'completed':
                print(f"\n[완료] Opus 4 분석 결과:")
                analysis = analysis_data[signal_id]
                
                if 'error' in analysis:
                    print(f"[ERROR] {analysis['error']}")
                else:
                    print(f"- Sonnet 시그널 정확: {analysis.get('sonnet_signal_correct', '?')}")
                    print(f"- 거부 사유 타당: {analysis.get('rejection_valid', '?')}")
                    
                    if 'correct_signal' in analysis and analysis['correct_signal']:
                        correct = analysis['correct_signal']
                        print(f"- 올바른 시그널: {correct.get('signal_type', 'N/A')}")
                        print(f"- 올바른 종목: {correct.get('asset', 'N/A')}")
                        
                    if 'analysis' in analysis:
                        print(f"- 분석 내용: {analysis['analysis'][:200]}...")
                        
                    if 'prompt_improvement' in analysis:
                        print(f"- 프롬프트 개선: {analysis['prompt_improvement'][:200]}...")
                break
                
            elif status == 'analyzing':
                time.sleep(5)
            else:
                print(f"[ERROR] 비정상 상태: {status}")
                break
        else:
            print(f"[{i*5:2d}s] 아직 분석 시작 안됨")
            time.sleep(5)
    else:
        print("[TIMEOUT] 분석 시간 초과")

if __name__ == "__main__":
    test_new_signal()