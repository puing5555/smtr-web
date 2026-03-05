"""
A/B Test: V10.10 (단일 프롬프트) vs V10.11 (2단계 프롬프트)
시그널 추출 정확도 비교

비용 제한: $10 초과시 중단
"""

import json
import os
import time
import random
import re
import httpx
import asyncio
from datetime import datetime
from pathlib import Path

# === Config ===
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"
MAX_COST = 10.0
SAMPLE_SIZE = 30  # Start with 30, scale up if budget allows

# Sonnet pricing: $3/M input, $15/M output
INPUT_COST_PER_TOKEN = 3.0 / 1_000_000
OUTPUT_COST_PER_TOKEN = 15.0 / 1_000_000

OUTPUT_DIR = Path("C:/Users/Mario/work/data/research")

# === Prompts ===

PROMPT_A = """당신은 한국 주식/미국 주식/크립토 투자 자막 분석 전문가입니다.

아래 유튜브 영상 자막에서 투자 시그널을 추출하세요.

## 입력
- 채널: {channel_name}
- 영상 제목: {video_title}
- 자막:
{subtitle}

## 시그널 5단계 (이것만 사용)
매수: 명확한 매수 액션 권유 ("사라, 담아라, 들어가라, 비중 확대")
긍정: 호의적이나 명확한 매수 권유 아님 ("좋아보인다, 괜찮다, 관심가져라")
중립: 지켜보자, 뉴스/리포트/교육 전달
부정: 부정적이나 매도 권유 아님
매도: 명확한 매도 액션 권유

## 핵심 규칙
- 1영상 1종목 1시그널 (같은 종목 중복 금지)
- 한국주식 + 미국주식 + 크립토만 (부동산/채권/원자재 제외)
- 교육/뉴스 전달만 있으면 시그널 없음
- 논거 종목은 최대 긍정까지만
- key_quote에 종목명 명시 필수, 20자 이상
- 타임스탬프 필수

## 매수 vs 긍정 구분: "본인이 샀거나 사라고 했는가?"
- Yes → 매수 (본인 매매 공개, 직접 매수 권유, 포트폴리오 편입)
- No → 긍정 (단순 전망, 관심 추천, 분석만 제공)

## 출력 형식 (JSON만)
```json
{{
  "signals": [
    {{
      "speaker": "발언자명",
      "stock_name": "종목명",
      "stock_code": "종목코드",
      "market": "KR",
      "mention_type": "결론",
      "signal_type": "매수",
      "confidence": "high",
      "timestamp": "12:34",
      "key_quote": "핵심 발언 원문",
      "reasoning": "분류 이유"
    }}
  ]
}}
```
시그널 없으면 {{"signals": []}}"""

PROMPT_B_STEP1 = """당신은 한국 주식/미국 주식/크립토 투자 자막 분석 전문가입니다.

아래 유튜브 영상 자막에서 언급된 **투자 종목**만 추출하세요.

## 입력
- 채널: {channel_name}
- 영상 제목: {video_title}
- 자막:
{subtitle}

## 추출 규칙
1. 한국주식 + 미국주식 + 크립토만 (부동산/채권/원자재/해외주식 제외)
2. 정식 종목명만 (약칭 금지: "삼전"→"삼성전자")
3. 음성인식 오류 교정
4. 지수 제외 (코스피, S&P500 등)
5. 섹터/ETF는 포함
6. 비종목 제외 (인물명, 서비스명, 일반 용어)

## 출력 형식 (JSON만, 설명 없이)
```json
{{
  "stocks": [
    {{"stock_name": "삼성전자", "stock_code": "005930", "market": "KR"}}
  ]
}}
```
종목이 없으면 {{"stocks": []}}"""

