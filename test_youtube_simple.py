#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube API 429 에러 상태 테스트 (이모지 없음)
"""

import requests
import time
from datetime import datetime

def test_youtube_access():
    """YouTube 접근 테스트"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] YouTube 429 상태 테스트 시작...")
    
    # 슈카월드 채널 비디오 목록 접근 테스트
    test_urls = [
        "https://www.youtube.com/feed/subscriptions",
        "https://www.youtube.com/@syukaworld/videos",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        try:
            print(f"\n[{i}] 테스트 URL: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            status = response.status_code
            print(f"    상태코드: {status}")
            
            if status == 429:
                print("    결과: 여전히 429 Too Many Requests 에러!")
                results.append(False)
            elif status == 200:
                print("    결과: 정상 응답")
                results.append(True)
            else:
                print(f"    결과: 기타 응답 ({status})")
                results.append(False)
                
        except Exception as e:
            print(f"    에러: {str(e)}")
            results.append(False)
            
        time.sleep(3)  # 간격
    
    success_count = sum(results)
    print(f"\n[결과] {len(results)}개 중 {success_count}개 성공")
    
    if success_count > 0:
        print(">> YouTube 접근 가능! 자막 추출 재개 추천")
        return True
    else:
        print(">> YouTube 아직 차단됨, 대기 필요")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("YouTube 자막 추출 시스템 상태 점검")
    print("=" * 60)
    
    # 접근 테스트
    access_ok = test_youtube_access()
    
    print("\n" + "=" * 60)
    print("최종 결과:")
    if access_ok:
        print(">> 자막 추출 재개 가능!")
        print(">> extract_subs_v9.py 실행 권장")
    else:
        print(">> 조금 더 대기 후 재시도 권장")
        
    print("=" * 60)