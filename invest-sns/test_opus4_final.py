#!/usr/bin/env python3
"""Opus 4 최종 테스트"""
import requests
import json
import time

BASE_URL = "http://localhost:8901"

def test_final():
    print("=== Opus 4 최종 테스트 ===")
    
    # 시그널 데이터 가져오기
    response = requests.get(f"{BASE_URL}/api/signals")
    signals = response.json()
    
    # 세 번째 시그널 선택
    test_signal = signals[2] if len(signals) > 2 else signals[0]
    signal_id = test_signal['video_id'] + '_' + test_signal['asset']
    
    print(f"테스트 시그널: {test_signal['asset']} - {test_signal['signal_type']}")
    print(f"내용: {test_signal.get('content', 'N/A')[:100]}...")
    print(f"Signal ID: {signal_id}")
    
    # 거부 처리
    reject_data = {
        "id": signal_id,
        "status": "rejected", 
        "reason": "시그널 근거 부족 및 타임스탬프 오류",
        "time": "2026-02-22 19:50:00"
    }
    
    print(f"\n거부 처리 중...")
    response = requests.post(f"{BASE_URL}/api/review",
                           headers={'Content-Type': 'application/json'}, 
                           data=json.dumps(reject_data))
    
    if response.status_code == 200:
        print("[OK] 거부 성공 - Claude Haiku 분석 시작")
    else:
        print(f"[FAIL] 거부 실패: {response.status_code}")
        return
    
    # 분석 상태 모니터링
    print(f"\n분석 진행 상황...")
    for i in range(30):  # 150초간 모니터링 (Claude 분석은 시간이 걸릴 수 있음)
        response = requests.get(f"{BASE_URL}/api/opus4-analysis")
        analysis_data = response.json()
        
        if signal_id in analysis_data:
            analysis = analysis_data[signal_id]
            status = analysis.get('status', 'unknown')
            
            if status == 'analyzing':
                print(f"[{i*5:2d}s] 분석 중...")
                time.sleep(5)
                continue
                
            elif status == 'completed':
                print(f"\n[완료] Claude Haiku 분석 완료!")
                
                if 'error' in analysis:
                    print(f"[ERROR] {analysis['error'][:200]}...")
                else:
                    print(f"✓ Sonnet 시그널 정확: {analysis.get('sonnet_signal_correct', '?')}")
                    print(f"✓ 거부 사유 타당성: {analysis.get('rejection_valid', '?')}")
                    
                    if 'correct_signal' in analysis and analysis['correct_signal']:
                        correct = analysis['correct_signal']
                        print(f"✓ 올바른 시그널 타입: {correct.get('signal_type', 'N/A')}")
                        print(f"✓ 올바른 종목: {correct.get('asset', 'N/A')}")
                        print(f"✓ 올바른 신뢰도: {correct.get('confidence', 'N/A')}")
                        
                    if 'analysis' in analysis:
                        print(f"\n[상세 분석]\n{analysis['analysis'][:400]}...")
                        
                    if 'prompt_improvement' in analysis:
                        print(f"\n[프롬프트 개선 제안]\n{analysis['prompt_improvement'][:400]}...")
                break
                
            else:
                print(f"[ERROR] 예외 상태: {status}")
                if 'error' in analysis:
                    print(f"오류: {analysis['error']}")
                break
        else:
            print(f"[{i*5:2d}s] 분석 시작 대기 중...")
            time.sleep(5)
    else:
        print("[TIMEOUT] 분석이 150초 내에 완료되지 않음")
    
    # 최종 상태 확인
    print(f"\n=== 최종 결과 확인 ===")
    response = requests.get(f"{BASE_URL}/api/prompt-suggestions")
    suggestions = response.json()
    print(f"프롬프트 제안 누적: {len(suggestions.get('suggestions', []))}개")

if __name__ == "__main__":
    test_final()