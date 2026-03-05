"""Quick test: run A and B on exactly 1 video."""
import httpx, json, time, sys
from pathlib import Path

key = [l.split("=",1)[1].strip() for l in Path("C:/Users/Mario/work/invest-sns/.env.local").read_text().splitlines() if l.startswith("ANTHROPIC_API_KEY=")][0]
SKEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

print("Fetching video...", flush=True)
r = httpx.get("https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_videos?select=title,subtitle_text&has_subtitle=eq.true&limit=1&order=published_at.desc",
    headers={"apikey": SKEY, "Authorization": f"Bearer {SKEY}"}, timeout=30)
v = r.json()[0]
sub = v["subtitle_text"][:8000]
print(f"Got: {v['title'][:40]}, sub={len(sub)} chars", flush=True)

def call(prompt, mt=2000):
    t0 = time.time()
    r = httpx.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": "claude-sonnet-4-20250514", "max_tokens": mt, "messages": [{"role": "user", "content": prompt}]},
        timeout=120)
    el = time.time() - t0
    d = r.json()
    inp = d["usage"]["input_tokens"]
    out = d["usage"]["output_tokens"]
    txt = d["content"][0]["text"]
    print(f"  {el:.1f}s, {inp}+{out} tokens", flush=True)
    return txt

# Method A
print("\n=== Method A ===", flush=True)
pa = f"""자막에서 투자 시그널 추출. 시그널: 매수/긍정/중립/부정/매도. JSON출력.
자막: {sub}
{{"signals": [{{"speaker":"","stock_name":"","signal_type":"","timestamp":"","key_quote":"","reasoning":""}}]}}"""
ta = call(pa)
print(ta[:300], flush=True)

# Method B step 1
print("\n=== Method B Step 1 ===", flush=True)
pb1 = f"""자막에서 투자 종목만 추출. JSON출력.
자막: {sub}
{{"stocks": [{{"stock_name":"","stock_code":"","market":""}}]}}"""
tb1 = call(pb1, 500)
print(tb1[:300], flush=True)

print("\nDone!", flush=True)
