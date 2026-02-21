#!/usr/bin/env python3
"""
코린이 아빠 채널 영상 목록 수집
"""
import requests
import json
import time
from datetime import datetime

# YouTube Data API v3 키 필요
API_KEY = "YOUR_API_KEY_HERE"  # 여기에 실제 API 키 입력
CHANNEL_ID = "UCkorinipapa1106"  # 코린이 아빠 채널 ID

def get_channel_videos(channel_id, api_key):
    """채널의 모든 영상 목록 가져오기"""
    videos = []
    next_page_token = None
    
    while True:
        # YouTube API 호출
        url = f"https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': api_key,
            'channelId': channel_id,
            'part': 'snippet',
            'order': 'date',
            'type': 'video',
            'maxResults': 50,
        }
        
        if next_page_token:
            params['pageToken'] = next_page_token
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"API 오류: {response.status_code}")
            print(response.text)
            break
        
        data = response.json()
        
        # 영상 정보 추출
        for item in data.get('items', []):
            video_info = {
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'upload_date': item['snippet']['publishedAt'][:10],
                'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description']
            }
            videos.append(video_info)
        
        print(f"수집 완료: {len(videos)}개")
        
        # 다음 페이지 토큰 확인
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
        
        # API 호출 제한 대기
        time.sleep(0.1)
    
    return videos

# API 키가 설정되지 않은 경우 대체 방법
def manual_video_list():
    """수동으로 영상 목록 생성 (테스트용)"""
    return [
        {
            'video_id': 'test123',
            'title': '테스트 영상',
            'url': 'https://www.youtube.com/watch?v=test123',
            'upload_date': '2024-01-01',
            'description': '테스트용 영상입니다'
        }
    ]

def main():
    print("코린이 아빠 채널 영상 목록 수집 시작...")
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  YouTube API 키가 설정되지 않았습니다.")
        print("1. https://console.developers.google.com 에서 YouTube Data API v3 활성화")
        print("2. API 키 생성 후 스크립트에 입력")
        print("3. 또는 yt-dlp 방식으로 수집")
        
        # yt-dlp 방식 제안
        print("\n대안: yt-dlp 사용")
        print("pip install yt-dlp")
        print("yt-dlp --dump-json --playlist-end 50 'https://www.youtube.com/@korinipapa1106/videos'")
        return
    
    try:
        videos = get_channel_videos(CHANNEL_ID, API_KEY)
        
        # JSON 파일로 저장
        output_file = 'korinipapa_videos.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 완료!")
        print(f"   총 영상: {len(videos)}개")
        print(f"   저장 파일: {output_file}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()