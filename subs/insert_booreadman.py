import httpx
import json
import uuid
from datetime import datetime

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def insert(table, data):
    r = httpx.post(f"{BASE}/{table}", headers=HEADERS, json=data)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and len(result) > 0:
            print(f"  OK: {table} -> {result[0].get('id', 'done')}")
            return result[0]
        print(f"  OK: {table}")
        return result
    else:
        print(f"  FAIL {table}: {r.status_code} {r.text}")
        return None

# 1. Channel: 부읽남TV
channel_id = str(uuid.uuid4())
ch = insert("influencer_channels", {
    "id": channel_id,
    "channel_name": "부읽남TV",
    "channel_handle": "@buiknam_tv",
    "channel_url": "https://www.youtube.com/@buiknam_tv",
    "platform": "youtube"
})
if ch:
    channel_id = ch["id"]
print(f"Channel ID: {channel_id}")

# 2. Speaker: 조진표
speaker_id = str(uuid.uuid4())
sp = insert("speakers", {
    "id": speaker_id,
    "name": "조진표",
    "aliases": ["조진표"]
})
if sp:
    speaker_id = sp["id"]
print(f"Speaker ID: {speaker_id}")

# 3. Video
video_id = str(uuid.uuid4())
vid = insert("influencer_videos", {
    "id": video_id,
    "channel_id": channel_id,
    "video_id": "Xv-wNA91EPE",
    "title": "삼성전자 절대 팔지 마세요, 상상 못했던 일 벌어집니다 [조진표 대표 2부]",
    "published_at": "2026-02-23T00:00:00+09:00",
    "duration_seconds": 1540,
    "has_subtitle": True,
    "subtitle_language": "ko",
    "analyzed_at": datetime.utcnow().isoformat() + "+00:00",
    "pipeline_version": "V9",
    "signal_count": 5
})
if vid:
    video_id = vid["id"]
print(f"Video ID: {video_id}")

# 4. Signals
signals = [
    {
        "video_id": video_id,
        "speaker_id": speaker_id,
        "stock": "삼성전자",
        "ticker": "005930",
        "market": "KR",
        "mention_type": "결론",
        "signal": "매수",
        "confidence": "high",
        "timestamp": "3:52",
        "key_quote": "20만 원은 전 출발점이 아닐까라고 말씀을 드리고 싶습니다",
        "reasoning": "433전략에서 핵심 메모리 대형주 40% 비중 권유. HBM4 세계 최초 양산, 파운드리 흑자전환 앞당김, 자사주 소각 등 다수 긍정 근거. '포트폴리오에 당연히 있으셔야 된다'고 명확한 매수 권유.",
        "review_status": "pending",
        "pipeline_version": "V9"
    },
    {
        "video_id": video_id,
        "speaker_id": speaker_id,
        "stock": "SK하이닉스",
        "ticker": "000660",
        "market": "KR",
        "mention_type": "결론",
        "signal": "매수",
        "confidence": "high",
        "timestamp": "17:09",
        "key_quote": "SK하이닉스하고 삼성원자 같은 경우에는 여러분들 포트폴리오에 당연히 있으셔야 된다",
        "reasoning": "PER 14배로 삼성전자(24배) 대비 저평가. HBM 점유율 63% 유지, 노무라 목표주가 156만원(65-70% 상승여력). '빠른 말' 비유로 고성장주 성격 강조. 두 종목 모두 사고 싶다고 명확한 매수 의견.",
        "review_status": "pending",
        "pipeline_version": "V9"
    },
    {
        "video_id": video_id,
        "speaker_id": speaker_id,
        "stock": "원익IPS",
        "ticker": "240810",
        "market": "KR",
        "mention_type": "결론",
        "signal": "긍정",
        "confidence": "medium",
        "timestamp": "19:23",
        "key_quote": "눌림목 오게 되면 매수하는 전략도 나쁘지 않다",
        "reasoning": "삼성 캡텍스 직접 수혜자, 파운드리 장비 매출 비중 20%. 소부장 종목 30% 비중 배분 권유 중 첫 번째로 언급. 단, '눌림목 오면 매수' 조건부 발언이라 매수가 아닌 긍정으로 분류.",
        "review_status": "pending",
        "pipeline_version": "V9"
    },
    {
        "video_id": video_id,
        "speaker_id": speaker_id,
        "stock": "주성엔지니어링",
        "ticker": "036930",
        "market": "KR",
        "mention_type": "결론",
        "signal": "긍정",
        "confidence": "medium",
        "timestamp": "19:59",
        "key_quote": "기술 옵션이 가장 풍부한 종목, 눌림목 오게 되면 매수하는 전략도 나쁘지 않다",
        "reasoning": "HBM 전공정/후공정 수혜 종목. 중장기적 안정적 실적과 기술 옵션 풍부. 단기 실적 변동성은 유동적이나 중장기 긍정적. 조건부(눌림목 매수) 발언으로 긍정 분류.",
        "review_status": "pending",
        "pipeline_version": "V9"
    },
    {
        "video_id": video_id,
        "speaker_id": speaker_id,
        "stock": "한미반도체",
        "ticker": "042700",
        "market": "KR",
        "mention_type": "결론",
        "signal": "긍정",
        "confidence": "medium",
        "timestamp": "23:56",
        "key_quote": "대한민국 장비주에서 한미반도체나 원익IPS 같은 이런 종목군들 매수하시게 된다라면 어렵지 않을 것 같고요",
        "reasoning": "소부장 30% 배분 전략 내에서 장비주로 언급. 반도체 장비 시장 2030년까지 연평균 7.5-8% 성장 전망 근거. 명확한 '사라'가 아닌 배분 전략 맥락이라 긍정 분류.",
        "review_status": "pending",
        "pipeline_version": "V9"
    }
]

print("\n=== Inserting signals ===")
for s in signals:
    insert("influencer_signals", s)

print("\nDone!")