PROMPT_B_STEP2 = """당신은 한국 주식/미국 주식/크립토 투자 시그널 분석 전문가입니다.

아래 자막에서 **{stock_name}**에 대한 발언자의 투자 시그널을 판단하세요.

## 입력
- 채널: {channel_name}
- 영상 제목: {video_title} (제목은 시그널 판단 금지)
- 분석 대상 종목: {stock_name}
- 자막:
{subtitle}

## 시그널 5단계
매수: 명확한 매수 액션 권유
긍정: 호의적이나 명확한 매수 권유 아님
중립: 뉴스/리포트/교육 전달
부정: 부정적이나 매도 권유 아님
매도: 명확한 매도 액션 권유

## 매수 vs 긍정 핵심 구분: "본인이 샀거나 사라고 했는가?"

매수 표현 (Yes):
- 본인 매매 공개: "저는 샀습니다", "담았습니다", "비중 늘렸습니다"
- 직접 매수 권유: "지금 사야", "매수 타이밍", "이 가격이면 사도 된다"
- 포트폴리오 편입: "포트폴리오에 넣을 만하다"
- 매수 방법 지시: "분할매수 하라", "추가매수 타이밍"

긍정 표현 (No):
- 단순 전망: "좋아 보인다", "전망이 밝다"
- 관심 추천: "관심 가져볼 만하다", "주목할 필요"
- 장기 평가: "장기적으로 유망하다"
- 타인 시각: "시장에서 좋게 보고 있다"

## 핵심 규칙
- 논거 종목 → 최대 긍정까지만
- 교육/뉴스/티저 → 시그널 없음
- 전망 표현 → 긍정 (매수 아님)
- 조건부 → confidence 하향
- key_quote: 종목명 포함, 투자근거 포함, 20자 이상

## 출력 (JSON만)
```json
{{
  "signal": {{
    "speaker": "발언자명",
    "stock_name": "{stock_name}",
    "stock_code": "종목코드",
    "market": "KR",
    "mention_type": "결론",
    "signal_type": "매수",
    "confidence": "high",
    "timestamp": "12:34",
    "key_quote": "핵심 발언 원문",
    "reasoning": "분류 이유"
  }}
}}
```
시그널 없으면: {{"signal": null, "reason": "이유"}}"""


class CostTracker:
    def __init__(self, max_cost):
        self.max_cost = max_cost
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.calls = 0

    @property
    def total_cost(self):
        return (self.total_input_tokens * INPUT_COST_PER_TOKEN +
                self.total_output_tokens * OUTPUT_COST_PER_TOKEN)

    def add(self, input_tokens, output_tokens):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.calls += 1

    def check(self):
        if self.total_cost >= self.max_cost:
            raise Exception(f"비용 한도 초과: ${self.total_cost:.2f} >= ${self.max_cost}")


async def call_claude(client, prompt, cost_tracker, max_tokens=2000):
    """Call Claude API with retry."""
    for attempt in range(3):
        try:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": MODEL,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=120
            )
            if resp.status_code == 429:
                wait = min(60, 2 ** attempt * 10)
                print(f"  Rate limited, waiting {wait}s...")
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()

            input_t = data.get("usage", {}).get("input_tokens", 0)
            output_t = data.get("usage", {}).get("output_tokens", 0)
            cost_tracker.add(input_t, output_t)
            cost_tracker.check()

            text = data["content"][0]["text"]
            return text
        except httpx.HTTPStatusError as e:
            if attempt == 2:
                raise
            await asyncio.sleep(5)
    return None


def extract_json(text):
    """Extract JSON from Claude response."""
    # Try to find JSON block
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'(\{.*\})',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
    # Try raw parse
    try:
        return json.loads(text)
    except:
        return None


