#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 시그널 57개 전수 QA 감사 스크립트
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import re
import time
import os
import sys
import requests
from datetime import datetime
from collections import defaultdict

# === 설정 ===
ANTHROPIC_API_KEY = "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"
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
DATA_FILE = r"C:\Users\Mario\work\sesang_signals_full.json"
PRICES_FILE = r"C:\Users\Mario\work\invest-sns\public\signal_prices.json"
REPORT_FILE = r"C:\Users\Mario\work\sesang_qa_report.md"
INTERMEDIATE_FILE = r"C:\Users\Mario\work\sesang_qa_intermediate.json"

INVALID_STOCKS = [
    '코스피', '코스닥', 'S&P500', 'S&P', '나스닥', '다우', '니케이', 'KOSPI', 'KOSDAQ',
    '달러', '원화', '엔화', '금', '원유', '채권', 'USD', 'KRW', '시장', '증시'
]

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ========== STEP 1: 데이터 로드 ==========
print("=" * 60)
print("STEP 1: 데이터 로드")
print("=" * 60)

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    signals = json.load(f)

print(f"총 시그널: {len(signals)}개")

signal_dist = defaultdict(int)
mention_dist = defaultdict(int)
for s in signals:
    signal_dist[s.get('signal', 'N/A')] += 1
    mention_dist[s.get('mention_type', 'N/A')] += 1

print("\n시그널 분포:")
for k, v in sorted(signal_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}개")

print("\nMention Type 분포:")
for k, v in sorted(mention_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}개")


# ========== STEP 2: 룰 기반 체크 ==========
print("\n" + "=" * 60)
print("STEP 2: 룰 기반 체크")
print("=" * 60)

# 2-1. 비종목 오추출
print("\n[2-1] 비종목 오추출 체크")
invalid_stock_signals = []
for s in signals:
    stock = s.get('stock', '')
    for inv in INVALID_STOCKS:
        if stock.strip() == inv or stock.strip().upper() == inv.upper():
            invalid_stock_signals.append(s)
            break
        # 부분 포함도 체크
        if inv.lower() in stock.lower() and len(stock) <= len(inv) + 5:
            invalid_stock_signals.append(s)
            break

# 중복 제거
seen_ids = set()
deduped = []
for s in invalid_stock_signals:
    if s['id'] not in seen_ids:
        seen_ids.add(s['id'])
        deduped.append(s)
invalid_stock_signals = deduped

print(f"비종목 오추출: {len(invalid_stock_signals)}개")
for s in invalid_stock_signals:
    print(f"  - ID:{s['id'][:8]}... | 종목:{s['stock']} | 시그널:{s['signal']} | TS:{s.get('timestamp')}")


# 2-2. 타임스탬프 유효성
print("\n[2-2] 타임스탬프 유효성 체크")
TS_VALID_PATTERN = re.compile(r'^\d{1,2}:\d{2}(:\d{2})?$')

invalid_ts_signals = []
for s in signals:
    ts = s.get('timestamp')
    if ts is None or ts == '' or ts == 'N/A':
        invalid_ts_signals.append({'signal': s, 'reason': f'NULL/빈값/N/A: {repr(ts)}'})
    elif not TS_VALID_PATTERN.match(str(ts).strip()):
        invalid_ts_signals.append({'signal': s, 'reason': f'잘못된 형식: {ts}'})

print(f"무효 타임스탬프: {len(invalid_ts_signals)}개")
for item in invalid_ts_signals:
    s = item['signal']
    print(f"  - ID:{s['id'][:8]}... | 종목:{s['stock']} | 이유:{item['reason']}")


# 2-3. 중복 체크
print("\n[2-3] 중복 시그널 체크")
video_stock_map = defaultdict(list)
for s in signals:
    key = (s.get('video_id', ''), s.get('stock', ''))
    video_stock_map[key].append(s)

duplicate_signals = []
for key, items in video_stock_map.items():
    if len(items) >= 2:
        duplicate_signals.append({'video_id': key[0], 'stock': key[1], 'signals': items})

