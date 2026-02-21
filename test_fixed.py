#!/usr/bin/env python3
import json
from youtube_transcript_api import YouTubeTranscriptApi

def test_video(video_id):
    print(f"Testing video: {video_id}")
    
    try:
        # 정확한 API 호출 방법
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        print("Manual Korean subtitles found!")
        print(f"Length: {len(transcript)} segments")
        if transcript:
            print(f"First text: {transcript[0]['text'][:50]}...")
        return True
    except Exception as e:
        print(f"Manual Korean failed: {str(e)[:100]}...")
    
    try:
        # 사용 가능한 자막 목록 확인
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("Available transcripts:")
        
        found_korean = False
        for transcript in transcript_list:
            print(f"  {transcript.language_code} (Generated: {transcript.is_generated})")
            
            # 한국어 자동생성 자막 시도
            if transcript.language_code in ['ko', 'ko-KR'] and transcript.is_generated:
                print("  -> Trying auto Korean...")
                data = transcript.fetch()
                print(f"  -> Success! {len(data)} segments")
                if data:
                    print(f"  -> First text: {data[0]['text'][:50]}...")
                found_korean = True
                break
                
        if not found_korean:
            print("  No Korean subtitles found")
                
    except Exception as e:
        print(f"List transcripts failed: {str(e)[:100]}...")
    
    return False

# 테스트
video_ids = ["7AaksU-R3dg", "ULXCspCxaSg", "YxI_Tx5Y-qY"]  # 처음 3개만

for i, video_id in enumerate(video_ids):
    print(f"\n--- Video {i+1} ---")
    test_video(video_id)
    print()