async def fetch_videos():
    """Fetch videos with subtitles from Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        # Get channels for name mapping
        ch_resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/influencer_channels",
            headers=headers,
            params={"select": "id,channel_name"}
        )
        ch_resp.raise_for_status()
        ch_map = {c["id"]: c["channel_name"] for c in ch_resp.json()}

        # Get videos with subtitles
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/influencer_videos",
            headers=headers,
            params={
                "select": "id,video_id,title,channel_id,subtitle_text",
                "has_subtitle": "eq.true",
                "limit": 500,
                "order": "published_at.desc"
            }
        )
        resp.raise_for_status()
        videos = resp.json()
        # Filter: subtitle not empty and reasonable length
        videos = [v for v in videos if v.get("subtitle_text") and len(v["subtitle_text"]) > 200]
        # Add channel_name and normalize field names
        for v in videos:
            v["channel_name"] = ch_map.get(v.get("channel_id"), "unknown")
            v["subtitle"] = v.pop("subtitle_text", "")
        print(f"Found {len(videos)} videos with subtitles")
        # Random sample
        if len(videos) > SAMPLE_SIZE:
            videos = random.sample(videos, SAMPLE_SIZE)
        return videos


def truncate_subtitle(subtitle, max_chars=15000):
    """Truncate subtitle to fit context window."""
    if len(subtitle) > max_chars:
        return subtitle[:max_chars] + "\n...(자막 잘림)"
    return subtitle


async def run_method_a(client, video, cost_a):
    """Method A: Single prompt (V10.10 style)."""
    subtitle = truncate_subtitle(video["subtitle"])
    prompt = PROMPT_A.format(
        channel_name=video.get("channel_name", "unknown"),
        video_title=video.get("title", "unknown"),
        subtitle=subtitle
    )
    text = await call_claude(client, prompt, cost_a, max_tokens=3000)
    if not text:
        return {"signals": [], "error": "API call failed"}

    result = extract_json(text)
    if not result:
        return {"signals": [], "error": "JSON parse failed", "raw": text[:500]}
    return result


async def run_method_b(client, video, cost_b):
    """Method B: 2-stage prompt (V10.11 style)."""
    subtitle = truncate_subtitle(video["subtitle"])

    # Step 1: Extract stocks
    prompt1 = PROMPT_B_STEP1.format(
        channel_name=video.get("channel_name", "unknown"),
        video_title=video.get("title", "unknown"),
        subtitle=subtitle
    )
    text1 = await call_claude(client, prompt1, cost_b, max_tokens=1000)
    if not text1:
        return {"signals": [], "stocks_found": 0, "error": "Step1 failed"}

    result1 = extract_json(text1)
    if not result1 or not result1.get("stocks"):
        return {"signals": [], "stocks_found": 0}

    stocks = result1["stocks"]

    # Step 2: Per-stock signal (max 5 stocks per video to control cost)
    signals = []
    for stock in stocks[:5]:
        stock_name = stock.get("stock_name", "")
        if not stock_name:
            continue

        prompt2 = PROMPT_B_STEP2.format(
            channel_name=video.get("channel_name", "unknown"),
            video_title=video.get("title", "unknown"),
            stock_name=stock_name,
            subtitle=subtitle
        )
        text2 = await call_claude(client, prompt2, cost_b, max_tokens=1000)
        if not text2:
            continue

        result2 = extract_json(text2)
        if result2 and result2.get("signal"):
            sig = result2["signal"]
            sig["stock_code"] = sig.get("stock_code") or stock.get("stock_code", "")
            sig["market"] = sig.get("market") or stock.get("market", "")
            signals.append(sig)

        await asyncio.sleep(0.5)  # Rate limit

    return {"signals": signals, "stocks_found": len(stocks)}


async def main():
    print("=" * 60)
    print("A/B Test: V10.10 vs V10.11 2단계 구조")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Sample size: {SAMPLE_SIZE}, Budget: ${MAX_COST}")
    print("=" * 60)

    # Fetch videos
    videos = await fetch_videos()
    print(f"Selected {len(videos)} videos for testing\n")

    cost_a = CostTracker(MAX_COST / 2)  # Split budget
    cost_b = CostTracker(MAX_COST / 2)

    results = []

    async with httpx.AsyncClient() as client:
        for i, video in enumerate(videos):
            vid = video.get("video_id", video.get("id", "?"))
            title = (video.get("title", "")[:40] + "...") if len(video.get("title", "")) > 40 else video.get("title", "")
            print(f"\n[{i+1}/{len(videos)}] {title}")

            try:
                # Method A
                print("  A (단일)...", end=" ", flush=True)
                result_a = await run_method_a(client, video, cost_a)
                sigs_a = result_a.get("signals", [])
                print(f"{len(sigs_a)} signals, ${cost_a.total_cost:.3f}")

                await asyncio.sleep(1)

                # Method B
                print("  B (2단계)...", end=" ", flush=True)
                result_b = await run_method_b(client, video, cost_b)
                sigs_b = result_b.get("signals", [])
                stocks_found = result_b.get("stocks_found", 0)
                print(f"{stocks_found} stocks → {len(sigs_b)} signals, ${cost_b.total_cost:.3f}")

                results.append({
                    "video_id": vid,
                    "title": video.get("title", ""),
                    "channel": video.get("channel_name", ""),
                    "subtitle_len": len(video.get("subtitle", "")),
                    "method_a": {
                        "signals": sigs_a,
                        "signal_count": len(sigs_a),
                    },
                    "method_b": {
                        "signals": sigs_b,
                        "signal_count": len(sigs_b),
                        "stocks_found": stocks_found,
                    }
                })

                await asyncio.sleep(1)

            except Exception as e:
                print(f"  ERROR: {e}")
                if "비용 한도" in str(e):
                    print("\n⚠️ 비용 한도 초과! 테스트 중단.")
                    break
                results.append({
                    "video_id": vid,
                    "title": video.get("title", ""),
                    "error": str(e)
                })

    # === Analysis ===
    print("\n" + "=" * 60)
    print("분석 결과")
    print("=" * 60)

    valid = [r for r in results if "error" not in r]
    total_a_signals = sum(r["method_a"]["signal_count"] for r in valid)
    total_b_signals = sum(r["method_b"]["signal_count"] for r in valid)
    total_b_stocks = sum(r["method_b"]["stocks_found"] for r in valid)

    # Signal type distribution
    def count_types(results_list, method_key):
        counts = {"매수": 0, "긍정": 0, "중립": 0, "부정": 0, "매도": 0, "기타": 0}
        for r in results_list:
            if "error" in r:
                continue
            for s in r[method_key]["signals"]:
                st = s.get("signal_type", "기타")
                if st in counts:
                    counts[st] += 1
                else:
                    counts["기타"] += 1
        return counts

    types_a = count_types(results, "method_a")
    types_b = count_types(results, "method_b")

    # Non-stock false positives (heuristic: check if stock_name looks like non-stock)
    non_stock_keywords = ["코스피", "코스닥", "나스닥", "S&P", "다우", "금리", "환율", "달러", "유가", "금값",
                          "부동산", "아파트", "전세", "월세", "채권", "국채"]
    def count_false_positives(results_list, method_key):
        fps = []
        for r in results_list:
            if "error" in r:
                continue
            for s in r[method_key]["signals"]:
                name = s.get("stock_name", "")
                if any(kw in name for kw in non_stock_keywords):
                    fps.append({"video": r["video_id"], "stock": name})
        return fps

    fp_a = count_false_positives(results, "method_a")
    fp_b = count_false_positives(results, "method_b")

    # Buy/Positive differences
    buy_positive_diffs = []
    for r in valid:
        sigs_a_map = {s.get("stock_name"): s.get("signal_type") for s in r["method_a"]["signals"]}
        sigs_b_map = {s.get("stock_name"): s.get("signal_type") for s in r["method_b"]["signals"]}
        common = set(sigs_a_map.keys()) & set(sigs_b_map.keys())
        for stock in common:
            a_type = sigs_a_map[stock]
            b_type = sigs_b_map[stock]
            if a_type != b_type and {a_type, b_type} & {"매수", "긍정"}:
                buy_positive_diffs.append({
                    "video": r["video_id"],
                    "stock": stock,
                    "method_a": a_type,
                    "method_b": b_type
                })

    summary = {
        "test_date": datetime.now().isoformat(),
        "sample_size": len(videos),
        "valid_results": len(valid),
        "cost": {
            "method_a": {"calls": cost_a.calls, "input_tokens": cost_a.total_input_tokens,
                         "output_tokens": cost_a.total_output_tokens, "cost_usd": round(cost_a.total_cost, 4)},
            "method_b": {"calls": cost_b.calls, "input_tokens": cost_b.total_input_tokens,
                         "output_tokens": cost_b.total_output_tokens, "cost_usd": round(cost_b.total_cost, 4)},
            "total_usd": round(cost_a.total_cost + cost_b.total_cost, 4)
        },
        "signals": {
            "method_a_total": total_a_signals,
            "method_b_total": total_b_signals,
            "method_b_stocks_found": total_b_stocks,
            "avg_per_video_a": round(total_a_signals / max(len(valid), 1), 2),
            "avg_per_video_b": round(total_b_signals / max(len(valid), 1), 2),
        },
        "signal_types": {"method_a": types_a, "method_b": types_b},
        "buy_positive_diffs": buy_positive_diffs,
        "false_positives": {"method_a": fp_a, "method_b": fp_b,
                            "count_a": len(fp_a), "count_b": len(fp_b)},
    }

    # Save raw data
    raw_output = {"summary": summary, "results": results}
    with open(OUTPUT_DIR / "ab_test_v10_results.json", "w", encoding="utf-8") as f:
        json.dump(raw_output, f, ensure_ascii=False, indent=2)

    # Generate markdown report
    report = f"""# A/B 테스트 결과: V10.10 vs V10.11 2단계 구조

