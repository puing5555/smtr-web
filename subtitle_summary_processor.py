#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Subtitle Extraction and Summary Generation Script
Processes videos in the influencer_videos table to extract subtitles and generate summaries.
"""

import time
import json
import requests
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript, NoTranscriptFound
from typing import Optional, List, Dict

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
        self.failed_count = 0
        self.success_count = 0
    
    def extract_subtitle_text(self, video_id: str) -> Optional[str]:
        """Extract subtitle text from YouTube video."""
        try:
            print(f"Extracting subtitles for video ID: {video_id}")
            
            # Try to get Korean subtitles first, then auto-generated
            try:
                transcript_list = YouTubeTranscriptApi().list(video_id)
                
                # Try Korean subtitles first
                try:
                    transcript = transcript_list.find_transcript(['ko'])
                    print(f"  → Found Korean subtitles for {video_id}")
                except:
                    # Try auto-generated subtitles
                    try:
                        transcript = transcript_list.find_generated_transcript(['ko'])
                        print(f"  → Found auto-generated Korean subtitles for {video_id}")
                    except:
                        # Try any available transcript
                        transcript = transcript_list.find_transcript(['en'])
                        print(f"  → Found English subtitles for {video_id}")
                
                subtitle_data = transcript.fetch()
                
                # Convert to text
                subtitle_text = ' '.join([item['text'] for item in subtitle_data])
                print(f"  → Extracted {len(subtitle_text)} characters")
                
                return subtitle_text
                
            except NoTranscriptFound:
                print(f"  → No transcripts found for {video_id}")
                return None
                
        except CouldNotRetrieveTranscript as e:
            if "429" in str(e):
                print(f"  → Rate limit hit for {video_id}, waiting 60 seconds...")
                time.sleep(60)
                return self.extract_subtitle_text(video_id)  # Retry
            else:
                print(f"  → Error extracting subtitles for {video_id}: {e}")
                return None
        except Exception as e:
            print(f"  → Unexpected error for {video_id}: {e}")
            return None
    
    def generate_summary(self, subtitle_text: str, channel_name: str) -> str:
        """Generate summary from subtitle text."""
        if not subtitle_text or len(subtitle_text) < 100:
            return f"{channel_name}에서 제공하는 투자 관련 콘텐츠입니다."
        
        # Simple summary generation based on content analysis
        text_lower = subtitle_text.lower()
        
        # Look for stock names and investment terms
        stock_keywords = ['삼성전자', '애플', 'nvidia', '비트코인', '테슬라', 'sk하이닉스', 
                         '카카오', '네이버', 'lg에너지솔루션', '현대자동차', '포스코']
        investment_keywords = ['매수', '매도', '상승', '하락', '투자', '분석', '전망', '추천']
        
        mentioned_stocks = []
        for keyword in stock_keywords:
            if keyword in text_lower:
                mentioned_stocks.append(keyword)
        
        # Extract key themes
        if '매수' in text_lower or '추천' in text_lower:
            sentiment = '긍정적인 투자 전망을'
        elif '매도' in text_lower or '주의' in text_lower:
            sentiment = '신중한 투자 접근을'
        else:
            sentiment = '투자 분석을'
        
        # Generate summary
        if mentioned_stocks:
            stocks_mentioned = ', '.join(mentioned_stocks[:3])  # Limit to 3 stocks
            summary = f"{channel_name}에서 {stocks_mentioned} 등 종목에 대해 {sentiment} 제시했다. "
        else:
            summary = f"{channel_name}에서 시장 상황과 투자 전략에 대해 {sentiment} 제시했다. "
        
        # Add key points based on content length and keywords
        if len(subtitle_text) > 2000:
            if '기술적분석' in text_lower or '차트' in text_lower:
                summary += "기술적 분석을 통한 차트 해석과 매매 타이밍을 설명했다. "
            if '실적' in text_lower or '재무' in text_lower:
                summary += "기업 실적과 재무 상황을 바탕으로 한 투자 근거를 제시했다. "
        
        # Add conclusion
        summary += "향후 시장 동향과 투자 전략에 대한 인사이트를 제공한다."
        
        return summary
    
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
                print(f"  → Updated subtitle_text for {video_id}")
                return True
            else:
                print(f"  → Failed to update subtitle_text for {video_id}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  → Error updating subtitle_text for {video_id}: {e}")
            return False
    
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
                print(f"  → Updated video_summary for {video_id}")
                return True
            else:
                print(f"  → Failed to update video_summary for {video_id}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  → Error updating video_summary for {video_id}: {e}")
            return False
    
    def process_video(self, video_id: str, channel_name: str):
        """Process a single video: extract subtitles and generate summary."""
        print(f"\nProcessing video {self.processed_count + 1}: {video_id} ({channel_name})")
        
        # Extract subtitles
        subtitle_text = self.extract_subtitle_text(video_id)
        
        if subtitle_text:
            # Update subtitle_text in database
            if self.update_subtitle_text(video_id, subtitle_text):
                # Generate summary
                summary = self.generate_summary(subtitle_text, channel_name)
                print(f"  → Generated summary: {summary[:100]}...")
                
                # Update video_summary in database
                if self.update_video_summary(video_id, summary):
                    self.success_count += 1
                    print(f"  [SUCCESS] Successfully processed {video_id}")
                else:
                    self.failed_count += 1
                    print(f"  [FAILED] Failed to update summary for {video_id}")
            else:
                self.failed_count += 1
                print(f"  [FAILED] Failed to update subtitles for {video_id}")
        else:
            self.failed_count += 1
            print(f"  [FAILED] Failed to extract subtitles for {video_id}")
        
        self.processed_count += 1
        
        # Rate limiting
        print("  → Waiting 3 seconds before next request...")
        time.sleep(3)
        
        # Long pause after 20 videos
        if self.processed_count % 20 == 0:
            print("  → Processed 20 videos, taking 5-minute break...")
            time.sleep(300)  # 5 minutes
    
    def process_subtitle_free_videos(self):
        """Process videos that don't have subtitles."""
        print("\nProcessing subtitle-free videos (has_subtitle=false)...")
        
        try:
            # Query for videos with has_subtitle=false
            url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
            params = {
                "has_subtitle": "eq.false",
                "select": "video_id,title"
            }
            
            response = requests.get(url, headers=HEADERS, params=params)
            
            if response.status_code == 200:
                videos = response.json()
                print(f"Found {len(videos)} subtitle-free videos")
                
                for video in videos:
                    video_id = video['video_id']
                    title = video.get('title', 'Unknown')
                    print(f"  Processing subtitle-free video: {video_id} ({title})")
                    
                    # Update with standard message
                    summary = "이 영상은 요약이 제공되지 않습니다"
                    if self.update_video_summary(video_id, summary):
                        print(f"  [SUCCESS] Updated {video_id} with standard message")
                    else:
                        print(f"  [FAILED] Failed to update {video_id}")
            else:
                print(f"Failed to query subtitle-free videos: {response.status_code}")
                
        except Exception as e:
            print(f"Error processing subtitle-free videos: {e}")
    
    def run(self):
        """Run the complete subtitle and summary processing."""
        print("Starting YouTube Subtitle and Summary Processing...")
        print(f"Total videos to process: {sum(len(videos) for videos in VIDEO_IDS.values())}")
        
        start_time = time.time()
        
        # Process videos with subtitles
        for channel_name, video_ids in VIDEO_IDS.items():
            print(f"\n{'='*50}")
            print(f"Processing {channel_name} videos ({len(video_ids)} videos)")
            print(f"{'='*50}")
            
            for video_id in video_ids:
                self.process_video(video_id, channel_name)
        
        # Process subtitle-free videos
        self.process_subtitle_free_videos()
        
        # Report results
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{'='*50}")
        print("PROCESSING COMPLETE")
        print(f"{'='*50}")
        print(f"Total processed: {self.processed_count}")
        print(f"Successful: {self.success_count}")
        print(f"Failed: {self.failed_count}")
        print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"{'='*50}")

if __name__ == "__main__":
    processor = SubtitleProcessor()
    processor.run()