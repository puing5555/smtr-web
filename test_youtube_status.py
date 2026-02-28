#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube API 429 에러 상태 테스트
"""

import requests
import time
from datetime import datetime

def test_youtube_api():
    """YouTube API 상태 테스트"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] YouTube API 429 상태 테스트 시작...")
    
    # 슈카월드 채널 비디오 목록 API 호출 테스트
    test_urls = [
        "https://www.youtube.com/feed/subscriptions",  # 일반 페이지
        "https://www.youtube.com/channel/UCYDkJM6zQ-r5HBuTgvKtSjA/videos",  # 슈카월드 비디오 목록
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in test_urls:
        try:
            print(f"\n테스트 URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"상태코드: {response.status_code}")
            
            if response.status_code == 429:
                print("❌ 여전히 429 Too Many Requests 에러!")
                return False
            elif response.status_code == 200:
                print("✅ 정상 응답")
            else:
                print(f"⚠️  다른 응답: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 에러: {e}")
            
        time.sleep(2)  # 간격 두기
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] API 테스트 완료")
    return True

def test_selenium_access():
    """Selenium 웹드라이버로 YouTube 접근 테스트"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Selenium 드라이버 테스트...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        # 슈카월드 채널 접근
        test_url = "https://www.youtube.com/@syukaworld/videos"
        driver.get(test_url)
        
        time.sleep(5)  # 페이지 로드 대기
        
        page_title = driver.title
        print(f"페이지 제목: {page_title}")
        
        if "슈카" in page_title or "syuka" in page_title.lower():
            print("✅ Selenium으로 YouTube 접근 성공!")
            success = True
        else:
            print("⚠️  페이지 로드됐지만 예상과 다름")
            success = False
            
        driver.quit()
        return success
        
    except Exception as e:
        print(f"❌ Selenium 에러: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("YouTube 자막 추출 시스템 상태 점검")
    print("=" * 50)
    
    # API 상태 테스트
    api_ok = test_youtube_api()
    
    # Selenium 상태 테스트
    selenium_ok = test_selenium_access()
    
    print("\n" + "=" * 50)
    print("📊 최종 결과:")
    print(f"API 접근: {'✅ OK' if api_ok else '❌ 차단됨'}")
    print(f"Selenium 접근: {'✅ OK' if selenium_ok else '❌ 실패'}")
    
    if api_ok or selenium_ok:
        print("\n🎯 권장 사항: 자막 추출 재개 가능!")
        if selenium_ok:
            print("   → Selenium 방식 사용 권장")
    else:
        print("\n⏰ 권장 사항: 조금 더 대기 후 재시도")
        
    print("=" * 50)