import requests, json

instances = [
    'https://inv.tux.pizza',
    'https://invidious.fdn.fr',
    'https://vid.puffyan.us',
    'https://invidious.nerdvpn.de',
    'https://y.com.sb',
    'https://iv.datura.network',
    'https://invidious.privacyredirect.com',
]
vid = 'fDZnPoK5lyc'

for inst in instances:
    try:
        url = f'{inst}/api/v1/captions/{vid}'
        r = requests.get(url, timeout=10)
        print(f'{inst}: {r.status_code}')
        if r.status_code == 200:
            caps = json.loads(r.text)
            captions = caps.get('captions', [])
            print(f'  Captions: {len(captions)}')
            for c in captions:
                print(f'  - {c.get("languageCode")} ({c.get("label")})')
            # Try to fetch Korean caption
            ko = next((c for c in captions if c.get('languageCode') == 'ko'), None)
            if ko:
                sub_url = f'{inst}{ko["url"]}'
                sr = requests.get(sub_url, timeout=10)
                print(f'  Subtitle fetch: {sr.status_code}, len={len(sr.text)}')
                if sr.status_code == 200:
                    print(f'  First 200 chars: {sr.text[:200]}')
                    print(f'\nSUCCESS! Instance: {inst}')
                    break
    except Exception as e:
        print(f'{inst}: ERROR {str(e)[:80]}')
