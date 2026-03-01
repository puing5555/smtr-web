#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script using yt-dlp to extract subtitles
"""

import yt_dlp
import os

# Test with the same video ID
test_video_id = "R6w3T3eUVIs"  # First video from 삼프로TV

print(f"Testing yt-dlp with video: {test_video_id}")

# Create yt-dlp options for subtitle extraction
ydl_opts = {
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['ko'],
    'subtitlesformat': 'vtt',
    'skip_download': True,
    'outtmpl': f'{test_video_id}_%(title)s.%(ext)s',
    'quiet': False,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Extracting video info...")
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={test_video_id}", download=False)
        
        print(f"Title: {info.get('title', 'Unknown')}")
        print(f"Duration: {info.get('duration', 'Unknown')} seconds")
        
        # Check available subtitles
        subtitles = info.get('subtitles', {})
        automatic_captions = info.get('automatic_captions', {})
        
        print(f"Manual subtitles available: {list(subtitles.keys())}")
        print(f"Auto subtitles available: {list(automatic_captions.keys())}")
        
        # Download subtitles
        print("Downloading subtitles...")
        ydl.download([f"https://www.youtube.com/watch?v={test_video_id}"])
        
        # Check if subtitle file was created
        vtt_files = [f for f in os.listdir('.') if f.endswith('.vtt') and test_video_id in f]
        print(f"Subtitle files created: {vtt_files}")
        
        if vtt_files:
            # Read the first VTT file
            with open(vtt_files[0], 'r', encoding='utf-8') as f:
                vtt_content = f.read()
                print(f"VTT file size: {len(vtt_content)} characters")
                print(f"First 500 characters:\n{vtt_content[:500]}")
            
            # Clean up
            os.remove(vtt_files[0])
            print(f"Cleaned up {vtt_files[0]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete.")