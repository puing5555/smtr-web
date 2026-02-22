#!/usr/bin/env python3
"""Opus 4 API 테스트 스크립트"""
import requests
import json
import time

BASE_URL = "http://localhost:8901"

def test_apis():
    print("=== Opus 4 API 테스트 ===")
    
    # 1. 시그널 데이터 확인
    print("\n1. 시그널 데이터 로드 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/signals")
        if response.status_code == 200:
            signals = response.json()
            print(f"[OK] 시그널 데이터 로드 성공: {len(signals)}개")
            if signals:
                print(f"   첫 번째 시그널: {signals[0].get('asset', 'N/A')} - {signals[0].get('signal_type', 'N/A')}")
        else:
            print(f"[FAIL] 시그널 데이터 로드 실패: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 시그널 데이터 로드 오류: {e}")
    
    # 2. 리뷰 데이터 확인
    print("\n2. 리뷰 데이터 로드 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/reviews")
        if response.status_code == 200:
            reviews = response.json()
            print(f"[OK] 리뷰 데이터 로드 성공: {len(reviews)}개")
        else:
            print(f"[FAIL] 리뷰 데이터 로드 실패: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 리뷰 데이터 로드 오류: {e}")
    
    # 3. Opus 4 분석 데이터 확인
    print("\n3. Opus 4 분석 데이터 로드 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/opus4-analysis")
        if response.status_code == 200:
            analysis = response.json()
            print(f"[OK] Opus 4 분석 데이터 로드 성공: {len(analysis)}개")
        else:
            print(f"[FAIL] Opus 4 분석 데이터 로드 실패: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Opus 4 분석 데이터 로드 오류: {e}")
    
    # 4. 프롬프트 제안 데이터 확인
    print("\n4. 프롬프트 제안 데이터 로드 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/prompt-suggestions")
        if response.status_code == 200:
            suggestions = response.json()
            print(f"[OK] 프롬프트 제안 데이터 로드 성공: {len(suggestions.get('suggestions', []))}개")
        else:
            print(f"[FAIL] 프롬프트 제안 데이터 로드 실패: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 프롬프트 제안 데이터 로드 오류: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_apis()