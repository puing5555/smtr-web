#!/usr/bin/env python3
from youtube_transcript_api import YouTubeTranscriptApi

def test_video(video_id):
    print(f"Testing video: {video_id}")
    
    try:
        # 사용 가능한 자막 목록
        transcript_list = YouTubeTranscriptApi.list(video_id)
        print("Available transcripts:")
        
        for transcript in transcript_list:
            print(f"  {transcript.language_code} (Generated: {transcript.is_generated})")
            
            # 한국어 자막 시도
            if transcript.language_code in ['ko', 'ko-KR']:
                try:
                    data = transcript.fetch()
                    print(f"  -> Korean success! {len(data)} segments")
                    if data:
                        print(f"  -> First: {data[0]['text'][:50]}...")
                    return True
                except Exception as e:
                    print(f"  -> Korean failed: {e}")
        
        # 영어 자막도 시도
        for transcript in transcript_list:
            if transcript.language_code in ['en', 'en-US']:
                try:
                    data = transcript.fetch()
                    print(f"  -> English fallback! {len(data)} segments")
                    return True
                except:
                    pass
                    
        return False
                
    except Exception as e:
        print(f"List failed: {e}")
        return False

# 코린이 아빠 영상들 테스트
video_ids = ["7AaksU-R3dg", "ULXCspCxaSg", "YxI_Tx5Y-qY"]

for i, video_id in enumerate(video_ids):
    print(f"\n--- Video {i+1} ---")
    success = test_video(video_id)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")