print(f"중복 시그널 그룹: {len(duplicate_signals)}개")
for dup in duplicate_signals:
    print(f"  - 비디오:{dup['video_id'][:8]}... | 종목:{dup['stock']} | 개수:{len(dup['signals'])}")
    for s in dup['signals']:
        print(f"      ID:{s['id'][:8]}... | 시그널:{s['signal']} | TS:{s.get('timestamp')}")


# 2-4. key_quote 품질
print("\n[2-4] key_quote 품질 체크")
quote_issues = []
CONDITIONAL_PATTERNS = ['만약', '조건부', '했다면', '이었다면', '됐다면', '된다면', '한다면']

for s in signals:
    kq = s.get('key_quote') or ''
    rs = s.get('reasoning') or ''
    issues = []
    
    if not kq or len(kq.strip()) == 0:
        issues.append('key_quote 없음')
    elif len(kq.strip()) < 50:
        issues.append(f'key_quote 짧음({len(kq.strip())}자)')
    
    if len(rs) >= 500:
        issues.append(f'reasoning 너무 길음({len(rs)}자)')
    
    for cp in CONDITIONAL_PATTERNS:
        if cp in kq:
            issues.append(f'가정형 표현("{cp}") 포함')
            break
    
    if issues:
        quote_issues.append({'signal': s, 'issues': issues})

print(f"key_quote 품질 이슈: {len(quote_issues)}개")
for item in quote_issues:
    s = item['signal']
    print(f"  - ID:{s['id'][:8]}... | 종목:{s['stock']} | 이슈:{', '.join(item['issues'])}")


# 2-5. mention_type 불일치
print("\n[2-5] mention_type vs signal 불일치 체크")
mismatch_signals = []
for s in signals:
    mt = s.get('mention_type', '')
    sig = s.get('signal', '')
    
    if mt in ['교육', '뉴스', '논거'] and sig == '매수':
        mismatch_signals.append({'signal': s, 'reason': f'mention_type={mt}인데 signal=매수'})
    elif mt == '결론' and sig == '중립':
        mismatch_signals.append({'signal': s, 'reason': f'mention_type=결론인데 signal=중립'})

print(f"mention_type 불일치: {len(mismatch_signals)}개")
for item in mismatch_signals:
    s = item['signal']
    print(f"  - ID:{s['id'][:8]}... | 종목:{s['stock']} | 이유:{item['reason']}")


# ========== STEP 3: AI 재검증 ==========
print("\n" + "=" * 60)
print("STEP 3: AI 재검증 (claude-haiku-3-5-20241022)")
print("=" * 60)

def call_haiku(signal_data, retry=0):
    """Haiku로 시그널 검증"""
    stock = signal_data.get('stock', '')
    sig = signal_data.get('signal', '')
    mt = signal_data.get('mention_type', '')
    kq = signal_data.get('key_quote') or ''
    rs = signal_data.get('reasoning') or ''
    
    prompt = f"""다음 투자 시그널을 검증해줘.

종목: {stock}
현재 시그널: {sig}
발언 유형: {mt}
핵심 발언: {kq}
분석 근거: {rs}

판단 기준:
- 매수: 본인 매수 또는 청중에게 직접 매수 권유
- 긍정: 긍정적 전망/분석, 매수 권유 없음
- 중립: 사실 전달, 양면 분석
- 경계: 주의/위험 경고
- 부정: 부정적 전망, 매도 이유
- 매도: 직접 매도 권유 또는 본인 매도

JSON으로만 답해:
{{"correct_signal": "매수/긍정/중립/경계/부정/매도", "is_wrong": true/false, "reason": "30자 이내"}}"""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-haiku-3-5-20241022",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 429:
            wait = 30 if retry < 3 else 60
            print(f"    429 에러, {wait}초 대기 후 재시도...")
            time.sleep(wait)
            return call_haiku(signal_data, retry + 1)
        
        resp.raise_for_status()
        content = resp.json()['content'][0]['text'].strip()
        
        # JSON 파싱
        # JSON 블록 추출
        json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {"correct_signal": sig, "is_wrong": False, "reason": "파싱 실패"}
            
    except Exception as e:
        if retry < 3:
            time.sleep(5)
            return call_haiku(signal_data, retry + 1)
        return {"correct_signal": sig, "is_wrong": False, "reason": f"에러: {str(e)[:20]}"}