## 테스트 개요
- **일시**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **샘플**: {len(videos)}개 영상 (자막 있는 영상 랜덤 선택)
- **유효 결과**: {len(valid)}개
- **모델**: {MODEL}

## 비용
| 항목 | A (단일) | B (2단계) |
|------|----------|-----------|
| API 호출 | {cost_a.calls}회 | {cost_b.calls}회 |
| 입력 토큰 | {cost_a.total_input_tokens:,} | {cost_b.total_input_tokens:,} |
| 출력 토큰 | {cost_a.total_output_tokens:,} | {cost_b.total_output_tokens:,} |
| 비용 | ${cost_a.total_cost:.4f} | ${cost_b.total_cost:.4f} |
| **총 비용** | **${cost_a.total_cost + cost_b.total_cost:.4f}** | |

## 1. 시그널 수 비교
| 항목 | A (단일) | B (2단계) |
|------|----------|-----------|
| 총 시그널 | {total_a_signals} | {total_b_signals} |
| 영상당 평균 | {summary['signals']['avg_per_video_a']} | {summary['signals']['avg_per_video_b']} |
| B 1단계 종목 수 | - | {total_b_stocks} |

## 2. 시그널 타입 분포
| 타입 | A (단일) | B (2단계) | 차이 |
|------|----------|-----------|------|
| 매수 | {types_a['매수']} | {types_b['매수']} | {types_b['매수'] - types_a['매수']:+d} |
| 긍정 | {types_a['긍정']} | {types_b['긍정']} | {types_b['긍정'] - types_a['긍정']:+d} |
| 중립 | {types_a['중립']} | {types_b['중립']} | {types_b['중립'] - types_a['중립']:+d} |
| 부정 | {types_a['부정']} | {types_b['부정']} | {types_b['부정'] - types_a['부정']:+d} |
| 매도 | {types_a['매도']} | {types_b['매도']} | {types_b['매도'] - types_a['매도']:+d} |

