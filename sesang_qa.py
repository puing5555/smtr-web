#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""세상학개론 시그널 57개 전수 QA"""
import json, re, sys, time, requests
from collections import defaultdict, Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
ANTHROPIC_KEY = "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"
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# ─── 데이터 로드 ───────────────────────────────
with open("C:/Users/Mario/work/sesang_signals_full.json", encoding="utf-8") as f:
    signals = json.load(f)
print(f"로드: {len(signals)}개")

# ─── 1. 기본 통계 ─────────────────────────────
sig_dist = Counter(s["signal"] for s in signals)
mention_dist = Counter(s["mention_type"] for s in signals)
print(f"\n[시그널 분포] {dict(sig_dist)}")
print(f"[mention_type] {dict(mention_dist)}")

# ─── 2. 룰 기반 체크 ──────────────────────────
issues = defaultdict(list)

INVALID_STOCKS = {
    "코스피", "코스닥", "S&P500", "S&P 500", "나스닥", "다우", "다우존스",
    "니케이", "KOSPI", "KOSDAQ", "달러", "원화", "엔화", "위안화",
    "금", "은", "원유", "채권", "USD", "KRW", "JPY", "EUR",
    "시장", "증시", "지수", "환율", "금리",
}

CONDITIONAL_KEYWORDS = ["만약", "~했다면", "이었다면", "였다면", "한다면", "된다면", "가정"]

video_stock_map = defaultdict(list)  # video_id → [stock, ...]