ai_results = []
invalid_stock_ids = {s['id'] for s in invalid_stock_signals}

print(f"총 {len(signals)}개 시그널 AI 검증 시작...")

for i, sig_data in enumerate(signals):
    batch_num = i // 10
    pos_in_batch = i % 10
    
    print(f"  [{i+1:02d}/57] ID:{sig_data['id'][:8]}... | 종목:{sig_data['stock']} | 현재:{sig_data['signal']}", end='', flush=True)
    
    result = call_haiku(sig_data)
    ai_results.append({
        'id': sig_data['id'],
        'stock': sig_data['stock'],
        'current_signal': sig_data['signal'],
        'ai_result': result,
        'mention_type': sig_data.get('mention_type', ''),
        'key_quote': (sig_data.get('key_quote') or '')[:80]
    })
    
    is_wrong = result.get('is_wrong', False)
    correct = result.get('correct_signal', sig_data['signal'])
    reason = result.get('reason', '')
    
    if is_wrong:
        print(f" → ❌ {correct} ({reason})")
    else:
        print(f" → ✅ OK")
    
    # 배치 간 대기
    if pos_in_batch == 9 and i < len(signals) - 1:
        print(f"  --- 배치 {batch_num+1} 완료, 5초 대기 ---")
        time.sleep(5)
    else:
        time.sleep(1)

# 중간 결과 저장
intermediate = {
    'timestamp': datetime.now().isoformat(),
    'total_signals': len(signals),
    'invalid_stocks': [{'id': s['id'], 'stock': s['stock']} for s in invalid_stock_signals],
    'invalid_timestamps': [{'id': i['signal']['id'], 'stock': i['signal']['stock'], 'ts': i['signal'].get('timestamp'), 'reason': i['reason']} for i in invalid_ts_signals],
    'duplicates': [{'video_id': d['video_id'], 'stock': d['stock'], 'count': len(d['signals'])} for d in duplicate_signals],
    'quote_issues': [{'id': qi['signal']['id'], 'stock': qi['signal']['stock'], 'issues': qi['issues']} for qi in quote_issues],
    'mismatch': [{'id': m['signal']['id'], 'stock': m['signal']['stock'], 'reason': m['reason']} for m in mismatch_signals],
    'ai_results': ai_results
}

with open(INTERMEDIATE_FILE, 'w', encoding='utf-8') as f:
    json.dump(intermediate, f, ensure_ascii=False, indent=2)
print(f"\n중간 결과 저장: {INTERMEDIATE_FILE}")


# ========== STEP 4: 수익률 데이터 체크 ==========
print("\n" + "=" * 60)
print("STEP 4: 수익률 데이터 체크")
print("=" * 60)

prices_data = {}
prices_available = 0
prices_missing = 0

if os.path.exists(PRICES_FILE):
    with open(PRICES_FILE, 'r', encoding='utf-8') as f:
        prices_data = json.load(f)
    print(f"signal_prices.json 로드 성공: {len(prices_data)}개 항목")
    
    for s in signals:
        sid = s['id']
        if sid in prices_data:
            prices_available += 1
        else:
            prices_missing += 1
    
    print(f"가격 데이터 있음: {prices_available}개")
    print(f"가격 데이터 없음: {prices_missing}개")
else:
    print(f"signal_prices.json 없음: {PRICES_FILE}")
    prices_missing = len(signals)
    print(f"가격 데이터 없음: {prices_missing}개 (전체)")


# ========== STEP 5: 리포트 생성 ==========
print("\n" + "=" * 60)
print("STEP 5: 리포트 생성")
print("=" * 60)

