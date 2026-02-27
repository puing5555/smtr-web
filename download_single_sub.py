import subprocess
import sys
import time
import os

def download_subtitle(video_id, max_retries=3, base_delay=60):
    output_dir = "C:/Users/Mario/work/subs"
    os.makedirs(output_dir, exist_ok=True)
    
    srt_path = f"{output_dir}/{video_id}.ko.srt"
    if os.path.exists(srt_path):
        print(f"Subtitles already exist for {video_id}")
        return True
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries} for video {video_id}")
        
        if attempt > 0:
            delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
            print(f"Waiting {delay} seconds before retry...")
            time.sleep(delay)
        
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--write-auto-sub',
            '--sub-lang', 'ko',
            '--skip-download',
            '--convert-subs', 'srt',
            '-o', f'{output_dir}/%(id)s',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"Successfully downloaded subtitles for {video_id}")
                return True
            else:
                print(f"Error downloading {video_id}: {result.stderr}")
                if "429" in result.stderr:  # Rate limited
                    print("Rate limited, will retry with longer delay...")
                    continue
                else:
                    print("Non-rate-limit error, skipping retries")
                    break
        except Exception as e:
            print(f"Exception downloading {video_id}: {e}")
    
    print(f"Failed to download subtitles for {video_id} after {max_retries} attempts")
    return False

# Try downloading the first video
if __name__ == "__main__":
    result = download_subtitle("hxpOT8n_ICw", max_retries=3, base_delay=120)
    print(f"Download result: {result}")