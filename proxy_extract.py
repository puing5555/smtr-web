import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import os
import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig

# 미추출 7개
VIDEOS = {
    "ksA4IT452_4": "syuka",
    "nm5zQxZSkbk": "syuka",
    "XveVkr3JHs4": "syuka",
    "N7xO-UWCM5w": "syuka",
    "B5owNUs_DFw": "hyoseok",
    "bmXgryWXNrw": "hyoseok",
    "5mvn3PfKf9Y": "dalant",
}

SUBS_DIR = r"C:\Users\Mario\work\subs"
os.makedirs(SUBS_DIR, exist_ok=True)

# Get free proxies
print("Fetching proxy list...")
resp = requests.get(
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=protocolipport&format=text&timeout=5000",
    timeout=10
)
proxies = [p.strip() for p in resp.text.strip().split('\n') if p.strip()]
print(f"Got {len(proxies)} proxies")

success = {}
failed = []

for vid, prefix in VIDEOS.items():
    out_file = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")
    if os.path.exists(out_file):
        print(f"[SKIP] {vid} already exists")
        success[vid] = out_file
        continue
    
    print(f"\n[{vid}] Trying proxies...")
    extracted = False
    
    for i, proxy_url in enumerate(proxies[:50]):  # Try up to 50 proxies
        proxy_url = proxy_url.strip()
        if not proxy_url:
            continue
        try:
            # GenericProxyConfig expects https and http
            ytt = YouTubeTranscriptApi(
                proxy_config=GenericProxyConfig(
                    http_url=proxy_url,
                    https_url=proxy_url,
                )
            )
            result = ytt.fetch(vid, languages=['ko', 'en'])
            snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in result.snippets]
            
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump({"video_id": vid, "subtitles": snippets}, f, ensure_ascii=False, indent=2)
            
            print(f"  OK! Proxy #{i}: {proxy_url} ({len(snippets)} snippets)")
            success[vid] = out_file
            extracted = True
            break
        except Exception as e:
            err = str(e)[:80]
            if i < 3 or i % 10 == 0:
                print(f"  X Proxy #{i}: {err}")
            continue
    
    if not extracted:
        failed.append(vid)
        print(f"  FAILED all proxies for {vid}")

print(f"\n=== RESULTS ===")
print(f"Success: {len(success)}/{len(VIDEOS)}")
print(f"Failed: {len(failed)}")
for vid in failed:
    print(f"  - {vid}")
