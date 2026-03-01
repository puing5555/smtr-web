#!/usr/bin/env python3
"""
V10.1 프롬프트 자율 개선 - DB 시그널 분석
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import re
from datetime import datetime

# Supabase 접속 정보
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

# PostgreSQL 접속 설정
DB_CONFIG = {
    'host': 'db.arypzhotxflimroprmdk.supabase.co',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '1234VoidZero!',
}

def get_db_connection():
    """Supabase PostgreSQL 연결"""
    return psycopg2.connect(**DB_CONFIG)

def fetch_all_signals():
    """101개 시그널 전체 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            s.id,
            s.stock,
            s.ticker,
            s.signal,
            s.confidence,
            s.key_quote,
            s.reasoning,
            s.video_id,
            s.speaker_id,
            sp.name as speaker_name,
            v.title as video_title,
            v.subtitle_text
        FROM influencer_signals s
        LEFT JOIN speakers sp ON s.speaker_id = sp.id
        LEFT JOIN influencer_videos v ON s.video_id = v.id
        ORDER BY s.id
        """
        
        cursor.execute(query)
        signals = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"총 {len(signals)}개 시그널 조회 완료")
        return [dict(signal) for signal in signals]
        
    except Exception as e:
        print(f"DB 조회 실패: {e}")
        return []

def analyze_issues(signals):
    """이슈 분석 및 분류"""
    issues = {
        'key_quote_quality': [],
        'signal_misclassification': [],
        'speaker_misattribution': [],
        'duplicates': [],
        'confidence_misapplied': [],
        'other': []
    }
    
    # 각 시그널 검증
    for signal in signals:
        signal_id = signal['id']
        stock = signal['stock'] or ''
        ticker = signal['ticker'] or ''
        signal_type = signal['signal'] or ''
        confidence = signal['confidence'] or ''
        key_quote = signal['key_quote'] or ''
        reasoning = signal['reasoning'] or ''
        speaker_name = signal['speaker_name'] or ''
        video_title = signal['video_title'] or ''
        subtitle_text = signal['subtitle_text'] or ''
        
        # 1. key_quote 품질 검사
        quote_issues = check_key_quote_quality(signal_id, stock, ticker, key_quote, signal_type)
        issues['key_quote_quality'].extend(quote_issues)
        
        # 2. 시그널 분류 검사
        classification_issues = check_signal_classification(signal_id, stock, signal_type, key_quote, reasoning, subtitle_text)
        issues['signal_misclassification'].extend(classification_issues)
        
        # 3. 화자 귀속 검사
        speaker_issues = check_speaker_attribution(signal_id, speaker_name, video_title, subtitle_text)
        issues['speaker_misattribution'].extend(speaker_issues)
        
        # 4. confidence 적용 검사
        confidence_issues = check_confidence_application(signal_id, confidence, key_quote, signal_type)
        issues['confidence_misapplied'].extend(confidence_issues)
    
    # 5. 중복 검사
    duplicate_issues = check_duplicates(signals)
    issues['duplicates'].extend(duplicate_issues)
    
    return issues

def check_key_quote_quality(signal_id, stock, ticker, key_quote, signal_type):
    """key_quote 품질 검사"""
    issues = []
    
    if not key_quote or len(key_quote.strip()) < 20:
        issues.append({
            'id': signal_id,
            'type': 'key_quote_too_short',
            'description': f'key_quote가 20자 미만: "{key_quote}"',
            'stock': stock,
            'signal': signal_type
        })
    
    # 종목명 포함 검사
    if stock and key_quote:
        stock_mentioned = False
        # 종목명 또는 ticker가 포함되어 있는지 확인
        if stock in key_quote or (ticker and ticker in key_quote):
            stock_mentioned = True
        # 약칭 확인 (삼전, 하닉 등)
        stock_shortcuts = {
            '삼성전자': ['삼전'],
            'SK하이닉스': ['하닉', '하이닉스'],
            '현대차': ['현차'],
            'LG전자': ['LG'],
            '포스코홀딩스': ['포스코']
        }
        for full_name, shortcuts in stock_shortcuts.items():
            if stock == full_name:
                for shortcut in shortcuts:
                    if shortcut in key_quote:
                        stock_mentioned = True
                        break
        
        if not stock_mentioned:
            issues.append({
                'id': signal_id,
                'type': 'stock_not_mentioned_in_quote',
                'description': f'key_quote에 종목명({stock}) 미포함: "{key_quote}"',
                'stock': stock,
                'signal': signal_type
            })
    
    # 투자근거 포함 검사 (시그널이 있는 경우)
    if signal_type in ['매수', '긍정', '경계', '매도'] and key_quote:
        investment_keywords = [
            '실적', '매출', '영업이익', '수익', '성장', '전망', '기대', '우려', '리스크',
            '밸류에이션', '주가', '목표가', '상승', '하락', '기회', '투자', '추천',
            '긍정적', '부정적', '호재', '악재', '펀더멘털', '기술적', '차트',
            '정부정책', '규제', '경기', '시장', '경쟁', '점유율', '브랜드'
        ]
        
        has_investment_reasoning = any(keyword in key_quote for keyword in investment_keywords)
        
        if not has_investment_reasoning:
            issues.append({
                'id': signal_id,
                'type': 'no_investment_reasoning',
                'description': f'key_quote에 투자근거 없음: "{key_quote}"',
                'stock': stock,
                'signal': signal_type
            })
    
    return issues

def check_signal_classification(signal_id, stock, signal_type, key_quote, reasoning, subtitle_text):
    """시그널 분류 오류 검사"""
    issues = []
    
    if not signal_type:
        return issues
    
    # 전망성 발언인데 시그널로 분류된 경우
    forecast_patterns = [
        '전망', '예상', '예측', '~것 같다', '~듯하다', '~보인다', '~것으로 보인다',
        '~할 것', '~할 듯', '~할 가능성', '~할 확률', '시장에서는', '애널리스트들은'
    ]
    
    action_patterns = [
        '사야', '팔아야', '매수해', '매도해', '추천', '비추천', '사세요', '파세요',
        '들어가', '나오', '홀딩', '보유', '손절', '익절', '해야 된다', '해야 한다'
    ]
    
    context = f"{key_quote} {reasoning}".lower()
    
    has_forecast = any(pattern in context for pattern in forecast_patterns)
    has_action = any(pattern in context for pattern in action_patterns)
    
    if has_forecast and not has_action and signal_type in ['매수', '매도']:
        issues.append({
            'id': signal_id,
            'type': 'forecast_classified_as_signal',
            'description': f'전망성 발언을 시그널로 분류: "{key_quote}"',
            'stock': stock,
            'signal': signal_type
        })
    
    # 교육성 내용인데 시그널로 분류된 경우
    education_patterns = [
        '공부', '학습', '이해', '개념', '원리', '방법', '차이', '구분', '설명',
        '교육', '강의', '수업', '튜토리얼', '가이드', '기초', '입문'
    ]
    
    has_education = any(pattern in context for pattern in education_patterns)
    
    if has_education and signal_type in ['매수', '긍정', '경계', '매도']:
        issues.append({
            'id': signal_id,
            'type': 'education_classified_as_signal',
            'description': f'교육성 내용을 시그널로 분류: "{key_quote}"',
            'stock': stock,
            'signal': signal_type
        })
    
    return issues

def check_speaker_attribution(signal_id, speaker_name, video_title, subtitle_text):
    """화자 귀속 오류 검사"""
    issues = []
    
    if not speaker_name:
        return issues
    
    # 채널명이 화자로 설정된 경우 (게스트 영상일 가능성)
    channel_names = [
        '신사임당', '코린이 아빠', '조대표', '삼프로TV', '경제유튜버', '스탁논리',
        '슈퍼개미', '개미만세', '재테크 전문가', '주식 전문가'
    ]
    
    if speaker_name in channel_names and video_title:
        # 게스트 출연 키워드가 있는지 확인
        guest_keywords = ['출연', '게스트', '인터뷰', '대담', 'vs', '특별출연', '초청']
        has_guest = any(keyword in video_title for keyword in guest_keywords)
        
        if has_guest:
            issues.append({
                'id': signal_id,
                'type': 'channel_name_as_speaker_with_guest',
                'description': f'게스트 영상인데 채널명이 화자: "{speaker_name}" in "{video_title}"',
                'speaker': speaker_name,
                'video_title': video_title
            })
    
    return issues

def check_confidence_application(signal_id, confidence, key_quote, signal_type):
    """confidence 적용 오류 검사"""
    issues = []
    
    if not confidence or not key_quote:
        return issues
    
    # 조건부 표현인데 confidence가 medium 이상인 경우
    conditional_patterns = [
        '만약', '~라면', '~한다면', '~할 경우', '~하면', '조건부', '상황에 따라',
        '경우에 따라', '~에 달려', '불확실', '애매', '확신할 수 없'
    ]
    
    has_conditional = any(pattern in key_quote for pattern in conditional_patterns)
    
    if has_conditional and confidence in ['high', 'medium']:
        issues.append({
            'id': signal_id,
            'type': 'conditional_with_high_confidence',
            'description': f'조건부 발언인데 confidence {confidence}: "{key_quote}"',
            'signal': signal_type,
            'confidence': confidence
        })
    
    return issues

def check_duplicates(signals):
    """중복 시그널 검사"""
    issues = []
    
    # video_id + stock + speaker_id 조합으로 그룹화
    groups = {}
    for signal in signals:
        key = (signal['video_id'], signal['stock'], signal['speaker_id'])
        if key not in groups:
            groups[key] = []
        groups[key].append(signal)
    
    # 같은 그룹에 2개 이상 시그널이 있으면 중복
    for key, group_signals in groups.items():
        if len(group_signals) > 1:
            for signal in group_signals:
                issues.append({
                    'id': signal['id'],
                    'type': 'duplicate_signal',
                    'description': f'중복 시그널 (영상={signal["video_id"]}, 종목={signal["stock"]}, 화자={signal["speaker_name"]})',
                    'stock': signal['stock'],
                    'video_id': signal['video_id'],
                    'speaker': signal['speaker_name']
                })
    
    return issues

def save_analysis_report(round_num, issues, total_signals):
    """분석 보고서 저장"""
    total_issues = sum(len(category_issues) for category_issues in issues.values())
    
    report = f"""# V10.1 프롬프트 개선 - 라운드 {round_num} 분석 보고서

