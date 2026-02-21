#!/usr/bin/env python3
"""자막 없는 영상에서 자막 다운로드"""
import json, os, glob, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def get_missing_video_ids():
    with open('_claude_partial_164.json', 'r', encoding='utf-8') as f:
        signals = json.load(f)
    
    existing = set()
    for f in glob.glob('*.txt'):
        existing.add(os.path.splitext(f)[0])
    
    missing = set()
    for s in signals:
        vid = s.get('video_id')
        if vid and vid not in existing:
            missing.add(vid)
    
    return list(missing)

def download_subtitle(video_id):
    """yt-dlp로 자막 다운로드"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    output = f"{video_id}.txt"
    
    try:
        # 한국어 자막 우선, 없으면 자동생성 자막
        result = subprocess.run([
            sys.executable, '-m', 'yt_dlp',
            '--skip-download',
            '--write-sub', '--write-auto-sub',
            '--sub-lang', 'ko,en',
            '--sub-format', 'vtt',
            '--convert-subs', 'vtt',
            '-o', video_id,
            url
        ], capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace')
        
        # vtt 파일을 우리 포맷으로 변환
        vtt_files = glob.glob(f"{video_id}*.vtt")
        if not vtt_files:
            print(f"  No subtitle found for {video_id}")
            return False
        
        # 가장 적합한 파일 선택 (ko 우선)
        vtt_file = vtt_files[0]
        for f in vtt_files:
            if '.ko.' in f:
                vtt_file = f
                break
        
        # VTT -> 우리 포맷 변환
        convert_vtt_to_txt(vtt_file, output)
        
        # vtt 파일 정리
        for f in vtt_files:
            try: os.remove(f)
            except: pass
        
        return True
    except subprocess.TimeoutExpired:
        print(f"  Timeout for {video_id}")
        return False
    except Exception as e:
        print(f"  Error for {video_id}: {e}")
        return False

def convert_vtt_to_txt(vtt_path, txt_path):
    """VTT 자막을 [MM:SS] 텍스트 포맷으로 변환"""
    import re
    
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = []
    seen_texts = set()
    
    # 블록 단위로 파싱
    blocks = content.split('\n\n')
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # 타임스탬프 라인 찾기
        ts_match = re.search(r'(\d{2}):(\d{2}):(\d{2})\.\d{3}\s*-->', block)
        if not ts_match:
            continue
        
        h, m, s = int(ts_match.group(1)), int(ts_match.group(2)), int(ts_match.group(3))
        
        # 타임스탬프 라인 이후 텍스트 추출
        block_lines = block.split('\n')
        text_lines = []
        past_ts = False
        for line in block_lines:
            if '-->' in line:
                past_ts = True
                continue
            if past_ts and line.strip():
                # align:start 등 속성이 있는 라인은 건너뛰지 않음
                text_lines.append(line.strip())
        
        if not text_lines:
            continue
        
        # 텍스트 합치고 태그 제거
        text = ' '.join(text_lines)
        text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)
        
        minutes = m + h * 60
        lines.append(f"[{minutes}:{s:02d}] {text}")
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"  Converted: {len(lines)} lines -> {txt_path}")

def main():
    missing = get_missing_video_ids()
    print(f"=== 자막 다운로드: {len(missing)}개 영상 ===")
    
    success = 0
    for i, vid in enumerate(missing):
        print(f"[{i+1}/{len(missing)}] {vid}")
        if download_subtitle(vid):
            success += 1
    
    print(f"\n=== 완료: {success}/{len(missing)} 다운로드 성공 ===")

if __name__ == "__main__":
    main()
