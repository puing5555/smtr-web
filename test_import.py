#!/usr/bin/env python3
# 라이브러리 확인
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("Import successful")
    print(f"Class: {YouTubeTranscriptApi}")
    print(f"Methods: {dir(YouTubeTranscriptApi)}")
    
    # 간단한 테스트 (유명한 영상)
    video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    print(f"\nTesting with video: {video_id}")
    
    # 사용 가능한 자막 목록
    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    print("Available transcripts:")
    for transcript in transcripts:
        print(f"  {transcript.language_code}")
    
    # 영어 자막 가져오기
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    print(f"Transcript length: {len(transcript)}")
    if transcript:
        print(f"First line: {transcript[0]}")
        
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()