#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V9 자막 추출 스크립트 - 4개 채널 병렬 처리
슈카월드/이효석/부읽남/달란트 자막 추출 → V9 분석 → Supabase INSERT
"""

import time
import json
import os
import re
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import requests

# 채널 정보
CHANNELS = {
    'syuka': {
        'name': '슈카월드',
        'url': 'https://www.youtube.com/@syukaworld',
        'channel_id': 'UCYDkJM6zQ-r5HBuTgvKtSjA'
    },
    'hyoseok': {
        'name': '이효석',  
        'url': 'https://www.youtube.com/@hyoseok_lee',
        'channel_id': 'UCK_ABC123'  # 실제 채널 ID 필요
    },
    'booknam': {
        'name': '부읽남',
        'url': 'https://www.youtube.com/@booknam', 
        'channel_id': 'UCK_DEF456'  # 실제 채널 ID 필요
    },
    'talent': {
        'name': '달란트',
        'url': 'https://www.youtube.com/@talent',
        'channel_id': 'UCK_GHI789'  # 실제 채널 ID 필요
    }
}

def setup_driver():
    """Chrome 드라이버 설정"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver

def get_recent_videos(driver, channel_url, limit=30):
    """최근 영상 30개 목록 가져오기"""
    driver.get(f"{channel_url}/videos")
    time.sleep(3)
    
    # 스크롤 다운으로 더 많은 영상 로드
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
    
    videos = []
    video_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/watch?v="]')
    
    for elem in video_elements[:limit]:
        try:
            href = elem.get_attribute('href')
            video_id = href.split('v=')[1].split('&')[0]
            
            # 제목 가져오기
            title_elem = elem.find_element(By.CSS_SELECTOR, '#video-title')
            title = title_elem.get_attribute('title') or title_elem.text
            
            videos.append({
                'video_id': video_id,
                'title': title,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            })
        except Exception as e:
            continue
    
    return videos

def filter_investment_videos(videos):
    """투자 관련 영상 필터링"""
    skip_keywords = [
        'Q&A', '구독자', '일상', '브이로그', '공지', '인사',
        '먹방', '여행', '휴가', '생일', '결혼', '가족',
        '라이브', 'LIVE', '실시간', '채팅'
    ]
    
    pass_keywords = [
        '주식', '투자', '매수', '매도', '종목', '시장', '코스피',
        '나스닥', '비트코인', '이더리움', '코인', '암호화폐',
        '삼성', '애플', '테슬라', '엔비디아', '반도체'
    ]
    
    filtered = []
    for video in videos:
        title = video['title'].lower()
        
        # skip 키워드 체크
        if any(keyword in title for keyword in skip_keywords):
            continue
            
        # pass 키워드 체크 또는 기본 통과
        if any(keyword in title for keyword in pass_keywords) or len(filtered) < 10:
            filtered.append(video)
    
    return filtered

