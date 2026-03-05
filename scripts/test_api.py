import httpx, json, time
from pathlib import Path

key = [l.split("=",1)[1].strip() for l in Path("C:/Users/Mario/work/invest-sns/.env.local").read_text().splitlines() if l.startswith("ANTHROPIC_API_KEY=")][0]
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

r = httpx.get("https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_videos?select=title,subtitle_text&has_subtitle=eq.true&limit=1&order=published_at.desc",
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
v = r.json()[0]
sub = v["subtitle_text"][:12000]
print(f"Sub len: {len(sub)}")

prompt = f"이 자막에서 투자 종목과 시그널을 JSON으로 추출하세요:\n{sub}"
print(f"Prompt chars: {len(prompt)}")

t0 = time.time()
r2 = httpx.post("https://api.anthropic.com/v1/messages",
    headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    json={"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "messages": [{"role": "user", "content": prompt}]},
    timeout=180)
elapsed = time.time() - t0
print(f"Time: {elapsed:.1f}s, Status: {r2.status_code}")
d = r2.json()
print(f"Input: {d['usage']['input_tokens']}, Output: {d['usage']['output_tokens']}")
print(d["content"][0]["text"][:300])
