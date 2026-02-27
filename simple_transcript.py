#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from youtube_transcript_api import YouTubeTranscriptApi

# 첫 번째 영상만 테스트
video_id = "6R1HiMUAQkM"
print(f"Testing transcript extraction for video: {video_id}")

try:
    # 간단한 방법으로 자막 가져오기
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    
    print("Success! Transcript found:")
    for i, entry in enumerate(transcript[:5]):  # 처음 5개만 출력
        timestamp = f"{int(entry['start']//60):02d}:{int(entry['start']%60):02d}"
        print(f"[{timestamp}] {entry['text']}")
    
    print(f"\nTotal entries: {len(transcript)}")
    
except Exception as e:
    print(f"Error: {e}")
    print("Trying with different language codes...")
    
    # 다른 언어 코드들 시도
    for lang in ['ko', 'ko-KR', 'kr', 'en']:
        try:
            print(f"Trying language: {lang}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
            print(f"Success with {lang}!")
            break
        except Exception as e2:
            print(f"Failed with {lang}: {e2}")