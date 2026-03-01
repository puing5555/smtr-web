"""Insert last 2 videos + signals: hyoseok bmXgryWXNrw + dalant 5mvn3PfKf9Y"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import httpx

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
H = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get(table, params=""):
    return httpx.get(BASE + table + params, headers=H).json()

def post(table, data):
    r = httpx.post(BASE + table, json=data, headers=H)
    result = r.json()
    if r.status_code >= 400:
        print(f"  ERROR {table}: {result}")
        return None
    return result

# Known IDs
HYOSEOK_CHANNEL = "d153b75b-1843-4a99-b49f-c31081a8f566"

# Get 이효석 speaker
speakers = get("speakers", "?select=id,name")
hyoseok_speaker = next((s for s in speakers if s['name'] == '이효석'), None)
if hyoseok_speaker:
    HYOSEOK_SPEAKER = hyoseok_speaker['id']
    print(f"이효석 speaker: {HYOSEOK_SPEAKER}")
else:
    # Create speaker
    result = post("speakers", {"name": "이효석", "channel_id": HYOSEOK_CHANNEL})
    HYOSEOK_SPEAKER = result[0]['id']
    print(f"Created 이효석 speaker: {HYOSEOK_SPEAKER}")

# Create 달란트투자 channel
dalant_channels = get("influencer_channels", "?channel_name=ilike.*달란트*")
if dalant_channels:
    DALANT_CHANNEL = dalant_channels[0]['id']
    print(f"달란트 channel exists: {DALANT_CHANNEL}")
else:
    result = post("influencer_channels", {
        "channel_name": "달란트투자",
        "channel_handle": "@dalant_invest",
        "channel_url": "https://www.youtube.com/@dalant_invest",
        "platform": "youtube"
    })
    DALANT_CHANNEL = result[0]['id']
    print(f"Created 달란트 channel: {DALANT_CHANNEL}")

# Create 달란트투자 speaker
dalant_speakers = get("speakers", "?name=eq.달란트투자")
if dalant_speakers:
    DALANT_SPEAKER = dalant_speakers[0]['id']
    print(f"달란트 speaker exists: {DALANT_SPEAKER}")
else:
    result = post("speakers", {"name": "달란트투자", "channel_id": DALANT_CHANNEL})
    DALANT_SPEAKER = result[0]['id']
    print(f"Created 달란트 speaker: {DALANT_SPEAKER}")

# Insert videos
print("\n--- Inserting videos ---")

# Video 1: bmXgryWXNrw (이효석 - 하이닉스)
v1 = post("influencer_videos", {
    "channel_id": HYOSEOK_CHANNEL,
    "video_id": "bmXgryWXNrw",
    "title": "하이닉스 없거나 추가 매수 고민하는 분들 제가 시원하게 바로 말씀드립니다 [Z1뉴스]",
    "has_subtitle": True,
    "subtitle_language": "ko",
})
if v1:
    V1_ID = v1[0]['id']
    print(f"Video 1 inserted: {V1_ID}")
else:
    print("Video 1 failed!")
    sys.exit(1)

# Video 2: 5mvn3PfKf9Y (달란트 - SMR/현대건설)
v2 = post("influencer_videos", {
    "channel_id": DALANT_CHANNEL,
    "video_id": "5mvn3PfKf9Y",
    "title": "SMR 올해 가장 강력한 섹터! 현대건설이 세계 최초 SMR 착공",
    "has_subtitle": True,
    "subtitle_language": "ko",
})
if v2:
    V2_ID = v2[0]['id']
    print(f"Video 2 inserted: {V2_ID}")
else:
    print("Video 2 failed!")
    sys.exit(1)

# Insert signals
print("\n--- Inserting signals ---")

signals = [
    # === Video 1: bmXgryWXNrw (이효석 - SK하이닉스/삼성전자) ===
    {
        "video_id": V1_ID,
        "speaker_id": HYOSEOK_SPEAKER,
        "stock": "SK하이닉스",
        "ticker": "000660",
        "market": "KR",
        "signal": "매수",
        "mention_type": "결론",
        "confidence": "high",
        "timestamp": "00:48",
        "key_quote": "지금이라도 사야 돼. 저는 뭐 사야 된다고 생각하지만. 추가적으로 담아가시는 전략이 낫지 않을까",
        "reasoning": "메모리 수요-공급 불균형 심화(NAND 부족 3년 전망), 장기계약 요구 증가, 2026년 설비투자 확대, AI 에이전트로 메모리 수요 폭증. 명확한 매수 권유('사야 된다') + 분할매수 전략 제안. ADR 상장 기대감도 추가 호재.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": V1_ID,
        "speaker_id": HYOSEOK_SPEAKER,
        "stock": "삼성전자",
        "ticker": "005930",
        "market": "KR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "medium",
        "timestamp": "09:36",
        "key_quote": "삼성전자도 좋아요. 시티은행 영업이익 251조원, 목표가 매수의견",
        "reasoning": "시티은행 영업이익 전망 182조→251조(38% 상향), 서버DRAM 가격 290% 상승 전망, DDR5 가격 상반기 상승. 다만 '좋아요'는 긍정 표현이지 명확한 매수 권유 아님. SK하이닉스가 10배 오른 반면 삼성전자 3-4배로 상대적 매력 언급.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    # === Video 2: 5mvn3PfKf9Y (달란트 - 현대건설/SMR) ===
    {
        "video_id": V2_ID,
        "speaker_id": DALANT_SPEAKER,
        "stock": "현대건설",
        "ticker": "000720",
        "market": "KR",
        "signal": "매수",
        "mention_type": "결론",
        "confidence": "high",
        "timestamp": "14:08",
        "key_quote": "SMR 1등 기업은 현대건설. 놓치지 마시고 분할로라도 공략해 보시면 좋을 것 같습니다",
        "reasoning": "미국 팰리세이즈 원전 SMR 2기 3월내 착공 예정(세계 최초), SMR특별법 통과, 수주잔고 95조(건설사 1위), 영업이익 흑자전환, MSCI IG 편입. '놓치지 마시고 분할로 공략'은 명확한 매수 권유.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": V2_ID,
        "speaker_id": DALANT_SPEAKER,
        "stock": "SMR/원전",
        "market": "SECTOR",
        "signal": "매수",
        "mention_type": "결론",
        "confidence": "high",
        "timestamp": "00:33",
        "key_quote": "단언컨대 SMR은 올해 가장 강력한 섹터가 될 것입니다",
        "reasoning": "AI 데이터센터 전력부족 심화, 빅테크(MS/구글/아마존/메타) SMR 투자, 트럼프 원전용량 3배 선언, 한국 SMR특별법 통과. '올해 가장 강력한 섹터'로 단언하며 투자 적기로 판단.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
]

for sig in signals:
    result = post("influencer_signals", sig)
    if result:
        print(f"  Signal: {sig['stock']} ({sig['signal']}) -> {result[0]['id'][:8]}...")
    else:
        print(f"  FAILED: {sig['stock']}")

# Count total signals
total = get("influencer_signals", "?select=id")
print(f"\nTotal signals in DB: {len(total)}")
