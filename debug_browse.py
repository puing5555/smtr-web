import urllib.request, json

url = 'https://www.youtube.com/youtubei/v1/browse'
payload = json.dumps({
    'browseId': 'UCe16dTsC0TJ06lASL3Bld4A',
    'params': 'EgZ2aWRlb3PyBgQKAjoA',
    'context': {'client': {'clientName': 'WEB', 'clientVersion': '2.20240101.00.00', 'hl': 'ko', 'gl': 'KR'}}
}).encode()
req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())

tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
for i, tab in enumerate(tabs):
    tr = tab.get('tabRenderer', {})
    title = tr.get('title', 'N/A')
    selected = tr.get('selected', False)
    content = tr.get('content', {})
    print(f"Tab {i}: {title} (selected={selected}), content keys={list(content.keys())[:5]}")
    rgr = content.get('richGridRenderer', {})
    if rgr:
        items = rgr.get('contents', [])
        print(f"  richGridRenderer: {len(items)} items")
        if items:
            for j, item in enumerate(items[:2]):
                print(f"  Item {j} keys: {list(item.keys())}")
                rir = item.get('richItemRenderer', {})
                if rir:
                    c = rir.get('content', {})
                    print(f"    content keys: {list(c.keys())}")
                    vr = c.get('videoRenderer', {})
                    if vr:
                        print(f"    videoId: {vr.get('videoId')}, title: {vr.get('title', {}).get('runs', [{}])[0].get('text', '')[:50]}")
    slr = content.get('sectionListRenderer', {})
    if slr:
        sections = slr.get('contents', [])
        print(f"  sectionListRenderer: {len(sections)} sections")