ai_wrong = [r for r in ai_results if r['ai_result'].get('is_wrong', False)]
ai_wrong_ids = {r['id'] for r in ai_wrong}

# 정상 시그널 = 어떤 문제도 없는 것
all_problem_ids = set()
all_problem_ids.update(s['id'] for s in invalid_stock_signals)
all_problem_ids.update(i['signal']['id'] for i in invalid_ts_signals)
all_problem_ids.update(r['id'] for r in ai_wrong)
all_problem_ids.update(i['signal']['id'] for i in quote_issues)
all_problem_ids.update(m['signal']['id'] for m in mismatch_signals)
for dup in duplicate_signals:
    for s in dup['signals']:
        all_problem_ids.add(s['id'])

normal_count = len(signals) - len(all_problem_ids)

now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

report_lines = [
    f"# 세상학개론 시그널 QA 리포트",
    f"생성: {now_str}",
    f"총 시그널: {len(signals)}개",
    f"",
    f"## 📊 요약",
    f"",
    f"| 카테고리 | 문제 수 | 심각도 |",
    f"|---------|---------|-------|",
    f"| 비종목 오추출 | {len(invalid_stock_signals)} | 🔴 HIGH |",
    f"| 타임스탬프 오류 | {len(invalid_ts_signals)} | 🟡 MEDIUM |",
    f"| 시그널 오분류 (AI 검증) | {len(ai_wrong)} | 🔴 HIGH |",
    f"| 중복 시그널 | {sum(len(d['signals']) for d in duplicate_signals)} | 🟡 MEDIUM |",
    f"| key_quote 품질 | {len(quote_issues)} | 🟢 LOW |",
    f"| mention_type 불일치 | {len(mismatch_signals)} | 🟡 MEDIUM |",
    f"",
]

# 비종목 오추출 섹션
report_lines.append("## 🔴 비종목 오추출 (즉시 삭제 필요)")
report_lines.append("")
if invalid_stock_signals:
    for s in invalid_stock_signals:
        vt = s.get('_video_title', '')[:40]
        report_lines.append(f"- **{s['stock']}** | ID: `{s['id'][:16]}...` | 시그널: {s['signal']} | 영상: {vt}")
        report_lines.append(f"  - 타임스탬프: {s.get('timestamp')} | ticker: {s.get('ticker')} | market: {s.get('market')}")
else:
    report_lines.append("없음")
report_lines.append("")

# AI 검증 오분류 섹션
report_lines.append("## 🔴 시그널 오분류 (AI 검증 결과)")
report_lines.append("")
if ai_wrong:
    for r in ai_wrong:
        current = r['current_signal']
        correct = r['ai_result'].get('correct_signal', current)
        reason = r['ai_result'].get('reason', '')
        mt = r['mention_type']
        kq_short = r['key_quote'][:60] if r['key_quote'] else ''
        report_lines.append(f"- **{r['stock']}** | ID: `{r['id'][:16]}...` | {current} → **{correct}**")
        report_lines.append(f"  - 이유: {reason} | mention_type: {mt}")
        report_lines.append(f"  - 핵심발언: {kq_short}...")
else:
    report_lines.append("없음")
report_lines.append("")

# 타임스탬프 오류 섹션
report_lines.append("## 🟡 타임스탬프 오류")
report_lines.append("")
if invalid_ts_signals:
    for item in invalid_ts_signals:
        s = item['signal']
        report_lines.append(f"- **{s['stock']}** | ID: `{s['id'][:16]}...` | {item['reason']}")
else:
    report_lines.append("없음")
report_lines.append("")

# 중복 시그널 섹션
report_lines.append("## 🟡 중복 시그널")
report_lines.append("")
if duplicate_signals:
    for dup in duplicate_signals:
        vt = dup['signals'][0].get('_video_title', '')[:40]
        report_lines.append(f"- **{dup['stock']}** | 비디오: `{dup['video_id'][:16]}...` | {len(dup['signals'])}개 중복")
        report_lines.append(f"  - 영상: {vt}")
        for s in dup['signals']:
            report_lines.append(f"  - ID: `{s['id'][:16]}...` | {s['signal']} | TS: {s.get('timestamp')}")
