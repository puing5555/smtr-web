#!/usr/bin/env python3
"""
코린이 아빠 채널 자막 추출 (자동생성 포함)
"""
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def extract_video_id(url):
    """YouTube URL에서 video ID 추출"""
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return None

def get_subtitles(video_id):
    """자막 추출 (수동 → 자동생성 순으로 시도)"""
    try:
        # 1. 먼저 수동 자막 시도
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'ko-KR'])
        return {'status': 'manual', 'text': ' '.join([t['text'] for t in transcript])}
    except:
        try:
            # 2. 자동생성 자막 시도
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['ko', 'ko-KR'], 
                preserve_formatting=True
            )
            return {'status': 'auto', 'text': ' '.join([t['text'] for t in transcript])}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

def process_video(video_data):
    """개별 비디오 처리"""
    video_id = extract_video_id(video_data['url'])
    if not video_id:
        return video_data['title'], {'status': 'no_id'}
    
    result = get_subtitles(video_id)
    result['video_id'] = video_id
    result['title'] = video_data['title']
    result['upload_date'] = video_data.get('upload_date', '')
    
    return video_data['title'], result

def main():
    # 기존 비디오 데이터 로드
    with open('korinipapa_videos.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    print(f"총 비디오: {len(videos)}개")
    
    # 기존 자막 파일이 있으면 로드
    subtitles_file = 'korinipapa_subtitles.json'
    if os.path.exists(subtitles_file):
        with open(subtitles_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
        print(f"기존 자막: {len(subtitles)}개")
    else:
        subtitles = {}
    
    # 처리할 비디오 필터링 (이미 성공한 건 제외)
    to_process = []
    for video in videos:
        title = video['title']
        if title not in subtitles or subtitles[title]['status'] == 'failed':
            to_process.append(video)
    
    print(f"처리할 비디오: {len(to_process)}개")
    
    if not to_process:
        print("모든 비디오 처리 완료!")
        return
    
    # 병렬 처리 (4개씩)
    success_count = 0
    auto_count = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 작업 제출
        future_to_video = {executor.submit(process_video, video): video for video in to_process}
        
        for i, future in enumerate(as_completed(future_to_video)):
            title, result = future.result()
            subtitles[title] = result
            
            if result['status'] == 'manual':
                success_count += 1
                print(f"  [{i+1}/{len(to_process)}] ✅ {title[:50]}...")
            elif result['status'] == 'auto':
                success_count += 1
                auto_count += 1
                print(f"  [{i+1}/{len(to_process)}] 🤖 {title[:50]}... (자동)")
            else:
                print(f"  [{i+1}/{len(to_process)}] ❌ {title[:50]}... ({result.get('error', 'failed')})")
            
            # 10개마다 저장
            if (i + 1) % 10 == 0:
                with open(subtitles_file, 'w', encoding='utf-8') as f:
                    json.dump(subtitles, f, ensure_ascii=False, indent=2)
                print(f"    💾 중간 저장 완료 ({i+1}/{len(to_process)})")
    
    # 최종 저장
    with open(subtitles_file, 'w', encoding='utf-8') as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 완료!")
    print(f"   성공: {success_count}개 (수동: {success_count-auto_count}, 자동: {auto_count})")
    print(f"   실패: {len(to_process) - success_count}개")
    print(f"   전체: {len(subtitles)}개 자막 보유")

if __name__ == "__main__":
    main()