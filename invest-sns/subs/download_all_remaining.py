"""모든 대기 중인 영상 자막 다운로드"""
import subprocess, sys, os, time, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# 대기 중인 모든 영상 ID
VIDEO_IDS = [
    'bmXgryWXNrw',
    'BVRoApF0c8k', 
    'fDZnPoK5lyc',
    'N7xO-UWCM5w',
    'nm5zQxZSkbk',
    'tSXkj2Omz34',
    'Xv-wNA91EPE',
    'XveVkr3JHs4',
    'ZXuQCpuVCYc'
]

print(f"=== 대기 중인 {len(VIDEO_IDS)}개 영상 자막 다운로드 ===")

success_count = 0
failed_videos = []

for i, vid in enumerate(VIDEO_IDS, 1):
    print(f"\n--- {i}/{len(VIDEO_IDS)}: {vid} ---")
    
    # 이미 존재하는지 확인
    vtt_file = f"{SUBS_DIR}/{vid}.ko.vtt"
    if os.path.exists(vtt_file):
        print(f"  SKIP: 이미 존재함 ({os.path.getsize(vtt_file)} bytes)")
        success_count += 1
        continue
    
    try:
        cmd = [sys.executable, '-m', 'yt_dlp',
               '--write-auto-sub', '--sub-lang', 'ko', '--skip-download',
               '--sleep-interval', '10', '--max-sleep-interval', '20',
               '-o', f'{SUBS_DIR}/{vid}',
               f'https://www.youtube.com/watch?v={vid}']
        
        print(f"  시도중...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if os.path.exists(vtt_file) and os.path.getsize(vtt_file) > 1000:
            print(f"  SUCCESS! ({os.path.getsize(vtt_file)} bytes)")
            success_count += 1
        else:
            print(f"  FAILED: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            failed_videos.append(vid)
            
    except Exception as e:
        print(f"  ERROR: {e}")
        failed_videos.append(vid)
    
    # 간격 두기 (rate limiting 방지)
    if i < len(VIDEO_IDS):
        print("  잠시 대기중...")
        time.sleep(15)

print(f"\n=== 최종 결과 ===")
print(f"성공: {success_count}/{len(VIDEO_IDS)}")
print(f"실패: {len(failed_videos)}")
if failed_videos:
    print(f"실패 영상: {', '.join(failed_videos)}")