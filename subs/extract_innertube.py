"""Try innertube with different clients"""
import sys, io, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

vid = '1NUkBQ9MQf8'
session = requests.Session()

clients = [
    {
        "name": "ANDROID",
        "client": {
            "clientName": "ANDROID",
            "clientVersion": "19.09.37",
            "androidSdkVersion": 30,
            "hl": "ko"
        }
    },
    {
        "name": "IOS", 
        "client": {
            "clientName": "IOS",
            "clientVersion": "19.09.3",
            "deviceMake": "Apple",
            "deviceModel": "iPhone14,3",
            "hl": "ko"
        }
    },
    {
        "name": "MWEB",
        "client": {
            "clientName": "MWEB",
            "clientVersion": "2.20240101.00.00",
            "hl": "ko"
        }
    },
    {
        "name": "TV_EMBEDDED",
        "client": {
            "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
            "clientVersion": "2.0",
            "hl": "ko"
        }
    },
]

player_url = 'https://www.youtube.com/youtubei/v1/player'

for c in clients:
    payload = {
        "context": {"client": c["client"]},
        "videoId": vid
    }
    
    headers = {'Content-Type': 'application/json'}
    if c["name"] == "ANDROID":
        headers['User-Agent'] = 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip'
    
    print(f"\n{c['name']}:")
    try:
        resp = session.post(player_url, json=payload, headers=headers, timeout=10)
        print(f"  Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            captions = data.get('captions', {})
            tracks = captions.get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
            print(f"  Caption tracks: {len(tracks)}")
            
            if tracks:
                for t in tracks:
                    print(f"    - {t.get('languageCode')}: {t.get('name', {}).get('simpleText', '?')}")
                
                ko = next((t for t in tracks if t.get('languageCode') == 'ko'), tracks[0])
                cap_url = ko['baseUrl'] + '&fmt=json3'
                
                resp2 = session.get(cap_url, headers=headers, timeout=10)
                print(f"  Caption fetch: {resp2.status_code}, len={len(resp2.text)}")
                if resp2.status_code == 200 and len(resp2.text) > 100:
                    try:
                        jdata = resp2.json()
                        events = jdata.get('events', [])
                        print(f"  Events: {len(events)}")
                        if events:
                            print("  SUCCESS!")
                            break
                    except:
                        print(f"  Not JSON: {resp2.text[:100]}")
                else:
                    print(f"  First 100: {resp2.text[:100]}")
        else:
            print(f"  Error: {resp.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")
