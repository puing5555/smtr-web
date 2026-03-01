import sys; sys.stdout.reconfigure(encoding='utf-8')
import httpx

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

r = httpx.get(BASE + "influencer_videos?select=id,video_id,title,video_summary,duration_seconds", headers=H)
videos = r.json()

print(f"Total videos: {len(videos)}\n")

for v in sorted(videos, key=lambda x: len(x.get('video_summary') or ''), reverse=False):
    summary = v.get('video_summary') or ''
    lines = len(summary.split('\n')) if summary else 0
    chars = len(summary)
    title = (v.get('title') or '')[:50]
    vid = v['video_id']
    status = 'OK' if chars > 300 else 'SHORT' if chars > 0 else 'EMPTY'
    print(f"[{status:5}] {chars:4}c {lines:2}L | {vid} | {title}")