## 기본 정보
- 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 총 시그널 수: {total_signals}
- 발견된 이슈 수: {total_issues}

## 이슈 분류별 현황

### 1. key_quote 품질 이슈 ({len(issues['key_quote_quality'])}건)
"""
    
    for issue in issues['key_quote_quality']:
        report += f"- [{issue['id']}] {issue['type']}: {issue['description']}\n"
    
    report += f"\n### 2. 시그널 분류 이슈 ({len(issues['signal_misclassification'])}건)\n"
    for issue in issues['signal_misclassification']:
        report += f"- [{issue['id']}] {issue['type']}: {issue['description']}\n"
    
    report += f"\n### 3. 화자 귀속 이슈 ({len(issues['speaker_misattribution'])}건)\n"
    for issue in issues['speaker_misattribution']:
        report += f"- [{issue['id']}] {issue['type']}: {issue['description']}\n"
    
    report += f"\n### 4. 중복 시그널 ({len(issues['duplicates'])}건)\n"
    for issue in issues['duplicates']:
        report += f"- [{issue['id']}] {issue['type']}: {issue['description']}\n"
    
    report += f"\n### 5. confidence 적용 이슈 ({len(issues['confidence_misapplied'])}건)\n"
    for issue in issues['confidence_misapplied']:
        report += f"- [{issue['id']}] {issue['type']}: {issue['description']}\n"
    
    report += f"\n### 6. 기타 이슈 ({len(issues['other'])}건)\n"
    for issue in issues['other']:
        report += f"- [{issue['id']}] {issue['type']}: {issue['description']}\n"
    
    # 이슈 상세 분석을 JSON으로도 저장
    report += f"\n## 상세 분석 데이터\n```json\n{json.dumps(issues, ensure_ascii=False, indent=2)}\n```\n"
    
    filename = f"C:\\Users\\Mario\\work\\prompts\\v10_{round_num}_report.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"분석 보고서 저장: {filename}")
    return total_issues

def main():
    """메인 실행"""
    print("V10.1 프롬프트 이슈 분석 시작")
    
    # DB에서 시그널 조회
    signals = fetch_all_signals()
    if not signals:
        print("시그널 조회 실패")
        return
    
    # 이슈 분석
    print("이슈 분석 중...")
    issues = analyze_issues(signals)
    
    # 보고서 저장
    total_issues = save_analysis_report(1, issues, len(signals))
    
    print(f"\n라운드 1 분석 완료")
    print(f"총 시그널: {len(signals)}개")
    print(f"발견 이슈: {total_issues}개")
    
    # 이슈별 요약 출력
    for category, category_issues in issues.items():
        if category_issues:
            print(f"- {category}: {len(category_issues)}건")

if __name__ == "__main__":
    main()