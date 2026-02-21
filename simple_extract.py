#!/usr/bin/env python3
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def get_subtitles(video_id):
    try:
        # 수동 자막 시도
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'ko-KR'])
        return {'status': 'manual', 'text': ' '.join([t['text'] for t in transcript])}
    except:
        try:
            # 자동생성 자막 시도
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                if transcript.language_code in ['ko', 'ko-KR'] and transcript.is_generated:
                    data = transcript.fetch()
                    return {'status': 'auto', 'text': ' '.join([t['text'] for t in data])}
        except:
            pass
        return {'status': 'failed', 'error': 'no subs'}

def process_raw_data():
    videos = []
    with open('corinpapa_clean.json', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                videos.append({
                    'video_id': data['id'],
                    'title': data['title'],
                    'url': data['url']
                })
            except:
                continue
    return videos

def main():
    print("Starting...")
    
    # 비디오 목록
    videos = process_raw_data()
    print(f"Videos: {len(videos)}")
    
    # 자막 파일
    subtitles_file = 'corinpapa_subtitles.json'
    subtitles = {}
    if os.path.exists(subtitles_file):
        with open(subtitles_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
        print(f"Existing subs: {len(subtitles)}")
    
    # 처리할 것들
    to_process = [v for v in videos if v['title'] not in subtitles]
    print(f"To process: {len(to_process)}")
    
    if not to_process:
        print("All done!")
        return
    
    # 처리
    success = 0
    auto = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for video in to_process:
            future = executor.submit(get_subtitles, video['video_id'])
            futures[future] = video
        
        for i, future in enumerate(as_completed(futures)):
            video = futures[future]
            result = future.result()
            
            result.update({
                'video_id': video['video_id'],
                'title': video['title'],
                'url': video['url']
            })
            
            subtitles[video['title']] = result
            
            if result['status'] == 'manual':
                success += 1
                print(f"[{i+1:3d}/{len(to_process)}] OK manual")
            elif result['status'] == 'auto':
                success += 1
                auto += 1
                print(f"[{i+1:3d}/{len(to_process)}] OK auto")
            else:
                print(f"[{i+1:3d}/{len(to_process)}] FAIL")
            
            # 저장
            if (i + 1) % 20 == 0:
                with open(subtitles_file, 'w', encoding='utf-8') as f:
                    json.dump(subtitles, f, ensure_ascii=False, indent=2)
                print(f"Saved {i+1}")
    
    # 최종 저장
    with open(subtitles_file, 'w', encoding='utf-8') as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)
    
    print(f"Done! Success: {success} (auto: {auto}), Fail: {len(to_process)-success}")

if __name__ == "__main__":
    main()