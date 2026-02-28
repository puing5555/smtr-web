import httpx
import json

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Get existing video_id and speaker_id for 부읽남TV 조진표
r = httpx.get(f"{BASE}/influencer_videos?video_id=eq.Xv-wNA91EPE&select=id", headers=HEADERS)
video_uuid = r.json()[0]["id"]
print(f"Video UUID: {video_uuid}")

r2 = httpx.get(f"{BASE}/speakers?name=eq.조진표&select=id", headers=HEADERS)
speaker_uuid = r2.json()[0]["id"]
print(f"Speaker UUID: {speaker_uuid}")

# Insert missing signals
signals = [
    {
        "video_id": video_uuid,
        "speaker_id": speaker_uuid,
        "stock": "HPSP",
        "ticker": "403870",
        "market": "KR",
        "mention_type": "결론",
        "signal": "긍정",
        "confidence": "medium",
        "timestamp": "20:27",
        "key_quote": "HPSP하고 PSK 또는 파크시스템 같은 종목들, 파운드리 증설이라든지 미국 팹 투자가 계속 전개될 경우 수혜를 많이 볼 수 있는 종목들",
        "reasoning": "소부장 30% 배분 전략 내 파운드리 장비주로 구체적 언급. 파운드리 증설/미국 팹 투자 수혜 종목. '적은 규모의 수주에도 주가 진폭이 크다'고 변동성 경고 포함. 조건부(파운드리 증설 시) 발언이라 긍정 분류.",
        "review_status": "pending",
        "pipeline_version": "V9"
    },
    {
        "video_id": video_uuid,
        "speaker_id": speaker_uuid,
        "stock": "SOXX",
        "ticker": "SOXX",
        "market": "ETF",
        "mention_type": "결론",
        "signal": "긍정",
        "confidence": "medium",
        "timestamp": "24:48",
        "key_quote": "SOSX라고 하는 ETF가 있으니까 반도체 ETF거든요. 이런 ETF 쪽에 30% 정도 투자하게 되면 어렵지 않게 수익을 낼 수 있지 않을까",
        "reasoning": "433전략의 글로벌 AI 반도체 30% 배분에서 직접 추천한 ETF. 엔비디아 등 개별종목이 어려운 투자자를 위한 대안으로 제시. '어렵지 않게 수익을 낼 수 있지 않을까'는 전망형 표현이라 매수가 아닌 긍정 분류.",
        "review_status": "pending",
        "pipeline_version": "V9"
    }
]

# Also update video signal_count from 5 to 7
for s in signals:
    r = httpx.post(f"{BASE}/influencer_signals", headers=HEADERS, json=s)
    if r.status_code in (200, 201):
        result = r.json()
        print(f"OK: {s['stock']} -> {result[0]['id']}")
    else:
        print(f"FAIL: {s['stock']} {r.status_code} {r.text}")

# Update video signal_count
patch_headers = {**HEADERS, "Prefer": "return=representation"}
r = httpx.patch(f"{BASE}/influencer_videos?id=eq.{video_uuid}", headers=patch_headers, json={"signal_count": 7})
print(f"Updated video signal_count: {r.status_code}")
print("Done!")
