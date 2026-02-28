"""Insert signals for 이효석 videos"""
import httpx

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

VIDEO1_ID = "cfc9e60f-5bae-45c5-8e57-8f624f79298c"
VIDEO2_ID = "94ff3a67-01d6-49da-89ff-d461a810774c"
SPEAKER_ID = "b07d8758-493a-4a51-9bc5-7ef75f0be67c"

signals = [
    # Video 1: fDZnPoK5lyc
    {
        "video_id": VIDEO1_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "HD현대일렉트릭",
        "market": "KR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "medium",
        "timestamp": "08:12",
        "key_quote": "AI 인프라의 핵심 파트너가 돼 버렸다. 아주 강력한 모트",
        "reasoning": "전세계 5개 회사만 가능한 초고압 변압기 기술. 영업이익률 계속 상승. 다만 명확한 매수 권유 아님, 전망 형태.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": VIDEO1_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "효성중공업",
        "market": "KR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "medium",
        "timestamp": "08:15",
        "key_quote": "HD현대일렉트릭이나 효성중공업이 AI 인프라의 핵심 파트너가 돼 버렸다",
        "reasoning": "초고압 변압기 제조 가능 기업. 극도로 높은 진입장벽. 전망 형태이나 매수 권유 아님.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": VIDEO1_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "조선",
        "market": "SECTOR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "medium",
        "timestamp": "08:53",
        "key_quote": "아직 식지 않은 기대감. 단순 하청이 아닌 안보 파트너로 격상",
        "reasoning": "한국 조선사 실적 좋고 고수익 선박으로 전환. 미국 브릿지 전략 발표로 안보 파트너 격상. LNG 운반선 수요 증가.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": VIDEO1_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "현대차",
        "market": "KR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "medium",
        "timestamp": "15:26",
        "key_quote": "자동차 회사가 로봇 회사로 바뀌면서 멀티플이 바뀌는 어마어마한 그런게 있다",
        "reasoning": "자동차→로봇 전환으로 멀티플 변화 기대. 보스턴다이나믹스 R&D→대량생산 전환. GTC 행사 모멘텀.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    # Video 2: tSXkj2Omz34
    {
        "video_id": VIDEO2_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "삼성전자",
        "market": "KR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "high",
        "timestamp": "05:01",
        "key_quote": "영업이익 43조에서 201조. 이익이 다섯배 늘어난 회사는 본 적이 없어요",
        "reasoning": "영업이익 5배 증가 전망. 글로벌 시총 매달권 진입 가능성. 멀티플 9배 미만으로 극도로 저평가. 다만 '숫자를 따져보자' 형태로 전망.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": VIDEO2_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "SK하이닉스",
        "market": "KR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "high",
        "timestamp": "05:01",
        "key_quote": "하이닉스 멀티플 다섯배. 이게 말이 돼? 글로벌 3위 진입 가능성",
        "reasoning": "영업이익 47.4조 전망. 멀티플 5배로 글로벌 대비 극도로 저평가. 엔비디아보다 이익 더 나는데 시총 0.4조달러.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
    {
        "video_id": VIDEO2_ID,
        "speaker_id": SPEAKER_ID,
        "stock": "반도체",
        "market": "SECTOR",
        "signal": "긍정",
        "mention_type": "결론",
        "confidence": "high",
        "timestamp": "01:55",
        "key_quote": "반도체가 바뀌었는데 시장에서 제대로 평가를 못 받고 있다",
        "reasoning": "코스피 영업이익 증가분 중 반도체가 100% 기여(210조). 이익 비중 56% 역대 최고. 멀티플 7배→12배 정상화 시 코스피 7900 가능.",
        "pipeline_version": "V9.1",
        "review_status": "pending",
    },
]

ok = 0
for s in signals:
    r = httpx.post(BASE + "influencer_signals", headers=HEADERS, json=s)
    if r.status_code in (200, 201):
        print(f"OK: {s['stock']} ({s['signal']})")
        ok += 1
    else:
        print(f"FAIL: {s['stock']} - {r.status_code} {r.text[:200]}")

print(f"\n=== {ok}/{len(signals)} signals inserted ===")
