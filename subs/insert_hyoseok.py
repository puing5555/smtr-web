"""Insert 이효석 analysis results to Supabase"""
import httpx
import json
import uuid

BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def post(table, data):
    r = httpx.post(BASE + table, headers=HEADERS, json=data)
    if r.status_code in (200, 201):
        result = r.json()
        print(f"  INSERT {table}: OK")
        return result[0] if isinstance(result, list) else result
    else:
        print(f"  INSERT {table}: FAILED {r.status_code} {r.text[:200]}")
        return None

# 1. Create channel: 이효석아카데미
print("=== Creating channel ===")
channel = post("influencer_channels", {
    "channel_name": "이효석아카데미",
    "channel_handle": "@hyoseok_academy",
    "channel_url": "https://www.youtube.com/@hyoseok_academy",
    "platform": "youtube"
})
if not channel:
    print("Channel creation failed, exiting")
    exit(1)
channel_id = channel["id"]
print(f"  Channel ID: {channel_id}")

# 2. Create speaker: 이효석
print("=== Creating speaker ===")
speaker = post("speakers", {
    "name": "이효석",
    "aliases": ["이효석", "이호석", "효석"]
})
if not speaker:
    print("Speaker creation failed, exiting")
    exit(1)
speaker_id = speaker["id"]
print(f"  Speaker ID: {speaker_id}")

# 3. Insert videos
print("\n=== Video 1: fDZnPoK5lyc ===")
video1 = post("influencer_videos", {
    "channel_id": channel_id,
    "video_id": "fDZnPoK5lyc",
    "title": "반도체 다음 무섭게 치고나갈 충격적 4종목 바로 찍어드립니다",
    "has_subtitle": True,
    "subtitle_language": "ko",
    "analyzed_at": "2026-02-28T09:00:00+00:00",
    "pipeline_version": "V9.1",
    "signal_count": 4
})
video1_id = video1["id"] if video1 else None

print("\n=== Video 2: tSXkj2Omz34 ===")
video2 = post("influencer_videos", {
    "channel_id": channel_id,
    "video_id": "tSXkj2Omz34",
    "title": "[속보효] 코스피 6000 돌파… 7,900 논리까지 바로 공개합니다",
    "has_subtitle": True,
    "subtitle_language": "ko",
    "analyzed_at": "2026-02-28T09:00:00+00:00",
    "pipeline_version": "V9.1",
    "signal_count": 3
})
video2_id = video2["id"] if video2 else None

# 4. Insert signals for Video 1
if video1_id:
    print("\n=== Signals for Video 1 ===")
    signals_v1 = [
        {
            "video_id": video1_id,
            "speaker_id": speaker_id,
            "ticker_name": "HD현대일렉트릭",
            "market": "KR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "medium",
            "timestamp_start": 492,
            "reasoning": "전력기기/초고압 변압기 섹터. 전세계 5개 회사만 가능한 기술, 극도로 높은 진입장벽, 영업이익률 계속 상승. '다 좋다'고 표현. 다만 명확한 매수 권유 어미 없이 전망 형태.",
        },
        {
            "video_id": video1_id,
            "speaker_id": speaker_id,
            "ticker_name": "효성중공업",
            "market": "KR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "medium",
            "timestamp_start": 492,
            "reasoning": "HD현대일렉트릭과 함께 초고압 변압기 제조 가능 기업으로 언급. AI 인프라의 핵심 파트너, 강력한 모트. 전망 형태이나 매수 권유 아님.",
        },
        {
            "video_id": video1_id,
            "speaker_id": speaker_id,
            "ticker_name": "조선",
            "market": "SECTOR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "medium",
            "timestamp_start": 533,
            "reasoning": "한국 조선사 실적 좋고, 미국 브릿지 전략 발표로 단순 하청→안보 파트너 격상. 고수익 선박으로 전환, LNG 운반선 수요 증가. '상당히 좋은 흐름이 장기적으로 예상된다'.",
        },
        {
            "video_id": video1_id,
            "speaker_id": speaker_id,
            "ticker_name": "현대차",
            "market": "KR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "medium",
            "timestamp_start": 926,
            "reasoning": "자동차→로봇 전환으로 멀티플 변화 기대. 보스턴다이나믹스 CEO 교체는 R&D→대량생산 전환 신호. GTC 행사와 엔비디아 실적으로 추가 모멘텀. 다만 전망 형태.",
        },
    ]
    for s in signals_v1:
        post("influencer_signals", s)

# 5. Insert signals for Video 2
if video2_id:
    print("\n=== Signals for Video 2 ===")
    signals_v2 = [
        {
            "video_id": video2_id,
            "speaker_id": speaker_id,
            "ticker_name": "삼성전자",
            "market": "KR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "high",
            "timestamp_start": 301,
            "reasoning": "영업이익 43조→201조(5배 증가) 전망. 글로벌 시총 3위 매달권 진입 가능성. 멀티플 9배도 안되는 상황을 '너무 싸다'고 평가. 단 명확한 매수 권유 어미 없이 '숫자를 따져보자' 형태.",
        },
        {
            "video_id": video2_id,
            "speaker_id": speaker_id,
            "ticker_name": "SK하이닉스",
            "market": "KR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "high",
            "timestamp_start": 301,
            "reasoning": "영업이익 47.4조 전망. 멀티플 5배로 글로벌 대비 극도로 저평가. 이익이 엔비디아 수준인데 시총은 0.4조달러에 불과. ADR 발행 가능성 언급.",
        },
        {
            "video_id": video2_id,
            "speaker_id": speaker_id,
            "ticker_name": "반도체",
            "market": "SECTOR",
            "signal_type": "긍정",
            "mention_type": "결론",
            "confidence": "high",
            "timestamp_start": 115,
            "reasoning": "코스피 영업이익 350조→570조 중 반도체가 210조 증가(100% 기여). 이익 비중 56% 역대 최고. 멀티플 7배→12배 정상화 시 코스피 7900 가능. '반도체가 바뀌었는데 시장에서 제대로 평가를 못 받고 있다'.",
        },
    ]
    for s in signals_v2:
        post("influencer_signals", s)

print("\n=== DONE ===")
print(f"Channel: {channel_id}")
print(f"Speaker: {speaker_id}")
print(f"Video1: {video1_id}")
print(f"Video2: {video2_id}")
print(f"Total signals: {len(signals_v1) + len(signals_v2)}")
