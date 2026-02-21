#!/usr/bin/env python3
import json
import os
import re
import glob
from difflib import SequenceMatcher

def parse_timestamp(timestamp_str):
    """타임스탬프 문자열을 초로 변환 ([0:05] -> 5, [1:23] -> 83)"""
    try:
        # Remove brackets if present
        timestamp_str = timestamp_str.strip('[]')
        parts = timestamp_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return None
    except:
        return None

def load_subtitle_file(filepath):
    """자막 파일을 로드하고 타임스탬프별로 파싱"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 타임스탬프와 텍스트를 추출 ([0:05] 형식)
        pattern = r'\[(\d{1,2}:\d{2})\]\s*([^\[\n]+)'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        subtitles = []
        for timestamp_str, text in matches:
            timestamp_seconds = parse_timestamp(timestamp_str)
            if timestamp_seconds is not None:
                # 텍스트 정리
                clean_text = re.sub(r'\s+', ' ', text.strip())
                if clean_text:
                    subtitles.append({
                        'timestamp': f"[{timestamp_str}]",
                        'timestamp_seconds': timestamp_seconds,
                        'text': clean_text
                    })
        
        return subtitles
    except Exception as e:
        print(f"Error loading subtitle file {filepath}: {e}")
        return []

def find_best_match(target_text, subtitles, min_similarity=0.3):
    """자막에서 가장 유사한 텍스트와 타임스탬프를 찾기"""
    if not target_text or not subtitles:
        return None, 0
    
    best_match = None
    best_score = 0
    
    # 타겟 텍스트를 정리
    clean_target = re.sub(r'[^\w\s가-힣]', ' ', target_text.lower())
    clean_target = re.sub(r'\s+', ' ', clean_target).strip()
    
    for subtitle in subtitles:
        # 자막 텍스트를 정리
        clean_subtitle = re.sub(r'[^\w\s가-힣]', ' ', subtitle['text'].lower())
        clean_subtitle = re.sub(r'\s+', ' ', clean_subtitle).strip()
        
        # 유사도 계산
        similarity = SequenceMatcher(None, clean_target, clean_subtitle).ratio()
        
        # 부분 문자열 매치도 확인
        if clean_target in clean_subtitle or clean_subtitle in clean_target:
            similarity = max(similarity, 0.8)
        
        if similarity > best_score and similarity >= min_similarity:
            best_score = similarity
            best_match = subtitle
    
    return best_match, best_score

def add_timestamps_to_signals(signals):
    """시그널에 타임스탬프 추가"""
    # 자막 파일 경로들
    subtitle_dirs = [
        "C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106",
        "C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106"
    ]
    
    # 자막 파일들을 로드
    subtitle_cache = {}
    
    for subtitle_dir in subtitle_dirs:
        if os.path.exists(subtitle_dir):
            for txt_file in glob.glob(os.path.join(subtitle_dir, "*.txt")):
                video_id = os.path.splitext(os.path.basename(txt_file))[0]
                if video_id not in subtitle_cache:
                    subtitles = load_subtitle_file(txt_file)
                    if subtitles:
                        subtitle_cache[video_id] = subtitles
                        print(f"Loaded {len(subtitles)} subtitles for {video_id}")
    
    print(f"Total subtitle files loaded: {len(subtitle_cache)}")
    
    # 각 시그널에 타임스탬프 매핑
    matched_count = 0
    
    for signal in signals:
        video_id = signal.get('video_id')
        content = signal.get('content', '')
        
        if video_id in subtitle_cache:
            best_match, similarity = find_best_match(content, subtitle_cache[video_id])
            
            if best_match:
                signal['timestamp'] = best_match['timestamp']
                signal['timestamp_seconds'] = best_match['timestamp_seconds']
                signal['timestamp_similarity'] = round(similarity, 3)
                signal['matched_subtitle'] = best_match['text']
                matched_count += 1
                print(f"+ Matched {video_id} (similarity: {similarity:.3f})")
            else:
                signal['timestamp'] = None
                signal['timestamp_seconds'] = None
                signal['timestamp_similarity'] = 0
                print(f"- No match for {video_id}")
        else:
            signal['timestamp'] = None
            signal['timestamp_seconds'] = None
            signal['timestamp_similarity'] = 0
            print(f"- No subtitle file for {video_id}")
    
    return matched_count

def main():
    input_path = "_deduped_signals.json"
    output_path = "_signals_with_timestamps.json"
    
    print(f"Loading deduped signals from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    print(f"Total signals: {len(signals)}")
    
    # 타임스탬프 매핑
    matched_count = add_timestamps_to_signals(signals)
    
    # 결과 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Timestamp Mapping Results ===")
    print(f"Total signals: {len(signals)}")
    print(f"Matched with timestamps: {matched_count}")
    print(f"Match rate: {matched_count/len(signals)*100:.1f}%")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()