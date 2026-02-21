#!/usr/bin/env python3
"""
코린이 아빠 채널 데이터 정리 및 자막 추출
"""
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_raw_data():
    """raw JSON을 정리된 형태로 변환"""
    videos = []
    
    with open('corinpapa_clean.json', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                video = {
                    'video_id': data['id'],
                    'title': data['title'],
                    'url': data['url'],
                    'duration': data.get('duration', 0),
                    'view_count': data.get('view_count', 0),
                    'description': data.get('description', '')[:200] + '...' if data.get('description') else ''
                }
                videos.append(video)
            except json.JSONDecodeError:
                continue
    
    # 정리된 데이터 저장
    with open('corinpapa_videos.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    
    print(f"비디오 데이터 정리 완료: {len(videos)}개")
    return videos

def get_subtitles(video_id):
    """자막 추출 (수동 → 자동생성 순으로 시도)"""
    try:
        # 1. 먼저 수동 자막 시도
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'ko-KR'])
        return {'status': 'manual', 'text': ' '.join([t['text'] for t in transcript])}
    except:
        try:
            # 2. 자동생성 자막 시도 (생성된 자막 포함)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 한국어 자동생성 자막 찾기
            for transcript in transcript_list:
                if transcript.language_code in ['ko', 'ko-KR']:
                    if transcript.is_generated:  # 자동생성 자막
                        data = transcript.fetch()
                        return {'status': 'auto', 'text': ' '.join([t['text'] for t in data])}
            
            # 그래도 없으면 영어 자막이라도 시도
            for transcript in transcript_list:
                if transcript.language_code in ['en', 'en-US', 'en-GB']:
                    data = transcript.fetch()
                    return {'status': 'en', 'text': ' '.join([t['text'] for t in data])}
            
            return {'status': 'no_subs', 'error': 'No Korean or English subtitles'}
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

def process_video(video):
    """개별 비디오 처리"""
    result = get_subtitles(video['video_id'])
    result.update({
        'video_id': video['video_id'],
        'title': video['title'],
        'url': video['url'],
        'duration': video['duration'],
        'view_count': video['view_count']
    })
    
    return video['title'], result

def main():
    print("코린이 아빠 채널 처리 시작...")
    
    # 1. Raw 데이터 정리
    if not os.path.exists('corinpapa_videos.json'):
        videos = process_raw_data()
    else:
        with open('corinpapa_videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        print(f"기존 비디오 데이터 로드: {len(videos)}개")
    
    # 2. 기존 자막 파일 확인
    subtitles_file = 'corinpapa_subtitles.json'
    if os.path.exists(subtitles_file):
        with open(subtitles_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
        print(f"기존 자막 데이터: {len(subtitles)}개")
    else:
        subtitles = {}
    
    # 3. 처리할 비디오 필터링
    to_process = []
    for video in videos:
        title = video['title']
        if title not in subtitles or subtitles[title]['status'] == 'failed':
            to_process.append(video)
    
    print(f"처리할 비디오: {len(to_process)}개")
    
    if not to_process:
        print("모든 비디오 처리 완료!")
        return
    
    # 4. 병렬 자막 추출 (6개씩)
    success_count = 0
    auto_count = 0
    en_count = 0
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_video = {executor.submit(process_video, video): video for video in to_process}
        
        for i, future in enumerate(as_completed(future_to_video)):
            title, result = future.result()
            subtitles[title] = result
            
            status = result['status']
            if status == 'manual':
                success_count += 1
                print(f"  [{i+1:3d}/{len(to_process)}] OK {title[:60]}...")
            elif status == 'auto':
                success_count += 1
                auto_count += 1
                print(f"  [{i+1:3d}/{len(to_process)}] AUTO {title[:60]}...")
            elif status == 'en':
                success_count += 1
                en_count += 1
                print(f"  [{i+1:3d}/{len(to_process)}] EN {title[:60]}...")
            else:
                print(f"  [{i+1:3d}/{len(to_process)}] FAIL {title[:60]}... ({result.get('error', 'failed')})")
            
            # 20개마다 저장
            if (i + 1) % 20 == 0:
                with open(subtitles_file, 'w', encoding='utf-8') as f:
                    json.dump(subtitles, f, ensure_ascii=False, indent=2)
                print(f"    저장 ({i+1}/{len(to_process)})")
    
    # 5. 최종 저장
    with open(subtitles_file, 'w', encoding='utf-8') as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)
    
    print(f"\n처리 완료!")
    print(f"   자막 성공: {success_count}개")
    print(f"      수동: {success_count-auto_count-en_count}개")
    print(f"      자동: {auto_count}개") 
    print(f"      영어: {en_count}개")
    print(f"   실패: {len(to_process) - success_count}개")
    print(f"   전체: {len(subtitles)}개")

if __name__ == "__main__":
    main()