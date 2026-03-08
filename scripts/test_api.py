import httpx, time, sys
print("Starting test...", flush=True)

# Test 1: Supabase
t0 = time.time()
print("Testing Supabase...", flush=True)
try:
    r = httpx.get("https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_videos?select=id&limit=1",
        headers={"apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"},
        timeout=30)
    print(f"Supabase OK: {time.time()-t0:.1f}s, {r.status_code}", flush=True)
except Exception as e:
    print(f"Supabase ERROR: {e}", flush=True)

# Test 2: Anthropic
from pathlib import Path
key = [l.split("=",1)[1].strip() for l in Path("C:/Users/Mario/work/invest-sns/.env.local").read_text().splitlines() if l.startswith("ANTHROPIC_API_KEY=")][0]
print(f"Key: {key[:20]}...", flush=True)

t0 = time.time()
print("Testing Anthropic...", flush=True)
try:
    r = httpx.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": "claude-sonnet-4-6", "max_tokens": 50, "messages": [{"role": "user", "content": "hi"}]},
        timeout=30)
    print(f"Anthropic OK: {time.time()-t0:.1f}s, {r.status_code}", flush=True)
    print(r.text[:200], flush=True)
except Exception as e:
    print(f"Anthropic ERROR: {e}", flush=True)

print("Done!", flush=True)

