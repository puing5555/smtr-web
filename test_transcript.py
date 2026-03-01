#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to check YouTube Transcript API
"""

from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript, NoTranscriptFound

# Test with one video ID from the list
test_video_id = "R6w3T3eUVIs"  # First video from 삼프로TV

print("Testing YouTube Transcript API...")
print(f"Video ID: {test_video_id}")

try:
    # Get transcript list
    print("Getting transcript list...")
    transcript_list = YouTubeTranscriptApi().list(test_video_id)
    print("Transcript list obtained successfully")
    
    # Print available transcripts
    print("Available transcripts:")
    for transcript in transcript_list:
        print(f"  - Language: {transcript.language} ({transcript.language_code})")
        print(f"    Generated: {transcript.is_generated}")
    
    # Try to get Korean transcript
    try:
        print("Trying to get Korean transcript...")
        transcript = transcript_list.find_transcript(['ko'])
        subtitle_data = transcript.fetch()
        
        # Convert to text
        subtitle_text = ' '.join([item['text'] for item in subtitle_data])
        print(f"Success! Extracted {len(subtitle_text)} characters")
        print(f"First 200 characters: {subtitle_text[:200]}...")
        
    except NoTranscriptFound:
        print("No Korean transcript found, trying auto-generated...")
        try:
            transcript = transcript_list.find_generated_transcript(['ko'])
            subtitle_data = transcript.fetch()
            subtitle_text = ' '.join([item['text'] for item in subtitle_data])
            print(f"Success! Extracted auto-generated {len(subtitle_text)} characters")
            print(f"First 200 characters: {subtitle_text[:200]}...")
        except NoTranscriptFound:
            print("No auto-generated Korean transcript found")

except CouldNotRetrieveTranscript as e:
    print(f"Could not retrieve transcript: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete.")