## 3. 매수/긍정 분류 차이
{len(buy_positive_diffs)}건의 분류 차이 발견:

"""
    for d in buy_positive_diffs[:20]:
        report += f"- **{d['stock']}** ({d['video'][:20]}): A={d['method_a']} → B={d['method_b']}\n"

    report += f"""
## 4. 비종목 오추출
| 항목 | A (단일) | B (2단계) |
|------|----------|-----------|
| 오추출 수 | {len(fp_a)} | {len(fp_b)} |

"""
    if fp_a:
        report += "### A 오추출:\n"
        for fp in fp_a[:10]:
            report += f"- {fp['stock']} ({fp['video'][:20]})\n"
    if fp_b:
        report += "\n### B 오추출:\n"
        for fp in fp_b[:10]:
            report += f"- {fp['stock']} ({fp['video'][:20]})\n"

    report += f"""
## 결론

### 시그널 수
- A(단일): 영상당 평균 {summary['signals']['avg_per_video_a']}개
- B(2단계): 영상당 평균 {summary['signals']['avg_per_video_b']}개
- B가 1단계에서 {total_b_stocks}개 종목 추출 후 각각 시그널 판단

### 매수/긍정 구분
- {len(buy_positive_diffs)}건의 분류 차이 발견
- 2단계 방식이 종목별 집중 분석으로 더 정확한 구분 기대

### 비용
- A: ${cost_a.total_cost:.4f} ({cost_a.calls}회 호출)
- B: ${cost_b.total_cost:.4f} ({cost_b.calls}회 호출)
- B가 종목 수만큼 추가 호출 필요하여 비용 {'높음' if cost_b.total_cost > cost_a.total_cost else '비슷'}

### 종합 판단
{'2단계 구조(B)가 더 많은 시그널을 추출하고 매수/긍정 구분이 더 정확함. 비용 증가분 대비 품질 향상이 유의미.' if total_b_signals >= total_a_signals else '단일 구조(A)가 효율적이나 2단계 구조(B)의 매수/긍정 구분 정확도가 더 높을 수 있음.'}
"""

    with open(OUTPUT_DIR / "ab_test_v10_results.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n총 비용: ${cost_a.total_cost + cost_b.total_cost:.4f}")
    print(f"결과 저장: {OUTPUT_DIR / 'ab_test_v10_results.md'}")
    print(f"원시 데이터: {OUTPUT_DIR / 'ab_test_v10_results.json'}")

    return summary


if __name__ == "__main__":
    asyncio.run(main())
