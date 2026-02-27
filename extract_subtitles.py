import subprocess
import sys
import os

video_urls = [
    "https://www.youtube.com/watch?v=6R1HiMUAQkM",  # 심텍·기아·SK스퀘어·쿼드메디슨·한국전력
    "https://www.youtube.com/watch?v=RdAzQQJUvRU",  # 랠리는 아직 끝나지 않았다
    "https://www.youtube.com/watch?v=8-hYd-8eojE",  # 자금 흐름이 바뀌고 있다
    "https://www.youtube.com/watch?v=qYAiv0Kljas",  # 현대그룹주, 외국인이 쐈다
    "https://www.youtube.com/watch?v=XFHD_1M3Mxg",  # 외국인 관광객, 신세계 따라간다
    "https://www.youtube.com/watch?v=ldT75QwBB6g"   # 6천피 시대! 반도체 다음 주자는 화학?
]

for url in video_urls:
    print(f"Extracting subtitles for: {url}")
    result = subprocess.run([
        sys.executable, '-m', 'yt_dlp',
        '--write-auto-sub',
        '--sub-lang', 'ko',
        '--skip-download',
        '--convert-subs', 'srt',
        '-o', 'C:/Users/Mario/work/subs/%(id)s',
        url
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Success")
    else:
        print(f"Error: {result.stderr}")
    print("---")