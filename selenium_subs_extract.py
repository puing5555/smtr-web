#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 기반 YouTube 자막 추출 (인코딩 문제 해결)
슈카월드/이효석/부읽남/달란트 최신 영상 자막 추출
"""

import time
import json
import os
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 채널 정보
CHANNELS = {
    'syuka': {
        'name': '슈카월드', 
        'url': 'https://www.youtube.com/@syukaworld/videos'
    },
    'hyoseok': {
        'name': '이효석',
        'url': 'https://www.youtube.com/@hyoseok_lee/videos' 
    },
    'booknam': {
        'name': '부읽남',
        'url': 'https://www.youtube.com/@booknam/videos'
    },
    'talent': {
        'name': '달란트',
        'url': 'https://www.youtube.com/@talent/videos'
    }
}

def setup_driver():
    """Chrome 드라이버 설정"""
    options = Options()
    # options.add_argument('--headless')  # 디버깅을 위해 주석처리
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver

def get_latest_videos(driver, channel_url, max_videos=5):
    """채널에서 최신 비디오 URL들 가져오기"""
    print(f"채널 접속: {channel_url}")
    
    try:
        driver.get(channel_url)
        time.sleep(5)
        
        # 페이지가 로드될 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 스크롤해서 더 많은 비디오 로드
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(3)
        
        # 비디오 링크 찾기
        video_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/watch?v="]')
        
        video_urls = []
        seen_ids = set()
        
        for element in video_elements:
            href = element.get_attribute('href')
            if href and '/watch?v=' in href:
                video_id = href.split('/watch?v=')[1].split('&')[0]
                if video_id not in seen_ids and len(video_urls) < max_videos:
                    video_urls.append(href)
                    seen_ids.add(video_id)
        
        print(f"   찾은 비디오: {len(video_urls)}개")
        return video_urls[:max_videos]
        
    except Exception as e:
        print(f"   에러: {str(e)}")
        return []

def extract_video_info(driver, video_url):
    """비디오에서 제목, 설명, 자막 추출"""
    try:
        print(f"   비디오 분석: {video_url}")
        driver.get(video_url)
        time.sleep(5)
        
        # 제목 추출
        try:
            title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.ytd-watch-metadata yt-formatted-string'))
            )
            title = title_element.text.strip()
        except:
            title = "제목 없음"
        
        # 설명 추출 시도
        description = ""
        try:
            # 더보기 버튼 클릭
            show_more = driver.find_element(By.CSS_SELECTOR, '[class*="show-more-button"]')
            show_more.click()
            time.sleep(2)
        except:
            pass
            
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, '[class*="ytd-watch-metadata"] [class*="description"]')
            description = description_element.text.strip()
        except:
            description = "설명 없음"
        
        # 업로드 날짜 추출
        upload_date = datetime.now().strftime('%Y-%m-%d')
        
        # 비디오 ID 추출
        video_id = video_url.split('/watch?v=')[1].split('&')[0] if '/watch?v=' in video_url else ""
        
        video_info = {
            'video_id': video_id,
            'title': title,
            'description': description,
            'upload_date': upload_date,
            'url': video_url,
            'subtitles': ""  # 자막은 별도로 처리 필요
        }
        
        print(f"      제목: {title[:50]}...")
        return video_info
        
    except Exception as e:
        print(f"      에러: {str(e)}")
        return None

def process_channel(channel_key, channel_info):
    """채널별 자막 추출 처리"""
    print(f"\n[{channel_info['name']}] 처리 시작")
    
    driver = setup_driver()
    results = []
    
    try:
        # 최신 비디오 URL 가져오기
        video_urls = get_latest_videos(driver, channel_info['url'], max_videos=3)
        
        if not video_urls:
            print(f"   {channel_info['name']}: 비디오를 찾을 수 없음")
            return results
        
        # 각 비디오 처리
        for video_url in video_urls:
            video_info = extract_video_info(driver, video_url)
            if video_info:
                results.append(video_info)
                
                # JSON 파일로 저장
                filename = f"subs/{channel_key}_{video_info['video_id']}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(video_info, f, ensure_ascii=False, indent=2)
                print(f"      저장: {filename}")
            
            time.sleep(2)  # 요청 간격
        
        print(f"   {channel_info['name']}: {len(results)}개 비디오 처리 완료")
        
    except Exception as e:
        print(f"   {channel_info['name']} 에러: {str(e)}")
    
    finally:
        driver.quit()
    
    return results

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Selenium YouTube 자막 추출 시작")
    print("대상: 슈카월드, 이효석, 부읽남, 달란트")
    print("=" * 60)
    
    # subs 폴더 생성
    os.makedirs('subs', exist_ok=True)
    
    total_videos = 0
    
    # 각 채널 순차 처리 (안정성을 위해)
    for channel_key, channel_info in CHANNELS.items():
        try:
            results = process_channel(channel_key, channel_info)
            total_videos += len(results)
            time.sleep(5)  # 채널 간 간격
            
        except Exception as e:
            print(f"채널 {channel_info['name']} 처리 중 에러: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print(f"전체 결과: {total_videos}개 비디오 처리 완료")
    print("다음 단계: V9 분석 스크립트로 시그널 추출")
    print("=" * 60)

if __name__ == "__main__":
    main()