else:
    report_lines.append("없음")
report_lines.append("")

# key_quote 품질 섹션
report_lines.append("## 🟢 key_quote 품질 이슈")
report_lines.append("")
if quote_issues:
    for item in quote_issues:
        s = item['signal']
        kq_short = (s.get('key_quote') or '')[:60]
        report_lines.append(f"- **{s['stock']}** | ID: `{s['id'][:16]}...` | {', '.join(item['issues'])}")
        if kq_short:
            report_lines.append(f"  - 발언: {kq_short}...")
else:
    report_lines.append("없음")
report_lines.append("")

# mention_type 불일치 (추가)
report_lines.append("## 🟡 mention_type 불일치")
report_lines.append("")
if mismatch_signals:
    for item in mismatch_signals:
        s = item['signal']
        report_lines.append(f"- **{s['stock']}** | ID: `{s['id'][:16]}...` | {item['reason']}")
else:
    report_lines.append("없음")
report_lines.append("")

# 프롬프트 개선 제안
report_lines.extend([
    "## 🔍 프롬프트 개선 제안 (원인 분석)",
    "",
])

# 패턴 분석
patterns = []

# 패턴 1: 비종목 오추출
if invalid_stock_signals:
    patterns.append({
        'name': '지수/시장 지표 오추출',
        'count': len(invalid_stock_signals),
        'cause': 'V9.1 프롬프트가 "종목 언급"을 너무 광범위하게 정의해 코스피 등 지수도 추출',
        'fix': '프롬프트에 "지수(코스피, 코스닥, S&P500, 나스닥 등), 통화(달러, 엔화 등), 원자재(금, 원유)는 종목에서 제외"를 명시. INVALID_STOCKS 리스트를 시스템 프롬프트에 삽입.'
    })

# 패턴 2: 가정형 발언 추출
cond_count = sum(1 for qi in quote_issues if any('가정형' in i for i in qi['issues']))
if cond_count > 0:
    patterns.append({
        'name': '가정형/조건부 발언 오추출',
        'count': cond_count,
        'cause': 'V9.1 프롬프트가 "만약 ~했다면" 같은 가정형 발언도 실제 투자 신호로 추출',
        'fix': '프롬프트에 "가정형 발언(만약, ~했다면, 조건부)은 투자 시그널로 추출하지 마시오"를 추가. 확실성(certainty) 기준을 강화.'
    })

# 패턴 3: 긍정/매수 혼동
buy_wrong = [r for r in ai_wrong if r['current_signal'] == '매수' and r['ai_result'].get('correct_signal') in ['긍정', '중립']]
pos_wrong = [r for r in ai_wrong if r['current_signal'] == '긍정' and r['ai_result'].get('correct_signal') == '매수']
if buy_wrong or pos_wrong:
    patterns.append({
        'name': '매수/긍정 경계 불명확',
        'count': len(buy_wrong) + len(pos_wrong),
        'cause': 'V9.1 프롬프트에서 "매수"와 "긍정"의 차이가 명확하지 않아 분류 오류 발생',
        'fix': '"매수"는 반드시 본인 매수 행위 또는 청중에게 직접 매수를 권유하는 명시적 발언에만 적용. "좋아 보인다", "관심있다", "긍정적으로 본다"는 긍정으로 분류.'
    })

# 패턴 4: 타임스탬프 날짜 형식
date_ts = [i for i in invalid_ts_signals if re.search(r'월|일|\d{4}', str(i['signal'].get('timestamp', '')))]
if date_ts:
    patterns.append({
        'name': '타임스탬프 날짜 형식 오류',
        'count': len(date_ts),
        'cause': 'V9.1 프롬프트가 타임스탬프 형식 검증 없이 날짜 표기도 허용',
        'fix': '타임스탬프 형식을 HH:MM:SS 또는 MM:SS로 엄격히 제한. "영상의 어떤 시점에 이 발언이 나왔는지 MM:SS 형식으로만 기입"을 명시.'
    })

