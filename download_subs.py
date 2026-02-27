import subprocess
import sys
import time
import os

video_ids = [
    'hxpOT8n_ICw',
    'R6w3T3eUVIs', 
    'WWtau8xFUU4',
    'zdMneplXBvQ',
    '-US4r1E1kOQ',
    'lXxz7WJj76Y'
]

output_dir = "C:/Users/Mario/work/subs"
os.makedirs(output_dir, exist_ok=True)

for i, video_id in enumerate(video_ids):
    print(f"Downloading subtitles for video {i+1}/{len(video_ids)}: {video_id}")
    
    # Check if subtitle already exists
    srt_path = f"{output_dir}/{video_id}.ko.srt"
    if os.path.exists(srt_path):
        print(f"Subtitles already exist for {video_id}")
        continue
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--write-auto-sub',
        '--sub-lang', 'ko',
        '--skip-download',
        '--convert-subs', 'srt',
        '-o', f'{output_dir}/%(id)s',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '--sleep-interval', '10',
        '--max-sleep-interval', '15',
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully downloaded subtitles for {video_id}")
        else:
            print(f"Error downloading {video_id}: {result.stderr}")
    except Exception as e:
        print(f"Exception downloading {video_id}: {e}")
    
    # Wait between downloads to avoid rate limiting
    if i < len(video_ids) - 1:
        print("Waiting 30 seconds before next download...")
        time.sleep(30)

print("Subtitle download process completed.")