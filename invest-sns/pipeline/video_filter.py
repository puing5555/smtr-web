#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video_filter.py - YouTube 채널 영상 사전 필터링
채널 메타데이터 수집 → 필터링 규칙 적용 → 투자 관련 영상만 통과
"""

import subprocess
import sys
import json
import time
import random
import os
import anthropic

ANTHROPIC_API_KEY = "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"

# 필터링 규칙
EXCLUDE_TITLE_KEYWORDS = ['일상', '먹방', '여행', '브이로그', 'vlog', '구독', '이벤트', '경품', '광고', '협찬', '소개', '인사']
EXCLUDE_SHORTS = ['#shorts', '#쇼츠']

INCLUDE_STOCK_KEYWORDS = [
    '삼성전자', '테슬라', '엔비디아', 'NVIDIA', '애플', 'SK하이닉스', '현대차', '카카오',
    '네이버', '셀트리온', '삼성바이오', 'TSLA', 'AAPL', 'META', '마이크로소프트', 'MSFT',
    '구글', '아마존', '비트코인', '이더리움'
]
INCLUDE_INVEST_KEYWORDS = ['매수', '매도', '포트폴리오', '주가', '실적', '전망', '분석', '추천', '종목', '투자', '주식', '코인']
INCLUDE_MARKET_KEYWORDS = ['코스피', '나스닥', 'S&P', '비트코인', '시장', '증시', '급등', '급락', '상승', '하락']
INCLUDE_URGENT_KEYWORDS = ['긴급', '속보', '돌발', '경보', '주의']
INCLUDE_EARNINGS_KEYWORDS = ['실적', '어닝', '컨콜', 'EPS', '매출', '영업이익']
INCLUDE_POSITION_KEYWORDS = ['포지션', '보유', '매매일지', '수익률']
INCLUDE_AMOUNT_KEYWORDS = ['만원', '억', '달러', '%']

ALL_INCLUDE_KEYWORDS = (
    INCLUDE_STOCK_KEYWORDS + INCLUDE_INVEST_KEYWORDS + INCLUDE_MARKET_KEYWORDS +
    INCLUDE_URGENT_KEYWORDS + INCLUDE_EARNINGS_KEYWORDS + INCLUDE_POSITION_KEYWORDS +
    INCLUDE_AMOUNT_KEYWORDS
)


def fetch_channel_metadata(channel_url: str) -> list[dict]:
    """yt-dlp로 채널 메타데이터 수집"""
    print(f"[필터] 채널 메타데이터 수집 중: {channel_url}")
    
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--flat-playlist', '--dump-json',
        '--no-warnings',
        channel_url
    ]
    
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding='utf-8',
            timeout=300
        )
        
        videos = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                video = {
                    'video_id': data.get('id', ''),
                    'title': data.get('title', ''),
                    'duration': data.get('duration') or 0,
                    'view_count': data.get('view_count') or 0,
                    'upload_date': data.get('upload_date', ''),
                }
                if video['video_id']:
                    videos.append(video)
            except json.JSONDecodeError:
                continue
        
        print(f"[필터] 총 {len(videos)}개 영상 메타데이터 수집 완료")
        return videos
    
    except subprocess.TimeoutExpired:
        print("[필터] 타임아웃 - 수집된 데이터 사용")
        return []
    except Exception as e:
        print(f"[필터] 오류: {e}")
        return []


def apply_hard_rules(video: dict) -> str:
    """하드 룰 적용. 반환값: 'include' / 'exclude' / 'ambiguous'"""
    duration = video.get('duration', 0) or 0
    view_count = video.get('view_count', 0) or 0
    title = video.get('title', '') or ''
    title_lower = title.lower()
    
    # 제외 규칙
    if duration < 60:
        return 'exclude'
    if duration > 7200:
        return 'exclude'
    if view_count < 1000:
        return 'exclude'
    for kw in EXCLUDE_TITLE_KEYWORDS:
        if kw in title:
            return 'exclude'
    for kw in EXCLUDE_SHORTS:
        if kw.lower() in title_lower:
            return 'exclude'
    
    # 포함 우선순위
    for kw in ALL_INCLUDE_KEYWORDS:
        if kw.lower() in title_lower:
            return 'include'
    
    return 'ambiguous'


def ai_filter_batch(titles: list[str]) -> list[bool]:
    """AI로 모호한 제목들 배치 판단"""
    if not titles:
        return []
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    title_list = '\n'.join([f"[{i+1}]: {t}" for i, t in enumerate(titles)])
    prompt = f"다음 유튜브 영상 제목들이 주식/코인 투자 관련 정보를 담고 있을 가능성이 높은지 판단해. 각 제목에 대해 yes/no로만 답해. 형식: [번호]: yes/no\n{title_list}"
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        results = [False] * len(titles)
        
        for line in result_text.splitlines():
            line = line.strip()
            if not line:
                continue
            # 형식: [번호]: yes/no
            if ']:' in line:
                try:
                    bracket_part = line.split(']:')[0].strip()
                    num = int(bracket_part.replace('[', '').strip())
                    answer_part = line.split(']:')[1].strip().lower()
                    if 1 <= num <= len(titles):
                        results[num - 1] = 'yes' in answer_part
                except (ValueError, IndexError):
                    continue
        
        return results
    
    except Exception as e:
        print(f"[필터] AI 판단 오류: {e}")
        return [False] * len(titles)


def filter_videos(channel_url: str, output_path: str = None) -> list[dict]:
    """메인 필터링 함수"""
    videos = fetch_channel_metadata(channel_url)
    if not videos:
        print("[필터] 메타데이터 없음")
        return []
    
    included = []
    excluded = []
    ambiguous_indices = []
    ambiguous_videos = []
    
    for video in videos:
        decision = apply_hard_rules(video)
        video['filter_decision'] = decision
        if decision == 'include':
            included.append(video)
        elif decision == 'exclude':
            excluded.append(video)
        else:
            ambiguous_indices.append(len(included) + len(ambiguous_videos))
            ambiguous_videos.append(video)
    
    print(f"[필터] 하드룰 결과 - 포함: {len(included)}, 제외: {len(excluded)}, 모호: {len(ambiguous_videos)}")
    
    # AI 배치 판단 (50개씩)
    if ambiguous_videos:
        print(f"[필터] AI 판단 시작: {len(ambiguous_videos)}개")
        batch_size = 50
        for i in range(0, len(ambiguous_videos), batch_size):
            batch = ambiguous_videos[i:i + batch_size]
            titles = [v['title'] for v in batch]
            decisions = ai_filter_batch(titles)
            
            for j, video in enumerate(batch):
                if j < len(decisions) and decisions[j]:
                    video['filter_decision'] = 'include_ai'
                    included.append(video)
                else:
                    video['filter_decision'] = 'exclude_ai'
            
            if i + batch_size < len(ambiguous_videos):
                time.sleep(2)
    
    print(f"[필터] 최종 통과 영상: {len(included)}개 / 전체: {len(videos)}개")
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(included, f, ensure_ascii=False, indent=2)
        print(f"[필터] 결과 저장: {output_path}")
    
    return included


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', required=True, help='YouTube 채널 URL')
    parser.add_argument('--output', help='결과 JSON 저장 경로')
    args = parser.parse_args()
    
    videos = filter_videos(args.channel, args.output)
    print(f"\n필터 통과: {len(videos)}개")
    for v in videos[:5]:
        print(f"  - {v['video_id']}: {v['title'][:60]}")