for i, p in enumerate(patterns, 1):
    report_lines.extend([
        f"### 오류 패턴 {i}: {p['name']}",
        f"- 발생 건수: {p['count']}",
        f"- 원인: {p['cause']}",
        f"- 개선안: {p['fix']}",
        ""
    ])

if not patterns:
    report_lines.append("패턴 분석 결과 특이 패턴 없음")
    report_lines.append("")

# 수익률 데이터
report_lines.extend([
    "## 💰 가격 데이터 현황",
    "",
    f"- 가격 데이터 있음: {prices_available}개",
    f"- 가격 데이터 없음: {prices_missing}개",
    f"- signal_prices.json 존재: {'있음' if os.path.exists(PRICES_FILE) else '없음'}",
    ""
])

# 정상 시그널
report_lines.extend([
    "## ✅ 정상 시그널",
    "",
    f"문제 없는 시그널: **{normal_count}개** / 전체 {len(signals)}개",
    ""
])

# 즉시 조치 필요
delete_list = [f"{s['stock']} (ID: {s['id'][:16]}...)" for s in invalid_stock_signals]
modify_list = [f"{r['stock']}: {r['current_signal']} → {r['ai_result'].get('correct_signal')} (ID: {r['id'][:16]}...)" for r in ai_wrong]
review_list = [f"{r['stock']} (ID: {r['id'][:16]}...)" for r in ai_wrong if r['ai_result'].get('correct_signal') not in ['매수', '긍정', '중립', '경계', '부정', '매도']]
ts_fix_list = [f"{i['signal']['stock']}: {i['reason']} (ID: {i['signal']['id'][:16]}...)" for i in invalid_ts_signals]

report_lines.extend([
    "## 📋 즉시 조치 필요 항목",
    "",
    "### 1. 삭제 (비종목 오추출)",
])
if delete_list:
    for d in delete_list:
        report_lines.append(f"- {d}")
else:
    report_lines.append("없음")

report_lines.extend([
    "",
    "### 2. 시그널 수정 (AI 검증 결과)",
])
if modify_list:
    for m in modify_list:
        report_lines.append(f"- {m}")
else:
    report_lines.append("없음")

report_lines.extend([
    "",
    "### 3. 타임스탬프 수정 필요",
])
if ts_fix_list:
    for t in ts_fix_list:
        report_lines.append(f"- {t}")
else:
    report_lines.append("없음")

report_lines.extend([
    "",
    "### 4. 재분석 필요 (중복 시그널)",
])
if duplicate_signals:
    for dup in duplicate_signals:
        report_lines.append(f"- {dup['stock']} ({len(dup['signals'])}개 중복)")
else:
    report_lines.append("없음")

report_lines.append("")

report_content = "\n".join(report_lines)

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"리포트 생성 완료: {REPORT_FILE}")


# ========== STEP 6: Supabase DB 업데이트 ==========
print("\n" + "=" * 60)
print("STEP 6: Supabase DB 업데이트")
print("=" * 60)

db_update_count = 0
db_error_count = 0

def patch_signal(signal_id, update_data):
    """Supabase에서 시그널 업데이트"""
    global db_update_count, db_error_count
    try:
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{signal_id}",
            json=update_data,
            headers={**SUPABASE_HEADERS, 'Prefer': 'return=representation'},
            timeout=15
        )
        if resp.status_code in [200, 204]:
            db_update_count += 1
            return True
        else:
            print(f"    DB 에러 {resp.status_code}: {resp.text[:100]}")
            db_error_count += 1
            return False
    except Exception as e:
        print(f"    예외: {e}")
        db_error_count += 1
        return False

# 6-1. 비종목 오추출 → rejected
print("\n[6-1] 비종목 오추출 → rejected")
for s in invalid_stock_signals:
    sid = s['id']
    print(f"  PATCH {sid[:16]}... ({s['stock']})", end='', flush=True)
    ok = patch_signal(sid, {
        'review_status': 'rejected',
        'review_note': 'QA: 지수/통화/일반명사 오추출'
    })
    print(" ✅" if ok else " ❌")
    time.sleep(0.3)

