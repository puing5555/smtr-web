"""
타임스탬프 추출 개선 스크립트
- 기존 자막에서 시그널 인용문에 해당하는 정확한 타임스탬프 찾기
- 더 나은 매칭 알고리즘 사용
"""
import json
import os
import re
import sys
import io
from difflib import SequenceMatcher

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def load_subtitle_with_timestamps(video_id):
    """자막 파일에서 타임스탬프와 텍스트 쌍 추출"""
    subtitle_paths = [
        f'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\{video_id}.txt',
        f'C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106\\{video_id}.txt'
    ]
    
    for subtitle_path in subtitle_paths:
        if os.path.exists(subtitle_path):
            try:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # SRT/VTT 형식 파싱
                timestamp_entries = []
                
                # SRT 형식 (예: 00:02:45,123 --> 00:02:47,456)
                srt_pattern = r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n(.*?)(?=\n\d+\s*\n|\n\n|\Z)'
                srt_matches = re.findall(srt_pattern, content, re.DOTALL)
                
                for start_time, end_time, text in srt_matches:
                    start_seconds = parse_timestamp(start_time)
                    text_clean = re.sub(r'\n', ' ', text).strip()
                    if start_seconds and text_clean:
                        timestamp_entries.append((start_seconds, text_clean))
                
                # VTT 형식도 시도 (예: 00:02:45.123 --> 00:02:47.456)
                if not timestamp_entries:
                    vtt_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n(.*?)(?=\n\d{2}:\d{2}:\d{2}|\n\n|\Z)'
                    vtt_matches = re.findall(vtt_pattern, content, re.DOTALL)
                    
                    for start_time, end_time, text in vtt_matches:
                        start_seconds = parse_timestamp(start_time)
                        text_clean = re.sub(r'\n', ' ', text).strip()
                        if start_seconds and text_clean:
                            timestamp_entries.append((start_seconds, text_clean))
                
                # 간단한 타임스탬프 + 텍스트 형식 (예: 02:45 텍스트내용)
                if not timestamp_entries:
                    simple_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)'
                    lines = content.split('\n')
                    for line in lines:
                        match = re.match(simple_pattern, line.strip())
                        if match:
                            time_str, text = match.groups()
                            seconds = parse_simple_timestamp(time_str)
                            if seconds:
                                timestamp_entries.append((seconds, text.strip()))
                
                print(f"📄 자막 파싱: {subtitle_path} - {len(timestamp_entries)}개 엔트리")
                return timestamp_entries
                
            except Exception as e:
                print(f"⚠️ 자막 파싱 실패: {subtitle_path} - {e}")
                continue
    
    print(f"❌ 자막 파일 없음: {video_id}")
    return []

def parse_timestamp(timestamp_str):
    """타임스탬프 문자열을 초로 변환 (SRT/VTT 형식)"""
    try:
        # 쉼표를 점으로 변환 (SRT의 경우)
        timestamp_str = timestamp_str.replace(',', '.')
        
        # HH:MM:SS.mmm 형식 파싱
        parts = timestamp_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_parts = parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return total_seconds
    except:
        pass
    return None

def parse_simple_timestamp(timestamp_str):
    """간단한 타임스탬프를 초로 변환 (MM:SS 또는 HH:MM:SS)"""
    try:
        parts = timestamp_str.split(':')
        if len(parts) == 2:  # MM:SS
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
    except:
        pass
    return None

def similarity(text1, text2):
    """두 텍스트의 유사도 계산 (0-1)"""
    # 텍스트 정규화
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    if not text1 or not text2:
        return 0
    
    return SequenceMatcher(None, text1, text2).ratio()

