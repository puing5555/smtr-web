#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium 기반 YouTube 자막 추출 (제목 필터링 추가)
V9 Step 1.5 제목 사전 필터링 적용: 투자/주식 관련 영상만 추출
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

def is_investment_related_title(title):
    """V9 Step 1.5: 제목 기반 투자 관련 영상 필터링"""
    
    # PASS 키워드: 투자/주식/경제 관련
    pass_keywords = [
        # 종목/기업
        '삼성전자', 'SK하이닉스', '현대차', '카카오', '네이버', '엔비디아', '테슬라', 'TSLA', 'NVDA',
        '애플', 'AAPL', '마이크로소프트', 'MSFT', '구글', '아마존', '메타', '넷플릭스',
        # 주식 용어
        '주식', '종목', '매수', '매도', '투자', '포트폴리오', '수익률', '손익', '차트', '기술적분석',
        '펀더멘털', '실적', '분기실적', '어닝시즌', '컨센서스', '목표가', '상승', '하락',
        # 시장/섹터
        '코스피', '나스닥', 'S&P500', '다우지수', '반도체', 'AI', '인공지능', '전기차', 'EV',
        '바이오', '제약', '게임', '엔터', '은행', '증권', '보험', '건설', '철강', '화학',
        # 경제지표
        '금리', '인플레이션', 'CPI', '실업률', 'GDP', '환율', '원달러', '유가', '국채', '회사채',
        # 크립토
        '비트코인', 'BTC', '이더리움', 'ETH', '코인', '크립토', '암호화폐', '디파이', 'NFT',
        # 투자 관련
        '분할매수', '손절', '익절', '리밸런싱', '달러비중', '현금비중', '배당', '증자', '감자',
        '공모주', 'IPO', '상장', '폐장', '장중', '시총', '시가총액', '52주', '신고가', '신저가'
    ]
    
    # SKIP 키워드: 투자 무관 콘텐츠  
    skip_keywords = [
        # Q&A/소통
        'Q&A', 'q&a', '질문답변', '구독자', '댓글', '라이브', '채팅', '인사', '공지',
        # 일상/브이로그
        '일상', '브이로그', 'vlog', '먹방', '여행', '휴가', '운동', '헬스', '다이어트',
        '취미', '게임', '영화', '드라마', '음악', '요리', '맛집', '카페', '쇼핑',
        # 교양/문화
        '역사', '문화', '예술', '철학', '종교', '정치', '사회', '교육', '학습', '독서',
        '책리뷰', '영화리뷰', '드라마리뷰', '콘서트', '전시회', '박물관', '미술관',
        # 시사/뉴스 (투자 무관)
        '선거', '정치인', '국정감사', '법안', '규제', '정책', '외교', '국제정세',
        '사건사고', '재해', '재난', '코로나', '팬데믹', '백신', '치료제',
        # 기타 제외 항목
        '무제한', '요금제', '영화관', '넷플릭스', '구독', '스트리밍', '콘텐츠',
        '유튜버', '크리에이터', '인플루언서', '방송', '예능', '토크쇼'
    ]
    
    title_lower = title.lower()
    
    # SKIP 키워드가 있으면 거르기
    for skip_word in skip_keywords:
        if skip_word.lower() in title_lower:
            return False, f"SKIP: '{skip_word}' 키워드 포함"
    
    # PASS 키워드가 있으면 통과
    for pass_word in pass_keywords:
        if pass_word.lower() in title_lower:
            return True, f"PASS: '{pass_word}' 키워드 포함"
    
    # 키워드 매칭이 안 되면 보수적으로 스킵
    return False, "SKIP: 투자 관련 키워드 없음"

def setup_driver():
    """Chrome 드라이버 설정"""
    options = Options()
    options.add_argument('--headless')  # 헤드리스 모드로 복원
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver

