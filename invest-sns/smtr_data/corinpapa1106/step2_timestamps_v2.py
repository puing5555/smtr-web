#!/usr/bin/env python3
"""
Step2 v2: 타임스탬프 매칭 개선
- 자막을 슬라이딩 윈도우로 묶어서 매칭 (문맥 파악)
- 키워드 기반 매칭 (종목명, 가격, 매수/매도 등)
- TF-IDF 유사도 활용
- 매칭 실패 시 종목명 + 핵심 키워드로 폴백
"""
import json
import os
import re
import sys
import io
import glob
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def parse_timestamp(timestamp_str):
    try:
        timestamp_str = timestamp_str.strip('[]')
        parts = timestamp_str.split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = map(int, parts)
            return m * 60 + s
        return None
    except:
        return None

def load_subtitle_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^\[\n]+)'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        subtitles = []
        for ts_str, text in matches:
            ts_sec = parse_timestamp(ts_str)
            if ts_sec is not None:
                clean = re.sub(r'\s+', ' ', text.strip())
                if clean:
                    subtitles.append({
                        'timestamp': f"[{ts_str}]",
                        'timestamp_seconds': ts_sec,
                        'text': clean
                    })
        return subtitles
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def clean_text(text):
    """텍스트 정규화"""
    text = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
    return re.sub(r'\s+', ' ', text).strip()

def extract_keywords(text):
    """시그널에서 핵심 키워드 추출"""
    # 종목명, 숫자(가격), 매수/매도 관련 용어
    keywords = set()
    
    # 한글 명사 (2글자 이상)
    korean = re.findall(r'[가-힣]{2,}', text)
    keywords.update(korean)
    
    # 영문 단어
    english = re.findall(r'[a-zA-Z]{2,}', text)
    keywords.update([w.lower() for w in english])
    
    # 숫자+단위 (가격 등)
    numbers = re.findall(r'\d+(?:\.\d+)?(?:만|억|원|달러|%|배)?', text)
    keywords.update(numbers)
    
    return keywords

def build_windows(subtitles, window_size=5, stride=2):
    """자막을 슬라이딩 윈도우로 묶기"""
    windows = []
    for i in range(0, len(subtitles), stride):
        window = subtitles[i:i + window_size]
        if not window:
            continue
        combined_text = ' '.join(s['text'] for s in window)
        # 윈도우의 시작 타임스탬프 사용
        windows.append({
            'timestamp': window[0]['timestamp'],
            'timestamp_seconds': window[0]['timestamp_seconds'],
            'text': combined_text,
            'start_idx': i,
            'end_idx': min(i + window_size, len(subtitles))
        })
    return windows

def keyword_overlap_score(keywords, text):
    """키워드가 텍스트에 얼마나 포함되는지"""
    if not keywords:
        return 0
    clean = clean_text(text)
    matched = sum(1 for kw in keywords if kw.lower() in clean)
    return matched / len(keywords)

def find_best_match_v2(signal, subtitles, asset_name=None):
    """개선된 매칭: 윈도우 + 키워드 + 시퀀스 매칭 복합"""
    content = signal.get('content', '')
    context = signal.get('context', '')
    
    if not content or not subtitles:
        return None, 0
    
    # 1. 키워드 추출
    search_text = f"{content} {context}"
    keywords = extract_keywords(search_text)
    if asset_name:
        keywords.add(asset_name.lower())
        # 종목명 변형 추가
        for part in asset_name.split():
            if len(part) >= 2:
                keywords.add(part.lower())
    
    # 2. 윈도우 빌드 (다양한 크기)
    all_candidates = []
    
    # 개별 자막 라인
    for sub in subtitles:
        all_candidates.append(sub)
    
    # 3줄 윈도우
    for win in build_windows(subtitles, window_size=3, stride=1):
        all_candidates.append(win)
    
    # 5줄 윈도우
    for win in build_windows(subtitles, window_size=5, stride=2):
        all_candidates.append(win)
    
    # 10줄 윈도우 (넓은 맥락)
    for win in build_windows(subtitles, window_size=10, stride=5):
        all_candidates.append(win)
    
    # 3. 각 후보에 대해 복합 점수 계산
    clean_content = clean_text(content)
    clean_context = clean_text(context)
    
    best_match = None
    best_score = 0
    
    for candidate in all_candidates:
        clean_cand = clean_text(candidate['text'])
        
        # (a) SequenceMatcher 유사도
        seq_score = SequenceMatcher(None, clean_content, clean_cand).ratio()
        
        # (b) 키워드 오버랩
        kw_score = keyword_overlap_score(keywords, candidate['text'])
        
        # (c) 종목명 매칭 보너스
        asset_bonus = 0
        if asset_name and asset_name.lower() in clean_cand:
            asset_bonus = 0.2
        
        # (d) 부분 문자열 매칭
        substring_bonus = 0
        if clean_content[:20] in clean_cand or clean_cand[:30] in clean_content:
            substring_bonus = 0.15
        
        # (e) context 매칭
        context_score = 0
        if clean_context:
            context_score = SequenceMatcher(None, clean_context, clean_cand).ratio() * 0.3
        
        # 복합 점수
        total_score = (seq_score * 0.3) + (kw_score * 0.35) + asset_bonus + substring_bonus + context_score
        
        if total_score > best_score:
            best_score = total_score
            best_match = candidate
    
    return best_match, best_score