# 6-2. AI wrong → needs_review
print("\n[6-2] AI 오분류 → needs_review")
for r in ai_wrong:
    sid = r['id']
    correct = r['ai_result'].get('correct_signal', '')
    reason = r['ai_result'].get('reason', '')
    note = f"QA: {correct}로 변경 검토 필요 - {reason}"
    
    # 비종목으로 이미 rejected 처리된 것은 건너뜀
    if sid in {s['id'] for s in invalid_stock_signals}:
        print(f"  SKIP {sid[:16]}... (이미 rejected)")
        continue
    
    print(f"  PATCH {sid[:16]}... ({r['stock']}: {r['current_signal']}→{correct})", end='', flush=True)
    ok = patch_signal(sid, {
        'review_status': 'needs_review',
        'review_note': note
    })
    print(" ✅" if ok else " ❌")
    time.sleep(0.3)

# 6-3. 무효 타임스탬프 → review_note 추가
print("\n[6-3] 무효 타임스탬프 → review_note")
for item in invalid_ts_signals:
    s = item['signal']
    sid = s['id']
    
    # 이미 처리된 것 건너뜀
    if sid in {x['id'] for x in invalid_stock_signals}:
        print(f"  SKIP {sid[:16]}... (이미 rejected)")
        continue
    if sid in {r['id'] for r in ai_wrong}:
        # 기존 review_note에 추가
        existing_note = s.get('review_note') or ''
        new_note = existing_note + ' | QA: 타임스탬프 오류' if existing_note else 'QA: 타임스탬프 오류'
        print(f"  PATCH {sid[:16]}... ({s['stock']}) [TS 추가]", end='', flush=True)
        ok = patch_signal(sid, {'review_note': new_note})
        print(" ✅" if ok else " ❌")
        continue
    
    print(f"  PATCH {sid[:16]}... ({s['stock']}) [TS 오류]", end='', flush=True)
    ok = patch_signal(sid, {
        'review_status': 'needs_review',
        'review_note': 'QA: 타임스탬프 오류'
    })
    print(" ✅" if ok else " ❌")
    time.sleep(0.3)


# ========== 완료 요약 ==========
print("\n" + "=" * 60)
print("✅ QA 감사 완료!")
print("=" * 60)

total_issues = (
    len(invalid_stock_signals) + 
    len(invalid_ts_signals) + 
    len(ai_wrong) + 
    sum(len(d['signals']) for d in duplicate_signals) +
    len(quote_issues) +
    len(mismatch_signals)
)

auto_fixed = db_update_count
manual_review = len(ai_wrong) + len(duplicate_signals) + len(mismatch_signals)

print(f"\n📊 최종 결과:")
print(f"  총 문제 수: {total_issues}건")
print(f"  자동 수정 (DB): {auto_fixed}건")
print(f"  수동 검토 필요: {manual_review}건")
print(f"  정상 시그널: {normal_count}개/{len(signals)}개")
print(f"\n  📄 리포트: {REPORT_FILE}")
print(f"  📦 중간 데이터: {INTERMEDIATE_FILE}")
print(f"\n상세 내역:")
print(f"  🔴 비종목 오추출: {len(invalid_stock_signals)}건 (→ rejected)")
print(f"  🔴 AI 오분류: {len(ai_wrong)}건 (→ needs_review)")
print(f"  🟡 타임스탬프 오류: {len(invalid_ts_signals)}건")
print(f"  🟡 중복 시그널: {sum(len(d['signals']) for d in duplicate_signals)}건")
print(f"  🟢 key_quote 품질: {len(quote_issues)}건")
print(f"  🟡 mention_type 불일치: {len(mismatch_signals)}건")
print(f"\nDB 업데이트: {db_update_count}건 성공, {db_error_count}건 실패")