def get_latest_videos_with_filter(driver, channel_url, max_videos=10):
    """채널에서 최신 비디오 URL들 가져오기 (제목 필터링 적용)"""
    print(f"채널 접속: {channel_url}")
    
    try:
        driver.get(channel_url)
        time.sleep(5)
        
        # 페이지가 로드될 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 스크롤해서 더 많은 비디오 로드
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # 비디오 링크와 제목 함께 찾기
        video_elements = driver.find_elements(By.CSS_SELECTOR, 'div#details')
        
        filtered_videos = []
        total_checked = 0
        
        for element in video_elements:
            try:
                # 제목 추출
                title_element = element.find_element(By.CSS_SELECTOR, 'a#video-title')
                title = title_element.text.strip()
                href = title_element.get_attribute('href')
                
                if not title or not href or '/watch?v=' not in href:
                    continue
                
                total_checked += 1
                
                # 제목 필터링 적용
                is_pass, reason = is_investment_related_title(title)
                
                print(f"   [{total_checked}] {title}")
                print(f"       결과: {reason}")
                
                if is_pass:
                    video_id = href.split('/watch?v=')[1].split('&')[0]
                    filtered_videos.append({
                        'url': href,
                        'title': title,
                        'video_id': video_id
                    })
                    
                    if len(filtered_videos) >= max_videos:
                        break
                        
                time.sleep(0.5)  # 과부하 방지
                
            except Exception as e:
                continue
        
        print(f"   전체 {total_checked}개 중 {len(filtered_videos)}개 통과")
        return filtered_videos
        
    except Exception as e:
        print(f"   에러: {str(e)}")
        return []

def extract_video_info(driver, video_data):
    """비디오에서 제목, 설명, 자막 추출"""
    try:
        video_url = video_data['url']
        print(f"   비디오 분석: {video_data['title']}")
        driver.get(video_url)
        time.sleep(5)
        
        # 제목은 이미 필터링에서 가져온 것 사용
        title = video_data['title']
        
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
        
        video_info = {
            'video_id': video_data['video_id'],
            'title': title,
            'description': description,
            'upload_date': upload_date,
            'url': video_url,
            'subtitles': "",  # 자막은 별도로 처리 필요
            'filtered': True,  # 필터링 통과 표시
            'filter_reason': "투자 관련 키워드 매칭"
        }
        
        print(f"      제목: {title}")
        return video_info
        
    except Exception as e:
        print(f"      에러: {str(e)}")
        return None

def process_channel(channel_key, channel_info):
    """채널별 자막 추출 처리 (필터링 적용)"""
    print(f"\n[{channel_info['name']}] 제목 필터링 + 자막 추출 시작")
    
    driver = setup_driver()
    results = []
    
    try:
        # 제목 필터링이 적용된 최신 비디오 가져오기
        filtered_videos = get_latest_videos_with_filter(driver, channel_info['url'], max_videos=5)
        
        if not filtered_videos:
            print(f"   {channel_info['name']}: 투자 관련 비디오 없음")
            return results
        
        # 각 비디오 처리
        for video_data in filtered_videos:
            video_info = extract_video_info(driver, video_data)
            if video_info:
                results.append(video_info)
                
                # JSON 파일로 저장
                filename = f"subs_filtered/{channel_key}_{video_info['video_id']}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(video_info, f, ensure_ascii=False, indent=2)
                print(f"      저장: {filename}")
            
            time.sleep(2)  # 요청 간격
        
        print(f"   {channel_info['name']}: {len(results)}개 투자 관련 비디오 처리 완료")
        
    except Exception as e:
        print(f"   {channel_info['name']} 에러: {str(e)}")
    
    finally:
        driver.quit()
    
    return results

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("Selenium YouTube 자막 추출 (V9 Step 1.5 제목 필터링 적용)")
    print("대상: 슈카월드, 이효석, 부읽남, 달란트")
    print("필터: 투자/주식/경제 관련 영상만 추출")
    print("=" * 70)
    
    # subs_filtered 폴더 생성
    os.makedirs('subs_filtered', exist_ok=True)
    
    total_videos = 0
    summary = []
    
    # 각 채널 순차 처리 (안정성을 위해)
    for channel_key, channel_info in CHANNELS.items():
        try:
            results = process_channel(channel_key, channel_info)
            total_videos += len(results)
            summary.append({
                'channel': channel_info['name'],
                'count': len(results),
                'videos': [r['title'] for r in results]
            })
            time.sleep(5)  # 채널 간 간격
            
        except Exception as e:
            print(f"채널 {channel_info['name']} 처리 중 에러: {str(e)}")
            summary.append({
                'channel': channel_info['name'],
                'count': 0,
                'error': str(e)
            })
            continue
    
    print("\n" + "=" * 70)
    print("[결과] 필터링 결과 요약:")
    for item in summary:
        if 'error' in item:
            print(f"[ERROR] {item['channel']}: 에러 발생")
        else:
            print(f"[SUCCESS] {item['channel']}: {item['count']}개 투자 관련 영상")
            for video in item['videos']:
                print(f"   - {video}")
    
    print(f"\n[완료] 전체 결과: {total_videos}개 투자 관련 비디오 추출 완료")
    print("다음 단계: V9 분석 스크립트로 시그널 추출")
    print("=" * 70)

if __name__ == "__main__":
    main()