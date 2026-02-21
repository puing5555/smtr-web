#!/usr/bin/env python3
import json
from youtube_transcript_api import YouTubeTranscriptApi

def test_video(video_id):
    print(f"Testing video: {video_id}")
    
    try:
        # 수동 자막
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'ko-KR'])
        print("Manual Korean subtitles found!")
        print(transcript[:2])  # 처음 2개만 출력
        return True
    except Exception as e:
        print(f"Manual Korean failed: {e}")
    
    try:
        # 자동생성 자막 리스트
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("Available transcripts:")
        for transcript in transcript_list:
            print(f"  {transcript.language_code} - Generated: {transcript.is_generated}")
            
            if transcript.language_code in ['ko', 'ko-KR'] and transcript.is_generated:
                print("Trying auto Korean...")
                data = transcript.fetch()
                print("Auto Korean subtitles found!")
                print(data[:2])
                return True
                
    except Exception as e:
        print(f"Auto failed: {e}")
    
    return False

# 처음 몇 개 비디오 테스트
with open('corinpapa_clean.json', 'r', encoding='utf-8') as f:
    videos = []
    for line in f:
        try:
            data = json.loads(line.strip())
            videos.append(data['id'])
            if len(videos) >= 5:  # 처음 5개만
                break
        except:
            continue

print(f"Testing {len(videos)} videos...")
for i, video_id in enumerate(videos):
    print(f"\n--- Video {i+1}/{len(videos)} ---")
    test_video(video_id)
    print()