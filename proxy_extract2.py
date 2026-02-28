import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi

VIDEOS = {
    "nm5zQxZSkbk": "syuka",
    "XveVkr3JHs4": "syuka",
    "N7xO-UWCM5w": "syuka",
    "B5owNUs_DFw": "hyoseok",
    "bmXgryWXNrw": "hyoseok",
    "5mvn3PfKf9Y": "dalant",
}

SUBS_DIR = r"C:\Users\Mario\work\subs"
os.makedirs(SUBS_DIR, exist_ok=True)

class TimeoutSession(requests.Session):
    def __init__(self, timeout=10, **kwargs):
        super().__init__(**kwargs)
        self._timeout = timeout
    def request(self, *args, **kwargs):
        kwargs.setdefault('timeout', self._timeout)
        return super().request(*args, **kwargs)

# Get free proxies
print("Fetching proxy list...")
resp = requests.get(
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=protocolipport&format=text&timeout=3000",
    timeout=10
)
proxies = [p.strip() for p in resp.text.strip().split('\n') if p.strip()]
print(f"Got {len(proxies)} proxies")

# Also try socks proxies
try:
    resp2 = requests.get(
        "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=socks5&proxy_format=protocolipport&format=text&timeout=3000",
        timeout=10
    )
    socks = [p.strip() for p in resp2.text.strip().split('\n') if p.strip()]
    print(f"Got {len(socks)} SOCKS5 proxies")
    proxies.extend(socks)
except:
    pass

print(f"Total: {len(proxies)} proxies to try")

success = {}
failed = []
working_proxy = None

for vid, prefix in VIDEOS.items():
    out_file = os.path.join(SUBS_DIR, f"{prefix}_{vid}.json")
    if os.path.exists(out_file):
        print(f"[SKIP] {vid} already exists")
        success[vid] = out_file
        continue
    
    print(f"\n[{vid}] Trying proxies...")
    extracted = False
    
    # Try working proxy first
    proxy_list = proxies
    if working_proxy:
        proxy_list = [working_proxy] + [p for p in proxies if p != working_proxy]
    
    for i, proxy_url in enumerate(proxy_list[:100]):
        proxy_url = proxy_url.strip()
        if not proxy_url:
            continue
        try:
            session = TimeoutSession(timeout=10)
            session.proxies = {"http": proxy_url, "https": proxy_url}
            
            ytt = YouTubeTranscriptApi(http_client=session)
            result = ytt.fetch(vid, languages=['ko', 'en'])
            snippets = [{"text": s.text, "start": s.start, "duration": s.duration} for s in result.snippets]
            
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump({"video_id": vid, "subtitles": snippets}, f, ensure_ascii=False, indent=2)
            
            print(f"  OK! Proxy #{i}: {proxy_url} ({len(snippets)} snippets)")
            success[vid] = out_file
            working_proxy = proxy_url
            extracted = True
            break
        except KeyboardInterrupt:
            raise
        except Exception as e:
            err = str(e)[:100].replace('\n', ' ')
            if i < 3 or i % 15 == 0:
                print(f"  X #{i}: {err}")
            continue
    
    if not extracted:
        failed.append(vid)
        print(f"  FAILED all proxies for {vid}")

print(f"\n=== RESULTS ===")
print(f"Success: {len(success)}/{len(VIDEOS)}")
if failed:
    print(f"Failed: {len(failed)}")
    for vid in failed:
        print(f"  - {vid}")
else:
    print("ALL DONE!")