def normalize_text(text):
    """텍스트 정규화 (공백, 구두점 등 제거)"""
    if not text:
        return ""
    
    # 따옴표, 구두점 제거
    text = re.sub(r'["""\'\'.,!?;:]', '', text)
    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def find_best_timestamp(quote_text, timestamp_entries, min_similarity=0.3):
    """인용문에 가장 잘 매칭되는 타임스탬프 찾기"""
    best_timestamp = None
    best_similarity = 0
    best_match_text = ""
    
    quote_normalized = normalize_text(quote_text)
    if not quote_normalized or len(quote_normalized) < 5:
        return None, 0, ""
    
    for timestamp, text in timestamp_entries:
        sim = similarity(quote_text, text)
        
        if sim > best_similarity and sim >= min_similarity:
            best_similarity = sim
            best_timestamp = timestamp
            best_match_text = text
    
    # 부분 매칭도 시도 (긴 인용문의 경우)
    if not best_timestamp and len(quote_normalized) > 20:
        # 인용문의 처음 10단어로 매칭
        quote_words = quote_normalized.split()[:10]
        quote_short = ' '.join(quote_words)
        
        for timestamp, text in timestamp_entries:
            text_normalized = normalize_text(text)
            if quote_short in text_normalized or text_normalized in quote_short:
                sim = len(quote_short) / max(len(quote_short), len(text_normalized))
                if sim > best_similarity:
                    best_similarity = sim
                    best_timestamp = timestamp
                    best_match_text = text
    
    return best_timestamp, best_similarity, best_match_text

def improve_all_timestamps():
    """모든 시그널의 타임스탬프 개선"""
    # 원본 시그널 로드
    signal_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_all_signals_194.json'
    with open(signal_file, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    print(f"🔄 타임스탬프 개선 시작: {len(signals)}개 시그널")
    
    improved_signals = []
    stats = {
        'total': len(signals),
        'improved': 0,
        'already_had': 0,
        'failed': 0
    }
    
    # 비디오별로 자막 캐싱
    subtitle_cache = {}
    
    for i, signal in enumerate(signals):
        video_id = signal.get('video_id', '')
        content = signal.get('content', '')
        
        print(f"📝 처리 중 ({i+1}/{len(signals)}): {video_id} - {signal.get('asset', 'N/A')}")
        
        # 자막 로드 (캐시 사용)
        if video_id not in subtitle_cache:
            subtitle_cache[video_id] = load_subtitle_with_timestamps(video_id)
        
        timestamp_entries = subtitle_cache[video_id]
        
        if not timestamp_entries:
            print(f"   ❌ 자막 없음")
            signal['timestamp_seconds'] = None
            signal['timestamp_confidence'] = 0
            signal['timestamp_match'] = ""
            stats['failed'] += 1
        else:
            # 타임스탬프 매칭
            timestamp, confidence, match_text = find_best_timestamp(content, timestamp_entries)
            
            if timestamp:
                signal['timestamp_seconds'] = timestamp
                signal['timestamp_confidence'] = confidence
                signal['timestamp_match'] = match_text
                
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                print(f"   ✅ 타임스탬프: {minutes:02d}:{seconds:02d} (신뢰도: {confidence:.2f})")
                stats['improved'] += 1
            else:
                signal['timestamp_seconds'] = None
                signal['timestamp_confidence'] = 0
                signal['timestamp_match'] = ""
                print(f"   ❌ 매칭 실패")
                stats['failed'] += 1
        
        improved_signals.append(signal)
    
    # 개선된 결과 저장
    output_file = 'C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106\\_signals_with_improved_timestamps.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(improved_signals, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 개선된 결과 저장: {output_file}")
    
    # 통계 출력
    print(f"\n📊 타임스탬프 개선 결과:")
    print(f"   - 전체: {stats['total']}개")
    print(f"   - 개선됨: {stats['improved']}개 ({stats['improved']/stats['total']*100:.1f}%)")
    print(f"   - 실패: {stats['failed']}개 ({stats['failed']/stats['total']*100:.1f}%)")
    
    return improved_signals, stats

if __name__ == "__main__":
    improve_all_timestamps()