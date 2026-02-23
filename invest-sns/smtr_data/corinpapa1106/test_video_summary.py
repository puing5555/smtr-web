#!/usr/bin/env python3
import json
import anthropic
from step0_extract_8types_claude import SYSTEM_PROMPT, extract_signals_from_subtitle

# 단일 영상으로 video_summary 필드 테스트
client = anthropic.Anthropic()
video_id = "-brWAKvRaqI"

# 자막 읽기
with open(f"{video_id}.txt", 'r', encoding='utf-8') as f:
    subtitle = f.read()

title = "Bitmine (BMNR) and the Triangle of Desire"
channel = "코린이 아빠"

print(f"Testing video: {video_id}")
print(f"Title: {title}")
print("\n" + "="*50)

try:
    result = extract_signals_from_subtitle(client, video_id, subtitle, title, channel)
    print("API call successful!")
    print(f"Result keys: {list(result.keys())}")
    
    if "video_summary" in result:
        print(f"video_summary found: {result['video_summary']}")
    else:
        print("video_summary field missing!")
    
    print(f"Number of signals: {len(result.get('signals', []))}")
    
    # 전체 결과를 파일로 저장
    with open('test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Result saved to test_result.json")
    
except Exception as e:
    print(f"Error: {e}")