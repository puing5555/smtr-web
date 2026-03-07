#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
subtitle_extractor.py - YouTube 자막 추출
yt-dlp로 한국어 자막 추출, SRT → 텍스트 변환
"""

import subprocess
import sys
import os
import time
import random
import re
import glob


SUBS_BASE_DIR = r'C:\Users\Mario\work\invest-sns\pipeline\subs'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
]


def srt_to_text(srt_content: str) -> str:
    """SRT 형식에서 타임스탬프 제거, 순수 텍스트 추출"""
    lines = srt_content.splitlines()
    text_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 숫자만 있는 줄 (인덱스) 제거
        if line.isdigit():
            continue
        # 타임스탬프 줄 제거 (00:00:00,000 --> 00:00:00,000)
        if re.match(r'\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->', line):
            continue
        # HTML 태그 제거
        line = re.sub(r'<[^>]+>', '', line)
        # 중복 공백 정리
        line = ' '.join(line.split())
        if line:
            text_lines.append(line)
    
    # 중복 제거 (연속된 동일 문장)
    deduped = []
    for line in text_lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)
    
    return '\n'.join(deduped)


def vtt_to_text(vtt_content: str) -> str:
    """VTT 형식에서 타임스탬프 제거, 순수 텍스트 추출"""
    lines = vtt_content.splitlines()
    text_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('WEBVTT'):
            continue
        if re.match(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->', line):
            continue
        if re.match(r'\d{2}:\d{2}\.\d{3}\s*-->', line):
            continue
        # HTML 태그 제거
        line = re.sub(r'<[^>]+>', '', line)
        line = re.sub(r'align:start position:\d+%', '', line)
        line = ' '.join(line.split())
        if line:
            text_lines.append(line)
    
    deduped = []
    for line in text_lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)
    
    return '\n'.join(deduped)


def download_subtitle(video_id: str, channel_handle: str, max_retries: int = 3) -> str | None:
    """
    단일 영상 자막 추출.
    반환: 텍스트 내용 or None (실패 시)
    """
    subs_dir = os.path.join(SUBS_BASE_DIR, channel_handle)
    os.makedirs(subs_dir, exist_ok=True)
    
    output_template = os.path.join(subs_dir, video_id)
    
    # 이미 존재하는지 확인
    existing = glob.glob(os.path.join(subs_dir, f"{video_id}.*"))
    for f in existing:
        if f.endswith('.txt') and 'subtitle' in f:
            with open(f, 'r', encoding='utf-8') as fp:
                return fp.read()
    
    # SRT/VTT 파일이 이미 있으면 변환
    srt_path = os.path.join(subs_dir, f"{video_id}.ko.srt")
    vtt_path = os.path.join(subs_dir, f"{video_id}.ko.vtt")
    
    if os.path.exists(srt_path):
        with open(srt_path, 'r', encoding='utf-8') as f:
            return srt_to_text(f.read())
    if os.path.exists(vtt_path):
        with open(vtt_path, 'r', encoding='utf-8') as f:
            return vtt_to_text(f.read())
    
    ua = random.choice(USER_AGENTS)
    
    for attempt in range(max_retries):
        try:
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--write-auto-sub', '--sub-lang', 'ko',
                '--skip-download', '--convert-subs', 'srt',
                '--user-agent', ua,
                '--no-warnings',
                '-o', output_template,
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding='utf-8', timeout=60
            )
            
            # 에러 텍스트에서 429 확인
            if '429' in (result.stderr or '') or 'Too Many Requests' in (result.stderr or ''):
                print(f"  [자막] 429 에러 - {60}초 대기...")
                time.sleep(60)
                continue
            
            # SRT 파일 확인
            if os.path.exists(srt_path):
                with open(srt_path, 'r', encoding='utf-8') as f:
                    return srt_to_text(f.read())
            
            # VTT 파일 확인 (변환 전)
            vtt_auto = os.path.join(subs_dir, f"{video_id}.ko.vtt")
            if os.path.exists(vtt_auto):
                with open(vtt_auto, 'r', encoding='utf-8') as f:
                    return vtt_to_text(f.read())
            
            # 다른 언어 코드로 시도 (ko-KR)
            srt_kr = os.path.join(subs_dir, f"{video_id}.ko-KR.srt")
            vtt_kr = os.path.join(subs_dir, f"{video_id}.ko-KR.vtt")
            if os.path.exists(srt_kr):
                with open(srt_kr, 'r', encoding='utf-8') as f:
                    return srt_to_text(f.read())
            if os.path.exists(vtt_kr):
                with open(vtt_kr, 'r', encoding='utf-8') as f:
                    return vtt_to_text(f.read())
            
            # 자막 없는 경우 (영상 자체에 자막 없음)
            if 'There are no subtitles' in (result.stderr or '') or 'no subtitles' in (result.stderr or '').lower():
                return None
            
            # 실패
            if attempt < max_retries - 1:
                wait = random.uniform(2, 4)
                time.sleep(wait)
        
        except subprocess.TimeoutExpired:
            print(f"  [자막] 타임아웃 (시도 {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(10)
        except Exception as e:
            print(f"  [자막] 오류: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return None


def extract_subtitles(videos: list[dict], channel_handle: str) -> dict[str, str]:
    """
    여러 영상 자막 추출.
    반환: {video_id: subtitle_text} 딕셔너리
    """
    results = {}
    total = len(videos)
    
    print(f"[자막] 총 {total}개 영상 자막 추출 시작")
    
    for i, video in enumerate(videos):
        video_id = video['video_id']
        title = video.get('title', video_id)[:50]
        
        print(f"  [{i+1}/{total}] {video_id} - {title}")
        
        text = download_subtitle(video_id, channel_handle)
        
        if text:
            results[video_id] = text
            print(f"    ✓ 자막 추출 성공 ({len(text)}자)")
        else:
            print(f"    ✗ 자막 없음 (skip)")
        
        # 레이트리밋 방지: 20개마다 5분 휴식
        if (i + 1) % 20 == 0 and (i + 1) < total:
            print(f"  [자막] 20개 완료 - 5분 휴식...")
            time.sleep(300)
        elif i + 1 < total:
            # 요청 간 랜덤 딜레이 2~4초
            time.sleep(random.uniform(2, 4))
    
    print(f"[자막] 완료 - 성공: {len(results)}/{total}")
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-id', help='단일 영상 ID')
    parser.add_argument('--channel-handle', required=True, help='채널 핸들 (예: GODofIT)')
    args = parser.parse_args()
    
    if args.video_id:
        text = download_subtitle(args.video_id, args.channel_handle)
        if text:
            print(f"자막 추출 성공:\n{text[:500]}...")
        else:
            print("자막 추출 실패")