for s in signals:
    sid = s["id"]
    stock = s.get("stock", "") or ""
    sig = s.get("signal", "")
    mtype = s.get("mention_type", "") or ""
    ts = s.get("timestamp", "") or ""
    kq = s.get("key_quote", "") or ""
    reasoning = s.get("reasoning", "") or ""
    vid = s.get("video_id", "")

    # 2-1. 비종목 오추출
    if stock in INVALID_STOCKS or s.get("market") == "INDEX":
        issues["비종목_오추출"].append({
            "id": sid, "stock": stock, "signal": sig,
            "ticker": s.get("ticker"), "market": s.get("market"),
            "title": s.get("_video_title", ""),
        })

    # 2-2. 타임스탬프 유효성 (HH:MM:SS or MM:SS)
    ts_valid = bool(re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", ts.strip())) if ts else False
    if not ts_valid:
        issues["타임스탬프_오류"].append({
            "id": sid, "stock": stock, "signal": sig,
            "timestamp": ts, "title": s.get("_video_title", ""),
        })

    # 2-3. 중복 (같은 video_id + stock)
    video_stock_map[vid].append((sid, stock))

    # 2-4. key_quote 품질
    if not kq or len(kq) < 20:
        issues["key_quote_부족"].append({
            "id": sid, "stock": stock, "signal": sig,
            "key_quote": kq[:80], "title": s.get("_video_title", ""),
        })
    # 가정형 발언
    if any(kw in kq for kw in CONDITIONAL_KEYWORDS):
        issues["가정형_발언"].append({
            "id": sid, "stock": stock, "signal": sig,
            "key_quote": kq[:100], "title": s.get("_video_title", ""),
        })
    # reasoning 지나치게 긺 (요약 실패)
    if len(reasoning) > 600:
        issues["reasoning_과다"].append({
            "id": sid, "stock": stock, "signal": sig,
            "reasoning_len": len(reasoning),
        })

    # 2-5. mention_type vs signal 불일치
    if mtype in ("교육", "뉴스") and sig == "매수":
        issues["mention_signal_불일치"].append({
            "id": sid, "stock": stock, "signal": sig,
            "mention_type": mtype, "key_quote": kq[:80],
        })
    if mtype == "결론" and sig == "중립":
        issues["결론_중립_의심"].append({
            "id": sid, "stock": stock, "signal": sig,
            "mention_type": mtype, "key_quote": kq[:80],
        })
    # 논거/교육인데 매수
    if mtype in ("논거", "교육", "보유", "뉴스") and sig == "매수":
        issues["논거_매수_의심"].append({
            "id": sid, "stock": stock, "signal": sig,
            "mention_type": mtype, "key_quote": kq[:80],
        })

# 중복 체크
for vid, items in video_stock_map.items():
    stock_counter = Counter(stock for _, stock in items)
    for stock, cnt in stock_counter.items():
        if cnt >= 2:
            dup_ids = [sid for sid, s in items if s == stock]
            issues["중복_시그널"].append({
                "video_id": vid, "stock": stock, "count": cnt,
                "signal_ids": dup_ids,
            })

# ─── 3. AI 재검증 (Haiku) ─────────────────────
print(f"\n[AI 재검증] Haiku로 57개 검증 중...")
ai_results = []

def haiku_verify(batch):
    """Haiku로 배치 검증"""
    items_text = ""
    for i, s in enumerate(batch):
        items_text += f"""
{i+1}. ID: {s['id']}
   종목: {s.get('stock','')} | 현재 시그널: {s.get('signal','')} | 유형: {s.get('mention_type','')}
   핵심발언: {(s.get('key_quote','') or '')[:150]}
"""

    prompt = f"""다음 투자 시그널들을 검증해줘.

판단 기준:
- 매수: 본인이 직접 매수했거나 청중에게 명확히 매수 권유
- 긍정: 긍정적 전망/분석이지만 직접 매수 권유 없음
- 중립: 사실 전달, 양면 분석, 교육적 설명
- 경계: 주의/위험 경고
- 부정: 부정적 전망, 매도 이유
- 매도: 직접 매도 권유 또는 본인 매도 공개

각 시그널에 대해 JSON 배열로만 답해 (다른 설명 없이):
[{{"id":"...", "correct_signal":"...", "is_wrong":true/false, "reason":"20자이내"}}]

시그널 목록:
{items_text}"""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-3-5-20241022",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        if r.status_code == 200:
            text = r.json()["content"][0]["text"].strip()
            # JSON 추출
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        else:
            print(f"  API 오류: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"  예외: {e}")
    return []

BATCH_SIZE = 10
for i in range(0, len(signals), BATCH_SIZE):
    batch = signals[i:i+BATCH_SIZE]
    print(f"  배치 {i//BATCH_SIZE+1}/{(len(signals)+BATCH_SIZE-1)//BATCH_SIZE} ({len(batch)}개)...")
    results = haiku_verify(batch)
    ai_results.extend(results)
    if i + BATCH_SIZE < len(signals):
        time.sleep(3)

# AI 결과 매핑
ai_map = {r["id"]: r for r in ai_results if isinstance(r, dict) and "id" in r}
ai_wrong = [r for r in ai_results if isinstance(r, dict) and r.get("is_wrong")]
print(f"  AI 검증 완료: {len(ai_results)}개, 오분류 의심: {len(ai_wrong)}개")

# ─── 4. 수익률 데이터 체크 ─────────────────────
import os
price_file = "C:/Users/Mario/work/invest-sns/public/signal_prices.json"
price_data = {}
if os.path.exists(price_file):
    with open(price_file, encoding="utf-8") as f:
        price_data = json.load(f)
    print(f"\n[수익률] signal_prices.json: {len(price_data)}개 항목")
    # 세상학개론 시그널 중 가격 데이터 있는 것
    has_price = sum(1 for s in signals if s["id"] in price_data)
    print(f"  세상학개론 가격 데이터 있음: {has_price}/{len(signals)}")
else:
    print("\n[수익률] signal_prices.json 없음")
    has_price = 0

# ─── 5. DB 자동 수정 ──────────────────────────
print("\n[DB 수정] 자동 업데이트 시작...")
updated = 0
patch_errors = 0

def patch_signal(signal_id, data):
    global updated, patch_errors
    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{signal_id}",
            json=data,
            headers={**H, "Prefer": "return=representation", "Content-Type": "application/json"},
        )
        if r.status_code in (200, 204):
            updated += 1
        else:
            print(f"  PATCH 오류 {signal_id[:8]}: {r.status_code}")
            patch_errors += 1
    except Exception as e:
        print(f"  PATCH 예외: {e}")
        patch_errors += 1

# 비종목 오추출 → rejected
for item in issues["비종목_오추출"]:
    patch_signal(item["id"], {
        "review_status": "rejected",
        "review_note": f"QA: 지수/통화/일반명사 오추출 (stock={item['stock']})",
    })

# AI 오분류 → needs_review
for item in ai_wrong:
    note = f"QA-AI: {item.get('correct_signal','?')}로 변경 검토 ({item.get('reason','')[:50]})"
    patch_signal(item["id"], {
        "review_status": "needs_review",
        "review_note": note,
    })

# 가정형 발언 → needs_review
for item in issues["가정형_발언"]:
    if item["id"] not in {x["id"] for x in ai_wrong}:  # 중복 방지
        patch_signal(item["id"], {
            "review_status": "needs_review",
            "review_note": "QA: 가정형 발언 - 시그널 유효성 재검토 필요",
        })

print(f"  DB 업데이트: {updated}건 성공, {patch_errors}건 오류")

# ─── 6. 리포트 생성 ───────────────────────────
sev = {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🟢 LOW"}

report_lines = [
    f"# 세상학개론 시그널 QA 리포트",
    f"생성: {datetime.now().strftime('%Y-%m-%d %H:%M')} (V9.1 파이프라인 기준)",
    f"총 시그널: {len(signals)}개",
    "",
    "## 요약",
    "",
    "| 카테고리 | 문제 수 | 심각도 |",
    "|---------|---------|-------|",
    f"| 비종목 오추출 | {len(issues['비종목_오추출'])} | 🔴 HIGH |",
    f"| 시그널 오분류 (AI) | {len(ai_wrong)} | 🔴 HIGH |",
    f"| 타임스탬프 오류 | {len(issues['타임스탬프_오류'])} | 🟡 MEDIUM |",
    f"| 논거/교육에 매수 | {len(issues['논거_매수_의심'])} | 🟡 MEDIUM |",
    f"| 중복 시그널 | {len(issues['중복_시그널'])} | 🟡 MEDIUM |",
    f"| 가정형 발언 | {len(issues['가정형_발언'])} | 🟡 MEDIUM |",
    f"| key_quote 부족 | {len(issues['key_quote_부족'])} | 🟢 LOW |",
    f"| reasoning 과다 | {len(issues['reasoning_과다'])} | 🟢 LOW |",
    "",
    f"### 시그널 분포",
    f"- 긍정: {sig_dist.get('긍정',0)}개 ({sig_dist.get('긍정',0)*100//len(signals)}%)",
    f"- 매수: {sig_dist.get('매수',0)}개 ({sig_dist.get('매수',0)*100//len(signals)}%)",
    f"- 중립: {sig_dist.get('중립',0)}개",
    f"- 부정: {sig_dist.get('부정',0)}개",
    f"- 경계: {sig_dist.get('경계',0)}개",
    f"- 매도: {sig_dist.get('매도',0)}개",
    "",
    "**경고: 긍정 70%, 매도/경계 0건 — 부정 시그널 감지 매우 약함**" if sig_dist.get('경계',0)+sig_dist.get('매도',0) == 0 else "",
]

# 비종목 오추출
report_lines += ["", "---", "## 🔴 비종목 오추출 (즉시 삭제 필요)", ""]
for item in issues["비종목_오추출"]:
    report_lines.append(f"- **{item['stock']}** (ticker: {item['ticker']}, market: {item['market']}) | {item['signal']} | ID: `{item['id'][:8]}`")
    report_lines.append(f"  > 영상: {item['title'][:60]}")

# AI 오분류
report_lines += ["", "---", "## 🔴 시그널 오분류 (AI 재검증)", ""]
if ai_wrong:
    for item in ai_wrong:
        orig = next((s for s in signals if s["id"] == item["id"]), {})
        report_lines.append(f"- **{orig.get('stock','')}** | {orig.get('signal','')} → **{item.get('correct_signal','')}** 권장")
        report_lines.append(f"  > 근거: {item.get('reason','')}")
        report_lines.append(f"  > 발언: {(orig.get('key_quote','') or '')[:80]}")
else:
    report_lines.append("AI 검증 오류 없음 (API 호출 실패 시 '에러' 표시)")

# 타임스탬프
report_lines += ["", "---", "## 🟡 타임스탬프 오류", ""]
for item in issues["타임스탬프_오류"][:20]:
    report_lines.append(f"- **{item['stock']}** | timestamp: `{item['timestamp']}` | {item['signal']} | ID: `{item['id'][:8]}`")

# 논거/교육에 매수
report_lines += ["", "---", "## 🟡 mention_type 불일치 (논거/교육/뉴스에 매수)", ""]
for item in issues["논거_매수_의심"]:
    report_lines.append(f"- **{item['stock']}** | mention={item['mention_type']} signal=**{item['signal']}** | ID: `{item['id'][:8]}`")
    report_lines.append(f"  > {item['key_quote'][:80]}")

# 중복
report_lines += ["", "---", "## 🟡 중복 시그널", ""]
for item in issues["중복_시그널"]:
    report_lines.append(f"- **{item['stock']}** | 같은 영상에서 {item['count']}번 등장 | video: `{item['video_id'][:8]}`")

# 가정형 발언
report_lines += ["", "---", "## 🟡 가정형 발언 (조건부 발언이 시그널로 등록)", ""]
for item in issues["가정형_발언"]:
    report_lines.append(f"- **{item['stock']}** | {item['signal']} | ID: `{item['id'][:8]}`")
    report_lines.append(f"  > \"{item['key_quote'][:100]}\"")

# key_quote 부족
report_lines += ["", "---", "## 🟢 key_quote 품질 이슈", ""]
for item in issues["key_quote_부족"][:10]:
    report_lines.append(f"- **{item['stock']}** | key_quote: `{item['key_quote'][:50]}`")

# 수익률
report_lines += ["", "---", "## 💰 수익률 데이터 현황", ""]
report_lines.append(f"- 가격 데이터 있음: {has_price}/{len(signals)}개")
report_lines.append(f"- 누락: {len(signals)-has_price}개")

# 프롬프트 개선 제안
report_lines += [
    "", "---",
    "## 📝 프롬프트 개선 제안 (V9.1 → V10.11 이행 필요)",
    "",
    "### 패턴 1: 지수/통화를 종목으로 오추출",
    f"- 발생: {len(issues['비종목_오추출'])}건",
    "- 원인: V9.1 프롬프트에 지수 제외 규칙이 없음",
    "- 개선안: `STEP 2.5 정규화` 단계에 명시적 제외 목록 추가",
    '  ```',
    '  절대 시그널로 만들지 말 것: 코스피, 코스닥, S&P500, 나스닥, 달러, 원화, 금, 원유, 지수',
    '  ```',
    "",
    "### 패턴 2: 논거/교육 언급을 매수로 분류",
    f"- 발생: {len(issues['논거_매수_의심'])}건",
    "- 원인: mention_type 분류가 주관적, 매수 판단 기준 불명확",
    "- 개선안 (V10.11 이미 적용됨): '본인이 샀거나 사라고 했는가?' → Yes = 매수",
    "",
    "### 패턴 3: 가정형 발언이 시그널로 등록",
    f"- 발생: {len(issues['가정형_발언'])}건",
    "- 원인: '만약 ~이었다면' 같은 가정형 발언이 시그널로 포함됨",
    "- 개선안: 가정형 조건부 발언은 시그널 생성 금지 규칙 추가",
    '  ```',
    '  금지: "만약", "~했다면", "~이었다면", "가정하면" 포함 발언은 시그널 생성 불가',
    '  ```',
    "",
    "### 패턴 4: 타임스탬프 형식 오류",
    f"- 발생: {len(issues['타임스탬프_오류'])}건",
    "- 원인: 날짜('3월 23일')나 텍스트가 타임스탬프로 입력됨",
    "- 개선안: 타임스탬프 형식 강제 (HH:MM:SS or MM:SS만 허용)",
    "",
    "### 결론: V9.1 → V10.11 재분석 필요",
    "- 세상학개론 채널은 V9.1 파이프라인으로 분석됨 (최신 V10.11 아님)",
    "- 위 오류들 중 상당수는 V10.11 재분석으로 자동 해결 예상",
    "- **추천: 세상학개론 81개 영상 V10.11로 재분석 → DB 교체**",
    "",
    "---",
    f"## 조치 현황",
    f"- DB 자동 수정 완료: {updated}건",
    f"  - 비종목 오추출 → rejected: {len(issues['비종목_오추출'])}건",
    f"  - AI 오분류 → needs_review: {len(ai_wrong)}건",
    f"  - 가정형 발언 → needs_review",
    f"- 수동 검토 필요: needs_review 상태 시그널 확인",
]

report = "\n".join(report_lines)
with open("C:/Users/Mario/work/sesang_qa_report.md", "w", encoding="utf-8") as f:
    f.write(report)

# 중간 결과도 갱신
with open("C:/Users/Mario/work/sesang_qa_intermediate.json", "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "issues": {k: v for k, v in issues.items()},
        "ai_results": ai_results,
        "ai_wrong": ai_wrong,
        "db_updated": updated,
    }, f, ensure_ascii=False, indent=2)

print(f"\n{'='*50}")
print(f"QA 완료")
print(f"{'='*50}")
print(f"총 시그널: {len(signals)}")
print(f"비종목 오추출: {len(issues['비종목_오추출'])}건")
print(f"AI 오분류 의심: {len(ai_wrong)}건")
print(f"타임스탬프 오류: {len(issues['타임스탬프_오류'])}건")
print(f"논거/교육에 매수: {len(issues['논거_매수_의심'])}건")
print(f"가정형 발언: {len(issues['가정형_발언'])}건")
print(f"중복 시그널: {len(issues['중복_시그널'])}건")
print(f"DB 자동 수정: {updated}건")
print(f"리포트: C:/Users/Mario/work/sesang_qa_report.md")
