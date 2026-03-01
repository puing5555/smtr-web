"""Try using requests with different headers/approach"""
import sys, io, json, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

vid = '1NUkBQ9MQf8'

# First get the page to extract caption URL
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
})

# Try innertube API directly
url = 'https://www.youtube.com/youtubei/v1/get_transcript'
payload = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20240101.00.00",
            "hl": "ko",
            "gl": "KR"
        }
    },
    "params": None  # Need video transcript params
}

# Alternative: use innertube player API
player_url = 'https://www.youtube.com/youtubei/v1/player'
player_payload = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20240101.00.00",
            "hl": "ko"
        }
    },
    "videoId": vid
}

print("Trying innertube player API...")
resp = session.post(player_url, json=player_payload)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    captions = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    print(f"Caption tracks: {len(captions)}")
    
    if captions:
        ko_track = next((t for t in captions if t.get('languageCode') == 'ko'), captions[0])
        caption_url = ko_track['baseUrl'] + '&fmt=json3'
        print(f"Fetching caption URL...")
        
        resp2 = session.get(caption_url)
        print(f"Caption status: {resp2.status_code}, length: {len(resp2.text)}")
        if resp2.status_code == 200:
            print(f"First 200: {resp2.text[:200]}")
        else:
            print(f"Error: {resp2.text[:300]}")
else:
    print(f"Error: {resp.text[:300]}")