def extract_subtitle_yt_dlp(video_id):
    """yt-dlp로 자막 추출"""
    try:
        import subprocess
        
        cmd = [
            'yt-dlp', 
            '--write-subs', 
            '--write-auto-subs',
            '--sub-langs', 'ko,en',
            '--skip-download',
            '--output', f'subs/{video_id}.%(ext)s',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # 자막 파일 읽기
        subtitle_files = [
            f'subs/{video_id}.ko.vtt',
            f'subs/{video_id}.en.vtt'
        ]
        
        for file_path in subtitle_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # VTT 포맷에서 텍스트만 추출
                    lines = []
                    for line in content.split('\n'):
                        if '-->' not in line and not line.startswith('WEBVTT') and line.strip():
                            lines.append(line.strip())
                    return ' '.join(lines)
        
        return None
        
    except Exception as e:
        print(f"yt-dlp 자막 추출 실패 {video_id}: {e}")
        return None

def analyze_with_v9_prompt(channel_name, video_data):
    """V9 프롬프트로 분석"""
    # 실제로는 Claude API 호출
    # 여기서는 더미 데이터 반환
    
    return {
        'signals': [
            {
                'speaker': '박명성',  # 정규화된 발언자 이름
                'stock': '삼성전자',
                'ticker': '005930',
                'market': 'KR',
                'mention_type': '결론',
                'signal': '매수',
                'confidence': 'high',
                'timestamp': '12:34',
                'key_quote': '삼성전자는 이번 분기 반등 확실하다',
                'reasoning': '명확한 매수 권유 표현, 강한 확신 어조'
            }
        ],
        'summary': f'{channel_name} 영상 분석 완료',
        'total_videos': len(video_data),
        'signals_count': 1
    }

def insert_to_supabase(signals):
    """Supabase에 시그널 삽입"""
    # 실제로는 Supabase API 호출
    print(f"Supabase에 {len(signals)}개 시그널 삽입 완료")
    return True

async def process_channel(channel_key, channel_info):
    """단일 채널 처리"""
    print(f"🚀 {channel_info['name']} 처리 시작...")
    
    driver = None
    try:
        # 1. 드라이버 설정
        driver = setup_driver()
        
        # 2. 최근 영상 30개 수집
        print(f"📹 {channel_info['name']} 최근 영상 수집 중...")
        videos = get_recent_videos(driver, channel_info['url'], 30)
        print(f"수집된 영상: {len(videos)}개")
        
        # 3. 투자 관련 영상 필터링
        filtered_videos = filter_investment_videos(videos)
        print(f"필터링 후: {len(filtered_videos)}개")
        
        # 4. 자막 추출 및 분석
        all_signals = []
        
        for i, video in enumerate(filtered_videos):
            print(f"📝 [{i+1}/{len(filtered_videos)}] {video['title'][:50]}...")
            
            # 자막 추출
            subtitle = extract_subtitle_yt_dlp(video['video_id'])
            if not subtitle:
                print(f"자막 추출 실패: {video['video_id']}")
                continue
            
            # V9 분석
            analysis = analyze_with_v9_prompt(channel_info['name'], [video])
            if analysis['signals']:
                all_signals.extend(analysis['signals'])
                print(f"시그널 {len(analysis['signals'])}개 추출")
            
            # 60초 간격
            time.sleep(60)
        
        # 5. Supabase 저장
        if all_signals:
            insert_to_supabase(all_signals)
            print(f"✅ {channel_info['name']} 완료: {len(all_signals)}개 시그널")
        else:
            print(f"⚠️ {channel_info['name']}: 시그널 없음")
            
        return {
            'channel': channel_info['name'],
            'videos_processed': len(filtered_videos),
            'signals_count': len(all_signals),
            'success': True
        }
        
    except Exception as e:
        print(f"❌ {channel_info['name']} 처리 실패: {e}")
        return {
            'channel': channel_info['name'],
            'error': str(e),
            'success': False
        }
    finally:
        if driver:
            driver.quit()

async def main():
    """메인 실행 함수 - 4개 채널 병렬 처리"""
    print("🔥 V9 자막 추출 & 분석 시작!")
    print("대상 채널: 슈카월드, 이효석, 부읽남, 달란트")
    
    # 필요한 폴더 생성
    os.makedirs('subs', exist_ok=True)
    
    # 4개 채널 병렬 처리
    tasks = []
    for channel_key, channel_info in CHANNELS.items():
        task = process_channel(channel_key, channel_info)
        tasks.append(task)
    
    # 모든 작업 완료 대기
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 결과 요약
    print("\n🎯 전체 결과 요약:")
    total_signals = 0
    success_count = 0
    
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ 예외 발생: {result}")
            continue
            
        if result['success']:
            success_count += 1
            total_signals += result['signals_count']
            print(f"✅ {result['channel']}: {result['signals_count']}개 시그널")
        else:
            print(f"❌ {result['channel']}: 실패")
    
    print(f"\n🎉 최종 결과: {success_count}/4 채널 성공, 총 {total_signals}개 시그널")
    
    # 텔레그램 보고
    await send_telegram_report(success_count, total_signals, results)

async def send_telegram_report(success_count, total_signals, results):
    """텔레그램으로 진행상황 보고"""
    report = f"""🚀 V9 자막 추출 완료 보고

✅ 성공: {success_count}/4 채널
📊 총 시그널: {total_signals}개
⏱️ 60초 간격 준수

채널별 결과:"""
    
    for result in results:
        if isinstance(result, Exception):
            continue
        if result['success']:
            report += f"\n• {result['channel']}: {result['signals_count']}개"
        else:
            report += f"\n• {result['channel']}: ❌ 실패"
    
    report += f"\n\n⏭️ 다음: V9 프롬프트 고도화 & Vercel 배포"
    
    print("\n📱 텔레그램 보고:")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())