def add_timestamps_to_signals(signals):
    # 자막 로드
    subtitle_dirs = [
        "C:\\Users\\Mario\\work\\invest-sns\\smtr_data\\corinpapa1106",
        "C:\\Users\\Mario\\.openclaw\\workspace\\smtr_data\\corinpapa1106"
    ]
    
    subtitle_cache = {}
    for d in subtitle_dirs:
        if os.path.exists(d):
            for txt_file in glob.glob(os.path.join(d, "*.txt")):
                vid = os.path.splitext(os.path.basename(txt_file))[0]
                if vid not in subtitle_cache:
                    subs = load_subtitle_file(txt_file)
                    if subs:
                        subtitle_cache[vid] = subs
    
    print(f"자막 파일 로드: {len(subtitle_cache)}개")
    
    matched = 0
    improved = 0
    
    for signal in signals:
        vid = signal.get('video_id')
        asset = signal.get('asset', '')
        old_ts = signal.get('timestamp_seconds')
        
        if vid not in subtitle_cache:
            signal.setdefault('timestamp', None)
            signal.setdefault('timestamp_seconds', None)
            signal.setdefault('timestamp_similarity', 0)
            continue
        
        best, score = find_best_match_v2(signal, subtitle_cache[vid], asset_name=asset)
        
        if best and score >= 0.2:
            signal['timestamp'] = best['timestamp']
            signal['timestamp_seconds'] = best['timestamp_seconds']
            signal['timestamp_similarity'] = round(score, 3)
            signal['matched_subtitle'] = best['text'][:200]
            matched += 1
            
            if not old_ts or old_ts == 0:
                improved += 1
                print(f"  ✅ NEW {vid} | {asset} | {best['timestamp']} (score={score:.2f})")
            elif old_ts != best['timestamp_seconds']:
                print(f"  🔄 UPD {vid} | {asset} | {old_ts}s → {best['timestamp_seconds']}s (score={score:.2f})")
        else:
            signal['timestamp'] = None
            signal['timestamp_seconds'] = None
            signal['timestamp_similarity'] = 0
            signal['matched_subtitle'] = ''
            print(f"  ❌ MISS {vid} | {asset} | score={score:.2f}")
    
    return matched, improved

def main():
    # 기존 데이터 로드 (이미 Claude 검증까지 된 데이터)
    input_path = "_claude_partial_164.json"
    output_path = "_claude_partial_164.json"  # 덮어쓰기
    backup_path = "_claude_partial_164_backup.json"
    
    print("=== Step2 v2: 타임스탬프 매칭 개선 ===")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    # 백업
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    print(f"백업 저장: {backup_path}")
    
    # 기존 매칭 통계
    old_matched = sum(1 for s in signals if s.get('timestamp_seconds') and s['timestamp_seconds'] > 0)
    print(f"기존 타임스탬프 있음: {old_matched}/{len(signals)}")
    
    # 개선된 매칭 실행
    matched, improved = add_timestamps_to_signals(signals)
    
    # 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    
    new_matched = sum(1 for s in signals if s.get('timestamp_seconds') and s['timestamp_seconds'] > 0)
    
    print(f"\n=== 결과 ===")
    print(f"전체 시그널: {len(signals)}")
    print(f"기존 매칭: {old_matched} ({old_matched*100//len(signals)}%)")
    print(f"개선 후 매칭: {new_matched} ({new_matched*100//len(signals)}%)")
    print(f"새로 찾은 타임스탬프: {improved}개")
    print(f"저장: {output_path}")

if __name__ == "__main__":
    main()
