import json

opus = json.load(open('_opus_inline.json', 'r', encoding='utf-8'))
opus_js = json.dumps(opus, ensure_ascii=False)

with open('signal-review-v3.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = "var OPUS_API_URL = '';"
new_code = f"""var OPUS_API_URL = '';
        var PRELOADED_OPUS = {opus_js};
        // Auto-load preloaded opus results
        (function(){{ var ex = loadOpusResults(); var pre = PRELOADED_OPUS; for(var k in pre){{ if(!ex[k]) ex[k] = pre[k]; }} saveOpusResults(ex); }})();"""

html = html.replace(old, new_code)

with open('signal-review-v3.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done! Opus results injected.")
