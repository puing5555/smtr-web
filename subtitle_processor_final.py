#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Subtitle Extraction and Summary Generation Script
현재 상황: YouTube가 이 IP를 차단하여 자막 추출이 불가능한 상태
"""

import time
import requests
from typing import List, Dict

# Supabase configuration
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

# Video IDs to process
VIDEO_IDS = {
    "코린이아빠": ["XxlsTMRDR_o", "pRTYEzspqyU", "IiPJSJ42H4o", "3eeUC7UBaG4", "awXkJ9hK-a0", 
                "82TEaq8GIfc", "7AaksU-R3dg", "A7qHwvcGh9A", "Vy2jrX-uCbY", "TjKVuAGhC1M", "PGQW7nyoRRI"],
    "삼프로TV": ["R6w3T3eUVIs", "-US4r1E1kOQ", "XFHD_1M3Mxg", "ldT75QwBB6g", "x0TKvrIdIwI", 
               "irK0YCnox78", "qYAiv0Kljas", "I4Tt3tevuTU", "8-hYd-8eojE", "hxpOT8n_ICw"],
    "달란트투자": ["kFa9RxL4HnA", "_MrBnIb0jOk"]
}

# Headers for Supabase API
HEADERS = {
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "apikey": SUPABASE_SERVICE_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

class SubtitleProcessor:
    def __init__(self):
        self.processed_count = 0
        self.success_count = 0
        self.failed_count = 0
    
    def update_video_summary(self, video_id: str, summary: str) -> bool:
        """Update video_summary column in the database."""
        try:
            url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
            
            data = {
                "video_summary": summary
            }
            
            params = {
                "video_id": f"eq.{video_id}"
            }
            
            response = requests.patch(url, headers=HEADERS, json=data, params=params)
            
            if response.status_code == 204:
                print(f"  [SUCCESS] Updated video_summary for {video_id}")
                return True
            else:
                print(f"  [FAILED] Failed to update video_summary for {video_id}: {response.status_code}")
                if response.text:
                    print(f"    Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] Error updating video_summary for {video_id}: {e}")
            return False
    
    def update_subtitle_text(self, video_id: str, subtitle_text: str) -> bool:
        """Update subtitle_text column in the database."""
        try:
            url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
            
            data = {
                "subtitle_text": subtitle_text
            }
            
            params = {
                "video_id": f"eq.{video_id}"
            }
            
            response = requests.patch(url, headers=HEADERS, json=data, params=params)
            
            if response.status_code == 204:
                print(f"  [SUCCESS] Updated subtitle_text for {video_id}")
                return True
            else:
                print(f"  [FAILED] Failed to update subtitle_text for {video_id}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] Error updating subtitle_text for {video_id}: {e}")
            return False
    
    def process_videos_with_ip_block_issue(self):
        """Process videos when IP is blocked - update with explanatory messages."""
        print("현재 상황 분석:")
        print("- YouTube가 이 IP 주소를 차단하여 자막 추출이 불가능")
        print("- 코린이아빠 채널의 일부 영상은 멤버십 전용 콘텐츠")
        print("- 삼프로TV 영상에서는 자막 정보 확인 가능하나 다운로드 시 429 에러")
        print("")
        
        print("해결책:")
        print("1. VPN 사용하여 다른 IP에서 실행")
        print("2. 개인 컴퓨터에서 실행 (클라우드 IP가 아닌 환경)")
        print("3. 프록시 설정 사용")
        print("")
        
        # For now, update database with appropriate messages
        for channel_name, video_ids in VIDEO_IDS.items():
            print(f"\n처리 중: {channel_name} ({len(video_ids)}개 영상)")
            
            for video_id in video_ids:
                self.processed_count += 1
                print(f"  영상 {self.processed_count}: {video_id}")
                
                # Check if this is a members-only video (코린이아빠 경우)
                if channel_name == "코린이아빠":
                    summary = f"{channel_name}의 투자 관련 콘텐츠입니다. 현재 자막 추출이 제한되어 상세한 요약을 제공할 수 없습니다."
                    subtitle_placeholder = "[자막 추출 제한: 멤버십 콘텐츠 또는 IP 차단]"
                else:
                    summary = f"{channel_name}에서 제공하는 투자 분석 콘텐츠입니다. 현재 자막 추출이 제한되어 상세한 요약을 제공할 수 없습니다."
                    subtitle_placeholder = "[자막 추출 제한: IP 차단으로 인한 일시적 제한]"
                
                # Update subtitle_text
                if self.update_subtitle_text(video_id, subtitle_placeholder):
                    # Update video_summary
                    if self.update_video_summary(video_id, summary):
                        self.success_count += 1
                    else:
                        self.failed_count += 1
                else:
                    self.failed_count += 1
                
                # Small delay to avoid overwhelming the database
                time.sleep(1)
    
    def process_subtitle_free_videos(self):
        """Process videos that don't have subtitles."""
        print("\n자막 없는 영상 처리 중...")
        
        try:
            # Query for videos with has_subtitle=false
            url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
            params = {
                "has_subtitle": "eq.false",
                "select": "video_id,title,channel_name"
            }
            
            response = requests.get(url, headers=HEADERS, params=params)
            
            if response.status_code == 200:
                videos = response.json()
                print(f"발견된 자막 없는 영상: {len(videos)}개")
                
                for video in videos:
                    video_id = video['video_id']
                    title = video.get('title', 'Unknown')
                    channel = video.get('channel_name', 'Unknown')
                    print(f"  처리 중: {video_id} ({channel})")
                    
                    # Update with standard message
                    summary = "이 영상은 요약이 제공되지 않습니다"
                    if self.update_video_summary(video_id, summary):
                        print(f"    [SUCCESS] {video_id} 업데이트 완료")
                        self.success_count += 1
                    else:
                        print(f"    [FAILED] {video_id} 업데이트 실패")
                        self.failed_count += 1
                    
                    time.sleep(1)  # Rate limiting
            else:
                print(f"자막 없는 영상 조회 실패: {response.status_code}")
                
        except Exception as e:
            print(f"자막 없는 영상 처리 중 오류: {e}")
    
    def query_current_database_status(self):
        """Check current database status."""
        try:
            url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
            params = {
                "select": "video_id,channel_name,has_subtitle,video_summary,subtitle_text",
                "video_summary": "is.null"
            }
            
            response = requests.get(url, headers=HEADERS, params=params)
            
            if response.status_code == 200:
                videos = response.json()
                print(f"\n현재 데이터베이스 상태:")
                print(f"video_summary가 NULL인 영상: {len(videos)}개")
                
                by_channel = {}
                for video in videos:
                    channel = video.get('channel_name', 'Unknown')
                    if channel not in by_channel:
                        by_channel[channel] = []
                    by_channel[channel].append({
                        'video_id': video['video_id'],
                        'has_subtitle': video.get('has_subtitle', False),
                        'subtitle_text': video.get('subtitle_text', None)
                    })
                
                for channel, vids in by_channel.items():
                    print(f"  {channel}: {len(vids)}개")
                    has_sub = len([v for v in vids if v['has_subtitle']])
                    no_sub = len([v for v in vids if not v['has_subtitle']])
                    print(f"    - has_subtitle=true: {has_sub}개")
                    print(f"    - has_subtitle=false: {no_sub}개")
                
                return videos
            else:
                print(f"데이터베이스 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"데이터베이스 조회 중 오류: {e}")
            return []
    
    def run(self):
        """Run the processing with current limitations."""
        print("="*60)
        print("YouTube 자막 추출 및 요약 생성 스크립트")
        print("="*60)
        
        # Check database status first
        videos = self.query_current_database_status()
        
        start_time = time.time()
        
        # Process videos with current IP blocking situation
        self.process_videos_with_ip_block_issue()
        
        # Process subtitle-free videos
        self.process_subtitle_free_videos()
        
        # Report results
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n" + "="*60)
        print("처리 완료")
        print("="*60)
        print(f"총 처리된 영상: {self.processed_count}")
        print(f"성공: {self.success_count}")
        print(f"실패: {self.failed_count}")
        print(f"소요 시간: {duration:.2f}초 ({duration/60:.2f}분)")
        print("="*60)
        
        print(f"\n다음 단계:")
        print("1. VPN 또는 다른 IP 환경에서 실제 자막 추출 실행")
        print("2. 추출된 자막으로 더 정확한 요약 생성")
        print("3. 멤버십 콘텐츠는 접근 권한 필요")

if __name__ == "__main__":
    processor = SubtitleProcessor()
    processor.run()