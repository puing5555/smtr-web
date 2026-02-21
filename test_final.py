#!/usr/bin/env python3
from youtube_transcript_api import YouTubeTranscriptApi

def test_video(video_id):
    print(f"Testing video: {video_id}")
    
    try:
        api = YouTubeTranscriptApi()
        
        # 바로 한국어 자막 시도
        try:
            transcript = api.fetch(video_id, languages=['ko', 'ko-KR'])
            print(f"Direct Korean success! {len(transcript)} segments")
            if transcript:
                print(f"First: {transcript[0]['text'][:50]}...")
            return 'manual'
        except Exception as e:
            print(f"Direct Korean failed: {str(e)[:50]}...")
        
        # 사용 가능한 자막 목록 확인
        transcript_list = api.list(video_id)
        print("Available transcripts:")
        
        korean_found = False
        auto_found = False
        
        for transcript in transcript_list:
            print(f"  {transcript.language_code} (Generated: {transcript.is_generated})")
            
            # 한국어 자동생성 자막
            if transcript.language_code in ['ko', 'ko-KR'] and transcript.is_generated and not auto_found:
                try:
                    data = transcript.fetch()
                    print(f"  -> Auto Korean success! {len(data)} segments")
                    auto_found = True
                except Exception as e:
                    print(f"  -> Auto Korean failed: {e}")
            
            # 한국어 수동 자막
            elif transcript.language_code in ['ko', 'ko-KR'] and not transcript.is_generated and not korean_found:
                try:
                    data = transcript.fetch()
                    print(f"  -> Manual Korean success! {len(data)} segments")
                    korean_found = True
                except Exception as e:
                    print(f"  -> Manual Korean failed: {e}")
        
        if korean_found:
            return 'manual'
        elif auto_found:
            return 'auto'
        else:
            return 'none'
                
    except Exception as e:
        print(f"API failed: {e}")
        return 'error'

# 테스트
video_ids = ["7AaksU-R3dg", "ULXCspCxaSg", "YxI_Tx5Y-qY"]

results = {}
for i, video_id in enumerate(video_ids):
    print(f"\n--- Video {i+1}: {video_id} ---")
    result = test_video(video_id)
    results[video_id] = result
    print(f"Result: {result}")

print(f"\nSummary:")
for vid, res in results.items():
    print(f"  {vid}: {res}")