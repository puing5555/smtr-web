# subtitle_extractor.py - 자막 추출 모듈
import os
import time
import json
import requests
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import yt_dlp
from pipeline_config import PipelineConfig

class SubtitleExtractor:
    def __init__(self):
        self.config = PipelineConfig()
        self.proxy_config = self.config.get_proxy_config()
        self.formatter = TextFormatter()  # fallback용만 유지

    def format_with_timestamps(self, transcript_data: list) -> str:
        """
        자막 데이터를 타임스탬프 포함 형태로 변환
        형식: [MM:SS] 텍스트
        Claude가 정확한 종목 언급 시점을 파악할 수 있도록 타임스탬프 보존
        """
        lines = []
        for entry in transcript_data:
            seconds = int(entry.get('start', 0))
            minutes = seconds // 60
            secs = seconds % 60
            timestamp = f"{minutes}:{secs:02d}"
            text = entry.get('text', '').strip()
            # 줄바꿈 정리
            text = text.replace('\n', ' ').strip()
            if text:
                lines.append(f"[{timestamp}] {text}")
        return '\n'.join(lines)
        
        # yt-dlp 설정
        self.ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ko', 'kr', 'ko-KR'],
            'skip_download': True,
            'quiet': True
        }
        
        if self.proxy_config:
            self.ydl_opts['proxy'] = self.proxy_config['https']
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """유튜브 URL에서 비디오 ID 추출"""
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_with_youtube_transcript_api(self, video_id: str) -> Optional[str]:
        """youtube_transcript_api로 자막 추출"""
        try:
            # 프록시 설정
            if self.proxy_config:
                # youtube_transcript_api는 requests를 사용하므로 환경변수로 프록시 설정
                os.environ['HTTP_PROXY'] = self.proxy_config['http']
                os.environ['HTTPS_PROXY'] = self.proxy_config['https']
            
            # 한국어 자막 시도
            languages = ['ko', 'kr', 'ko-KR', 'ko-US']
            
            for lang in languages:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # 수동 자막 우선
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        subtitle_data = transcript.fetch()
                        subtitle_text = self.format_with_timestamps(subtitle_data)
                        print(f"[OK] 수동 자막 추출 성공 ({lang}): {len(subtitle_text)} 글자 (타임스탬프 포함)")
                        return subtitle_text
                    except:
                        pass
                    
                    # 자동 자막 시도
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        subtitle_data = transcript.fetch()
                        subtitle_text = self.format_with_timestamps(subtitle_data)
                        print(f"[OK] 자동 자막 추출 성공 ({lang}): {len(subtitle_text)} 글자 (타임스탬프 포함)")
                        return subtitle_text
                    except:
                        pass
                        
                except Exception as e:
                    continue
                    
            print(f"[ERROR] 한국어 자막 없음 (video_id: {video_id})")
            return None
            
        except Exception as e:
            print(f"[ERROR] youtube_transcript_api 에러: {e}")
            return None
        finally:
            # 프록시 환경변수 정리
            if 'HTTP_PROXY' in os.environ:
                del os.environ['HTTP_PROXY']
            if 'HTTPS_PROXY' in os.environ:
                del os.environ['HTTPS_PROXY']
    
    def extract_with_yt_dlp(self, url: str) -> Optional[str]:
        """yt-dlp로 자막 추출"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 정보 추출
                info = ydl.extract_info(url, download=False)
                
                # 자막 파일 다운로드 시도
                ydl.download([url])
                
                # 자막 파일 찾기
                video_id = info.get('id')
                subtitle_files = [
                    f"{video_id}.ko.vtt",
                    f"{video_id}.kr.vtt", 
                    f"{video_id}.ko-KR.vtt",
                    f"{video_id}.live_chat.json"
                ]
                
                for subtitle_file in subtitle_files:
                    if os.path.exists(subtitle_file):
                        try:
                            with open(subtitle_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # VTT 파일 파싱
                            if subtitle_file.endswith('.vtt'):
                                subtitle_text = self.parse_vtt_content(content)
                                print(f"[OK] yt-dlp 자막 추출 성공: {len(subtitle_text)} 글자")
                                
                                # 임시 파일 정리
                                os.remove(subtitle_file)
                                return subtitle_text
                        except Exception as e:
                            print(f"자막 파일 읽기 에러: {e}")
                            continue
                        finally:
                            # 임시 파일 정리
                            if os.path.exists(subtitle_file):
                                os.remove(subtitle_file)
                
                print(f"[ERROR] yt-dlp 자막 파일 없음")
                return None
                
        except Exception as e:
            print(f"[ERROR] yt-dlp 에러: {e}")
            return None
    
    def parse_vtt_content(self, content: str) -> str:
        """
        VTT 파일 내용을 타임스탬프 포함 텍스트로 파싱
        형식: [MM:SS] 텍스트
        """
        import re
        
        lines = content.split('\n')
        result = []
        current_timestamp = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            if '-->' in line:
                # 이전 블록 저장
                if current_text and current_timestamp:
                    text = ' '.join(current_text)
                    clean_text = re.sub(r'<[^>]+>', '', text).strip()
                    if clean_text:
                        result.append(f"[{current_timestamp}] {clean_text}")
                current_text = []
                
                # 시작 시간 파싱: "00:15:30.000 --> 00:15:32.000"
                start_raw = line.split('-->')[0].strip()
                parts = start_raw.split(':')
                try:
                    if len(parts) == 3:
                        # HH:MM:SS.mmm
                        total_minutes = int(parts[0]) * 60 + int(parts[1])
                        secs = int(float(parts[2]))
                        current_timestamp = f"{total_minutes}:{secs:02d}"
                    elif len(parts) == 2:
                        # MM:SS.mmm
                        current_timestamp = f"{int(parts[0])}:{int(float(parts[1])):02d}"
                except:
                    current_timestamp = "0:00"
                    
            elif (line and 
                  not line.startswith('WEBVTT') and 
                  not line.startswith('NOTE') and
                  not line.isdigit()):
                # HTML 태그 제거
                clean = re.sub(r'<[^>]+>', '', line).strip()
                if clean:
                    current_text.append(clean)
        
        # 마지막 블록 저장
        if current_text and current_timestamp:
            text = ' '.join(current_text)
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if clean_text:
                result.append(f"[{current_timestamp}] {clean_text}")
        
        return '\n'.join(result)
    
    def extract_subtitle(self, url: str, retries: int = 3) -> Optional[str]:
        """
        자막 추출 (여러 방법 시도)
        
        Args:
            url: 유튜브 영상 URL
            retries: 재시도 횟수
        
        Returns:
            자막 텍스트 또는 None
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            print(f"[ERROR] 유효하지 않은 유튜브 URL: {url}")
            return None
        
        print(f"자막 추출 시작: {video_id}")
        
        for attempt in range(retries):
            try:
                # 방법 1: youtube_transcript_api 시도
                subtitle = self.extract_with_youtube_transcript_api(video_id)
                if subtitle:
                    return subtitle
                
                print(f"youtube_transcript_api 실패, yt-dlp 시도...")
                
                # 방법 2: yt-dlp 시도
                subtitle = self.extract_with_yt_dlp(url)
                if subtitle:
                    return subtitle
                
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"재시도 {attempt + 1}/{retries} ({wait_time}초 후)...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"자막 추출 에러 (시도 {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(5)
        
        print(f"[ERROR] 자막 추출 완전 실패: {video_id}")
        return None
    
    def extract_with_rate_limit(self, videos: list) -> list:
        """
        레이트리밋을 고려한 일괄 자막 추출
        
        Args:
            videos: 영상 정보 리스트
        
        Returns:
            자막이 추가된 영상 정보 리스트
        """
        results = []
        batch_count = 0
        
        for i, video in enumerate(videos):
            print(f"\n진행: {i+1}/{len(videos)} - {video['title'][:50]}...")
            
            # 자막 추출
            subtitle = self.extract_subtitle(video['url'])
            
            video_result = video.copy()
            video_result['subtitle'] = subtitle
            video_result['subtitle_success'] = subtitle is not None
            
            results.append(video_result)
            
            # 성공한 경우만 배치 카운트
            if subtitle:
                batch_count += 1
            
            # 레이트리밋 적용
            if i < len(videos) - 1:  # 마지막이 아닐 때만
                # 일반 요청 간격
                print(f"대기 중... ({self.config.RATE_LIMIT_REQUESTS}초)")
                time.sleep(self.config.RATE_LIMIT_REQUESTS)
                
                # 배치 휴식 (20개마다 5분)
                if batch_count > 0 and batch_count % self.config.RATE_LIMIT_BATCH_SIZE == 0:
                    print(f"배치 휴식: {self.config.RATE_LIMIT_BATCH_BREAK // 60}분...")
                    time.sleep(self.config.RATE_LIMIT_BATCH_BREAK)
        
        # 결과 요약
        success_count = sum(1 for r in results if r['subtitle_success'])
        print(f"\n=== 자막 추출 완료 ===")
        print(f"성공: {success_count}/{len(videos)}개")
        print(f"실패: {len(videos) - success_count}개")
        
        return results