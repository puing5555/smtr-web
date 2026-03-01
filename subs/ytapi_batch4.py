"""youtube-transcript-api로 9개 영상 자막 추출"""
import sys, io, json, os, time, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

SUBS_DIR = 'C:/Users/Mario/work/subs'

VIDEOS = [
    ('booread', '1NUkBQ9MQf8'),
    ('booread', 'IjDhjDgC4Ao'),
    ('booread', '1iuRuDfMLUE'),
    ('booread', 'f519DUfXkzQ'),
    ('booread', 'jXME1wXZDRU'),
    ('dalrant', 'DCpdPagMLbQ'),
    ('hyoseok', 'IjYr0FrINis'),
    ('hyoseok', 'Rdw1judfd5E'),
    ('hyoseok', 'Y-7UUKocmC0'),
]

results = []

for i, (prefix, vid) in enumerate(VIDEOS):
    out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
    ft_path = f'{SUBS_DIR}/{prefix}_{vid}_fulltext.txt'
    
    # Skip existing
    if os.path.exists(out_path):
        try:
            d = json.load(open(out_path, 'r', encoding='utf-8'))
            segs = d.get('segments', d.get('subtitles', []))
            if segs and len(segs) > 10:
                print(f"SKIP {vid} ({prefix}): {len(segs)} segs")
                results.append((vid, prefix, len(segs), 'skipped'))
                continue
        except:
            pass
    
    print(f"[{i+1}/9] {vid} ({prefix}): ", end='', flush=True)
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(vid, languages=['ko'])
        
        segments = []
        for snippet in transcript.snippets:
            segments.append({
                'start': snippet.start,
                'duration': snippet.duration,
                'text': snippet.text
            })
        
        if segments:
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'video_id': vid, 'channel': prefix, 'subtitles': segments}, f, ensure_ascii=False, indent=2)
            
            fulltext = '\n'.join(s['text'] for s in segments)
            with open(ft_path, 'w', encoding='utf-8') as f:
                f.write(fulltext)
            
            print(f"OK {len(segments)} segs")
            results.append((vid, prefix, len(segments), 'ok'))
        else:
            print("EMPTY")
            results.append((vid, prefix, 0, 'empty'))
    
    except Exception as e:
        err = str(e)
        if '429' in err or 'Too Many' in err:
            print(f"429 RATE LIMITED - waiting 1 hour...")
            time.sleep(3600)
            # Retry once
            try:
                ytt_api = YouTubeTranscriptApi()
                transcript = ytt_api.fetch(vid, languages=['ko'])
                segments = [{'start': s.start, 'duration': s.duration, 'text': s.text} for s in transcript.snippets]
                if segments:
                    with open(out_path, 'w', encoding='utf-8') as f:
                        json.dump({'video_id': vid, 'channel': prefix, 'subtitles': segments}, f, ensure_ascii=False, indent=2)
                    fulltext = '\n'.join(s['text'] for s in segments)
                    with open(ft_path, 'w', encoding='utf-8') as f:
                        f.write(fulltext)
                    print(f"OK (retry) {len(segments)} segs")
                    results.append((vid, prefix, len(segments), 'ok'))
                else:
                    print("EMPTY after retry")
                    results.append((vid, prefix, 0, 'empty'))
            except Exception as e2:
                print(f"FAIL after retry: {e2}")
                results.append((vid, prefix, 0, 'rate-limited'))
        else:
            print(f"ERROR: {err[:100]}")
            results.append((vid, prefix, 0, 'error'))
    
    # Delay between videos
    if i < len(VIDEOS) - 1:
        if (i + 1) % 3 == 0:
            delay = random.randint(150, 210)
            print(f"  --- Batch pause: {delay}s ---")
        else:
            delay = random.randint(5, 15)
        time.sleep(delay)

print(f"\n=== 결과 ===")
ok = sum(1 for _,_,_,s in results if s in ('ok', 'skipped'))
print(f"성공: {ok}/{len(results)}")
for vid, prefix, count, status in results:
    emoji = '✅' if status in ('ok','skipped') else '❌'
    print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")

with open(f'{SUBS_DIR}/batch4_results.json', 'w', encoding='utf-8') as f:
    json.dump([{'vid': v, 'prefix': p, 'count': c, 'status': s} for v,p,c,s in results], f, indent=2)
