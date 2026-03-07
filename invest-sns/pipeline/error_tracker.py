#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
error_tracker.py - QA 오류 패턴 누적 저장
QA에서 검출된 이슈를 error_patterns.json에 누적.
10건 이상 누적 시 프롬프트 수정 제안 자동 작성.
"""

import json
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'qa')
os.makedirs(DATA_DIR, exist_ok=True)

ERROR_PATTERNS_FILE = os.path.join(DATA_DIR, 'error_patterns.json')
PROMPT_FIX_FILE = os.path.join(DATA_DIR, 'prompt_fix_suggestions.md')

# 이슈 → 패턴 매핑
PATTERN_RULES = [
    {
        'pattern_id': '지수_종목_오추출',
        'keywords': ['지수 오추출', 'index_extractions'],
        'description': '코스피/나스닥/S&P 등 지수를 종목으로 추출',
        'prompt_problem': '프롬프트가 지수명과 종목명을 구분하지 못함',
        'prompt_fix': '명시적으로 "코스피, 코스닥, S&P500, 나스닥, 다우 등 지수는 stock 필드에 사용 금지" 추가',
    },
    {
        'pattern_id': '일반단어_오추출',
        'keywords': ['일반 단어 오추출', 'generic_extractions'],
        'description': '"금", "달러" 등 일반 단어를 종목으로 추출',
        'prompt_problem': '원자재/화폐 명칭이 종목으로 오분류됨',
        'prompt_fix': '"금, 달러, 원, 엔 등 화폐/원자재는 종목이 아님. SPDR Gold Shares(GLD) 등 ETF 형태만 인정" 추가',
    },
    {
        'pattern_id': '매수_편향',
        'keywords': ['매수 편향 의심'],
        'description': '매수 비율 80% 이상 - 분석 편향 의심',
        'prompt_problem': '프롬프트가 매수/긍정 구분 기준이 불명확해서 긍정→매수 오분류',
        'prompt_fix': 'V10.11의 "본인이 샀거나 사라고 했는가?" 기준 강화, 예시 추가',
    },
    {
        'pattern_id': '부정시그널_미검출',
        'keywords': ['부정 시그널 미검출'],
        'description': '매도/경계 시그널이 전혀 없음',
        'prompt_problem': '프롬프트가 부정적 발언을 시그널로 추출하지 않음',
        'prompt_fix': '"주가 고점 경고, 리스크 언급, 매도 시점 제안도 반드시 경계/매도 시그널로 추출" 강화',
    },
    {
        'pattern_id': '타임스탬프_부정확',
        'keywords': ['타임스탬프 부정확 의심'],
        'description': '타임스탬프 50% 이상이 00:00:00 또는 영상 끝',
        'prompt_problem': '자막 텍스트에서 타임스탬프 매핑 실패',
        'prompt_fix': '"타임스탬프를 알 수 없으면 00:00:00 대신 발언이 나온 구간 시작 시간을 추정해서 입력" 추가',
    },
    {
        'pattern_id': '짧은_종목명',
        'keywords': ['짧은 종목명'],
        'description': '2글자 이하 종목명 추출',
        'prompt_problem': '종목명 정규화 미흡',
        'prompt_fix': '"종목명은 최소 3글자 이상의 공식 명칭 사용. 약칭 사용 금지" 추가',
    },
]


def load_patterns() -> dict:
    """기존 패턴 로드"""
    if os.path.exists(ERROR_PATTERNS_FILE):
        with open(ERROR_PATTERNS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {p['pattern_id']: p for p in data}
    return {}


def save_patterns(patterns: dict):
    """패턴 저장"""
    pattern_list = list(patterns.values())
    with open(ERROR_PATTERNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pattern_list, f, ensure_ascii=False, indent=2)


def match_pattern(issue_text: str) -> str | None:
    """이슈 텍스트에서 패턴 ID 찾기"""
    for rule in PATTERN_RULES:
        for kw in rule['keywords']:
            if kw in issue_text:
                return rule['pattern_id']
    return None


def get_rule_by_id(pattern_id: str) -> dict | None:
    for rule in PATTERN_RULES:
        if rule['pattern_id'] == pattern_id:
            return rule
    return None


def track_errors(channel_handle: str, qa_result: dict) -> dict:
    """
    QA 결과에서 이슈/경고를 패턴으로 분류하여 누적 저장.
    반환: 업데이트된 패턴 통계
    """
    today = date.today().isoformat()
    patterns = load_patterns()

    all_texts = qa_result.get('issues', []) + qa_result.get('warnings', [])

    new_pattern_counts = {}

    for text in all_texts:
        pattern_id = match_pattern(text)
        if not pattern_id:
            continue

        rule = get_rule_by_id(pattern_id)
        if not rule:
            continue

        # 예시 추출 (이슈 텍스트에서 핵심 정보)
        example = text[:100]

        if pattern_id not in patterns:
            patterns[pattern_id] = {
                'pattern_id': pattern_id,
                'description': rule['description'],
                'count': 0,
                'examples': [],
                'first_seen': today,
                'last_seen': today,
                'channels': [],
            }

        p = patterns[pattern_id]
        p['count'] += 1
        p['last_seen'] = today

        if example not in p['examples']:
            p['examples'] = (p['examples'] + [example])[-10:]  # 최대 10개 유지

        if channel_handle not in p['channels']:
            p['channels'].append(channel_handle)

        new_pattern_counts[pattern_id] = p['count']

    save_patterns(patterns)

    # 10건 이상 패턴에 대해 프롬프트 수정 제안 생성
    high_count_patterns = {k: v for k, v in patterns.items() if v['count'] >= 10}
    if high_count_patterns:
        generate_prompt_fix_suggestions(high_count_patterns)

    # 요약 출력
    if new_pattern_counts:
        print(f"\n[에러추적] {channel_handle} - {len(new_pattern_counts)}개 패턴 업데이트:")
        for pid, count in new_pattern_counts.items():
            emoji = "🔥" if count >= 10 else "📊"
            print(f"  {emoji} {pid}: 누적 {count}건")
    else:
        print(f"\n[에러추적] {channel_handle} - 새 패턴 없음")

    return new_pattern_counts


def generate_prompt_fix_suggestions(high_count_patterns: dict):
    """10건 이상 누적된 패턴에 대해 프롬프트 수정 제안 작성"""
    lines = [
        "# 프롬프트 수정 제안 (자동 생성)",
        f"생성일: {date.today().isoformat()}",
        "",
        "## 누적 10건 이상 오류 패턴 & 수정 제안",
        "",
    ]

    for pattern_id, pattern in sorted(high_count_patterns.items(), key=lambda x: -x[1]['count']):
        rule = get_rule_by_id(pattern_id)
        if not rule:
            continue

        lines.extend([
            f"### {pattern_id} ({pattern['count']}건)",
            f"**설명**: {pattern['description']}",
            f"**현재 프롬프트 문제**: {rule['prompt_problem']}",
            f"**수정 제안**: {rule['prompt_fix']}",
            f"**첫 발견**: {pattern['first_seen']} | **최근**: {pattern['last_seen']}",
            f"**채널**: {', '.join(pattern['channels'])}",
            "",
            "**예시**:",
        ])
        for ex in pattern['examples'][:3]:
            lines.append(f"- {ex}")
        lines.append("")

    with open(PROMPT_FIX_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"[에러추적] 프롬프트 수정 제안 저장: {PROMPT_FIX_FILE}")


if __name__ == '__main__':
    # 테스트
    test_qa = {
        'issues': [
            "🚨 지수 오추출: '코스피' (video: abc123)",
            "🚨 일반 단어 오추출: '금' (video: xyz456)",
        ],
        'warnings': [
            "⚠️ 매수 편향 의심: 매수 18/20 (90.0%)",
        ]
    }
    result = track_errors('TEST_CHANNEL', test_qa)
    print(f"패턴 업데이트: {result}")
