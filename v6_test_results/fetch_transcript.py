import sys
from youtube_transcript_api import YouTubeTranscriptApi

video_id = sys.argv[1]
ytt = YouTubeTranscriptApi()
try:
    t = ytt.fetch(video_id, languages=['ko'])
except Exception as e:
    print(f"Error with ko: {e}")
    try:
        tl = ytt.list(video_id)
        print("Available transcripts:")
        for tr in tl:
            print(f"  {tr.language} ({tr.language_code}) auto={tr.is_generated}")
        # try first available
        t = tl[0].fetch()
    except Exception as e2:
        print(f"Error listing: {e2}")
        sys.exit(1)

for snippet in t.snippets:
    ts = int(snippet.start)
    mm, ss = divmod(ts, 60)
    print(f"[{mm}:{ss:02d}] {snippet.text}")

print(f"\n--- Total: {len(t.snippets)} entries ---")
