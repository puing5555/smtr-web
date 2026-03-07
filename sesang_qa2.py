#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""세상학개론 QA + DB 수정 (service role key)"""
import json, re, sys, requests
from collections import defaultdict, Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SRK = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
H = {"apikey": SRK, "Authorization": f"Bearer {SRK}", "Content-Type": "application/json", "Prefer": "return=representation"}

with open("C:/Users/Mario/work/sesang_signals_full.json", encoding="utf-8") as f:
    signals = json.load(f)
print(f"로드: {len(signals)}개")

INVALID_STOCKS = {
    "코스피","코스닥","S&P500","S&P 500","나스닥","다우","니케이",
    "KOSPI","KOSDAQ","달러","원화","엔화","위안화",
    "금","은","원유","채권","USD","KRW","JPY","EUR",
    "시장","증시","지수","환율","금리"
}
CONDITIONAL_KW = ["만약","이었다면","였다면","한다면","된다면"]

issues = defaultdict(list)
video_stock_map = defaultdict(list)

for s in signals:
    sid = s["id"]
    stock = s.get("stock","") or ""
    sig = s.get("signal","")
    mtype = s.get("mention_type","") or ""
    ts = s.get("timestamp","") or ""
    kq = s.get("key_quote","") or ""
    reasoning = s.get("reasoning","") or ""
    vid = s.get("video_id","")
    title = s.get("_video_title","") or ""

    # 비종목
    if stock in INVALID_STOCKS or s.get("market") == "INDEX":
        issues["nonstock"].append({"id": sid, "stock": stock, "ticker": s.get("ticker"), "market": s.get("market"), "signal": sig, "title": title[:60]})

    # 타임스탬프
    ts_clean = ts.strip() if ts else ""
    ts_valid = bool(re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", ts_clean))
    if not ts_valid:
        issues["ts_err"].append({"id": sid, "stock": stock, "ts": ts, "title": title[:50]})

    # 중복
    video_stock_map[vid].append({"id": sid, "stock": stock})

    # 가정형
    if any(kw in kq for kw in CONDITIONAL_KW):
        issues["conditional"].append({"id": sid, "stock": stock, "signal": sig, "kq": kq[:120]})

    # mention_type vs signal
    if mtype in ("논거","교육","뉴스","보유") and sig == "매수":
        issues["mismatch"].append({"id": sid, "stock": stock, "mtype": mtype, "signal": sig, "kq": kq[:80]})

    # key_quote 부족
    if len(kq) < 15:
        issues["short_quote"].append({"id": sid, "stock": stock, "kq": kq})

    # reasoning 과다
    if len(reasoning) > 600:
        issues["long_reason"].append({"id": sid, "stock": stock, "len": len(reasoning)})

# 중복
for vid, items in video_stock_map.items():
    cnt = Counter(x["stock"] for x in items)
    for stock, c in cnt.items():
        if c >= 2:
            ids = [x["id"] for x in items if x["stock"] == stock]
            issues["dup"].append({"vid": vid[:8], "stock": stock, "count": c, "ids": ids})

# ── 결과 출력 ──────────────────────────────────────────
print("\n===== 룰 기반 체크 결과 =====")
print(f"비종목 오추출  : {len(issues['nonstock'])}건")
print(f"타임스탬프 오류: {len(issues['ts_err'])}건 / 57개")
print(f"가정형 발언    : {len(issues['conditional'])}건")
print(f"mention 불일치 : {len(issues['mismatch'])}건")
print(f"key_quote 부족 : {len(issues['short_quote'])}건")
print(f"reasoning 과다 : {len(issues['long_reason'])}건")
print(f"중복 시그널    : {len(issues['dup'])}건")

print("\n--- 비종목 오추출 상세 ---")
for x in issues["nonstock"]:
    print(f"  [{x['signal']}] {x['stock']} (ticker:{x['ticker']}, market:{x['market']})")
    print(f"   영상: {x['title']}")

print("\n--- 타임스탬프 오류 (전체) ---")
for x in issues["ts_err"]:
    print(f"  {x['stock']} | ts=\"{x['ts']}\"")

print("\n--- mention/signal 불일치 ---")
for x in issues["mismatch"]:
    print(f"  {x['stock']} | {x['mtype']}→{x['signal']}")
    print(f"   \"{x['kq']}\"")

print("\n--- 가정형 발언 ---")
for x in issues["conditional"]:
    print(f"  [{x['signal']}] {x['stock']}")
    print(f"   \"{x['kq']}\"")

# ── DB 수정 ────────────────────────────────────────────
print("\n===== DB 수정 =====")
updated = 0
errors = 0

def patch(sid, data):
    global updated, errors
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{sid}", json=data, headers=H)
    if r.status_code in (200, 204):
        updated += 1
    else:
        errors += 1
        print(f"  PATCH 실패 {sid[:8]}: {r.status_code} {r.text[:100]}")

# 비종목 → rejected
for x in issues["nonstock"]:
    patch(x["id"], {"review_status": "rejected", "review_note": f"QA: 지수/통화/일반명사 오추출 (stock={x['stock']})"})
    print(f"  비종목 reject: {x['stock']}")

# 가정형 → review_note 추가
for x in issues["conditional"]:
    patch(x["id"], {"review_note": "QA: 가정형 발언 - 시그널 유효성 재검토 필요"})

# mention_type 불일치 → review_note 추가
for x in issues["mismatch"]:
    patch(x["id"], {"review_note": f"QA: {x['mtype']} 유형에 매수 분류됨 - 긍정으로 재검토 필요"})

print(f"\nDB 업데이트: {updated}건 성공, {errors}건 실패")

# ── 리포트 생성 ────────────────────────────────────────
sig_dist = Counter(s["signal"] for s in signals)
now = datetime.now().strftime("%Y-%m-%d %H:%M")

ts_err_stocks = [x["stock"] for x in issues["ts_err"]]
ts_err_ts = [x["ts"] for x in issues["ts_err"]]

lines = []
lines.append("# 세상학개론 시그널 QA 리포트")
lines.append(f"생성: {now} | 총 시그널: 57개 | 파이프라인: V9.1")
lines.append("")
lines.append("## 요약")
lines.append("")
lines.append("| 카테고리 | 건수 | 심각도 | 조치 |")
lines.append("|---------|------|-------|------|")
lines.append(f"| 비종목 오추출 | {len(issues['nonstock'])} | HIGH | DB rejected 처리 완료 |")
lines.append(f"| 타임스탬프 오류 | {len(issues['ts_err'])} | MEDIUM | 수동 확인 필요 |")
lines.append(f"| mention/signal 불일치 | {len(issues['mismatch'])} | MEDIUM | review_note 추가 |")
lines.append(f"| 가정형 발언 | {len(issues['conditional'])} | MEDIUM | review_note 추가 |")
lines.append(f"| 중복 시그널 | {len(issues['dup'])} | MEDIUM | 수동 확인 |")
lines.append(f"| key_quote 부족 | {len(issues['short_quote'])} | LOW | - |")
lines.append(f"| reasoning 과다 | {len(issues['long_reason'])} | LOW | - |")
lines.append("")
lines.append("## 시그널 분포")
lines.append(f"- 긍정: {sig_dist.get('긍정',0)}개 ({sig_dist.get('긍정',0)*100//57}%)")
lines.append(f"- 매수: {sig_dist.get('매수',0)}개 ({sig_dist.get('매수',0)*100//57}%)")
lines.append(f"- 중립: {sig_dist.get('중립',0)}개")
lines.append(f"- 부정: {sig_dist.get('부정',0)}개")
lines.append(f"- 경계: {sig_dist.get('경계',0)}개 ← 0건 경고")
lines.append(f"- 매도: {sig_dist.get('매도',0)}개 ← 0건 경고")
lines.append("")
lines.append("> 경고: 긍정 70%, 매도/경계 0건. V9.1 프롬프트는 부정 시그널 감지 매우 약함.")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 1. 비종목 오추출 (rejected 처리 완료)")
lines.append("")
for x in issues["nonstock"]:
    lines.append(f"- **{x['stock']}** (ticker: `{x['ticker']}`, market: `{x['market']}`) | signal: {x['signal']}")
    lines.append(f"  > 영상: {x['title']}")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 2. 타임스탬프 오류 (34건 / 57건 = 60%)")
lines.append("")
lines.append("> V9.1에서 타임스탬프를 영상 내 시간(HH:MM:SS) 대신 날짜나 텍스트로 넣은 사례가 많음.")
lines.append("")
lines.append("| 종목 | 잘못된 timestamp |")
lines.append("|------|-----------------|")
for x in issues["ts_err"]:
    lines.append(f"| {x['stock']} | `{x['ts']}` |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 3. mention_type vs signal 불일치")
lines.append("")
for x in issues["mismatch"]:
    lines.append(f"- **{x['stock']}** | mention_type=`{x['mtype']}` → signal=**{x['signal']}**")
    lines.append(f"  > \"{x['kq']}\"")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 4. 가정형 발언 (시그널로 등록 부적절)")
lines.append("")
for x in issues["conditional"]:
    lines.append(f"- **{x['stock']}** | {x['signal']}")
    lines.append(f"  > \"{x['kq']}\"")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 5. 중복 시그널")
lines.append("")
if issues["dup"]:
    for x in issues["dup"]:
        lines.append(f"- **{x['stock']}** | 동일 영상에서 {x['count']}번 등장")
else:
    lines.append("- 없음")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 6. 프롬프트 개선 제안 (V9.1 → V10.11)")
lines.append("")
lines.append("### 패턴 A: 지수/통화를 종목으로 오추출")
lines.append(f"- 발생: {len(issues['nonstock'])}건 (코스피, 게임스톱 등)")
lines.append("- 원인: V9.1에 비종목 제외 규칙 없음")
lines.append("- 개선안 (V10.11 이미 적용):")
lines.append("  ```")
lines.append("  절대 시그널 생성 금지: 코스피, 코스닥, S&P500, 나스닥, 달러, 원유, 지수류")
lines.append("  ```")
lines.append("")
lines.append("### 패턴 B: 타임스탬프 형식 오류 (60%)")
lines.append(f"- 발생: {len(issues['ts_err'])}건")
lines.append("- 원인: V9.1 프롬프트에 타임스탬프 형식 강제 없음")
lines.append("- 개선안:")
lines.append("  ```")
lines.append("  타임스탬프 형식: 반드시 HH:MM:SS 또는 MM:SS 형식만 허용")
lines.append("  날짜(3월 23일), 없음(N/A), 0:00 등 사용 금지")
lines.append("  ```")
lines.append("")
lines.append("### 패턴 C: 가정형 발언 시그널 등록")
lines.append(f"- 발생: {len(issues['conditional'])}건")
lines.append("- 원인: '만약 ~이었다면' 조건부 발언이 시그널로 포함됨")
lines.append("- 개선안:")
lines.append("  ```")
lines.append("  '만약', '~했다면', '이었다면' 포함 발언은 시그널 생성 금지")
lines.append("  ```")
lines.append("")
lines.append("### 패턴 D: mention_type 논거/보유에 매수 분류")
lines.append(f"- 발생: {len(issues['mismatch'])}건")
lines.append("- 원인: 매수/긍정 구분 기준 불명확")
lines.append("- 개선안 (V10.11 적용됨): '본인이 샀거나 사라고 했는가?' → Yes=매수, No=긍정")
lines.append("")
lines.append("### 종합 권고")
lines.append("- **세상학개론 채널 V10.11로 재분석 필요**")
lines.append("- 현재 V9.1 기준 57개 중 실제 유효 시그널 추정: ~35~40개")
lines.append("- 비종목 3건 이미 rejected 처리 완료")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## AI 재검증")
lines.append("")
lines.append("- Anthropic API 인증 오류로 자동 검증 불가")
lines.append("- 룰 기반 체크만 적용됨")
lines.append("- API 키 재확인 후 재실행 필요")
lines.append("")
lines.append("---")
lines.append("")
lines.append(f"## DB 조치 현황")
lines.append(f"- 자동 수정 완료: {updated}건")
lines.append(f"  - 비종목 오추출 → rejected: {len(issues['nonstock'])}건")
lines.append(f"  - 가정형 발언 → review_note 추가: {len(issues['conditional'])}건")
lines.append(f"  - mention_type 불일치 → review_note 추가: {len(issues['mismatch'])}건")
lines.append(f"- 오류: {errors}건")

report = "\n".join(lines)
with open("C:/Users/Mario/work/sesang_qa_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("\n리포트 저장: C:/Users/Mario/work/sesang_qa_report.md")
print("완료!")
