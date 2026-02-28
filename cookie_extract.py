import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import requests
from http.cookiejar import MozillaCookieJar

# Try browser_cookie3 to get YouTube cookies from Chrome
try:
    import browser_cookie3
    print("Getting cookies from Chrome...")
    cj = browser_cookie3.chrome(domain_name='.youtube.com')
    print(f"Got {len(list(cj))} cookies from Chrome")
except Exception as e:
    print(f"browser_cookie3 failed: {e}")
    print("Trying manual cookie file...")
    cj = None

from youtube_transcript_api import YouTubeTranscriptApi

VIDEOS = {
    "bmXgryWXNrw": "hyoseok",
    "5mvn3PfKf9Y": "dalant",
}

SUBS_DIR = r"C:\Users\Mario\work\subs"

if cj:
    session = requests.Session()
    session.cookies = cj
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    
    # Test cookie auth
    print("Testing with cookie auth...")
    for vid, prefix in VIDEOS.items():
        out_file = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")
        if os.path.exists(out_file):
            print(f"[SKIP] {vid}")
            continue
        try:
            ytt = YouTubeTranscriptApi(http_client=session)
            result = ytt.fetch(vid, languages=['ko', 'en'])
            snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in result.snippets]
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump({"video_id": vid, "subtitles": snippets}, f, ensure_ascii=False, indent=2)
            print(f"OK! {vid}: {len(snippets)} snippets")
        except Exception as e:
            print(f"FAIL {vid}: {str(e)[:150]}")
else:
    print("No cookies available. Need manual cookie export.")
    print("Run in Chrome console: document.cookie")
    print("Or use 'Get cookies.txt LOCALLY' Chrome extension")
