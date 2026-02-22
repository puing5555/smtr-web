#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코린이 아빠 검증 완료 시그널 169개를 test-timeline.html에 통합하는 스크립트
"""
import json
import re
from datetime import datetime

# 파일 경로 설정
SIGNALS_FILE = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_deduped_signals_8types_dated.json"
REVIEW_FILE = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_review_results.json"
HTML_FILE = r"C:\Users\Mario\work\invest-sns\test-timeline.html"
HTML_BACKUP = r"C:\Users\Mario\work\invest-sns\test-timeline.html.backup"

def main():
    print("코린이 아빠 시그널 통합 시작...")
    
    # 1. 시그널 데이터 로드
    print("1. 시그널 데이터 로드 중...")
    with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    print(f"   총 {len(signals)}개 시그널 로드됨")
    
    # 2. 리뷰 결과 로드
    print("2. 리뷰 결과 로드 중...")
    with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    # approved만 필터링
    approved_keys = [key for key, value in reviews.items() if value.get('status') == 'approved']
    print(f"   총 {len(approved_keys)}개 승인된 시그널")
    
    # 3. 시그널을 corinpapaStatements 형식으로 변환
    print("3. 시그널 형식 변환 중...")
    corinpapa_statements = []
    
    # signal_type 매핑
    signal_type_mapping = {
        'STRONG_BUY': 'strong_buy',
        'BUY': 'buy',
        'POSITIVE': 'positive',
        'HOLD': 'hold',
        'NEUTRAL': 'neutral',
        'CONCERN': 'concern',
        'SELL': 'sell',
        'STRONG_SELL': 'strong_sell'
    }
    
    for signal in signals:
        # 승인된 시그널만 처리
        signal_key = f"{signal['video_id']}_{signal['asset']}"
        if signal_key not in approved_keys:
            continue
            
        # dirType 변환
        dir_type = signal_type_mapping.get(signal['signal_type'], 'neutral')
        
        # timestamp에서 괄호 제거
        timestamp = signal.get('timestamp', '0:00').strip('[]')
        
        # detail은 context 우선, 없으면 content 앞부분
        detail = signal.get('context', '')
        if not detail and signal.get('content'):
            detail = signal['content'][:100] + ('...' if len(signal['content']) > 100 else '')
        
        # statement 객체 생성
        statement = {
            "stock": signal['asset'],
            "dirType": dir_type,
            "detail": detail,
            "quote": signal['content'],
            "influencer": "코린이 아빠",
            "video_id": signal['video_id'],
            "ts": timestamp,
            "date": signal['date'],
            "url": f"https://www.youtube.com/watch?v={signal['video_id']}"
        }
        
        corinpapa_statements.append(statement)
    
    # 날짜순 정렬 (최신순)
    corinpapa_statements.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"   {len(corinpapa_statements)}개 시그널 변환 완료")
    
    # 4. HTML 파일 백업
    print("4. HTML 파일 백업 중...")
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    with open(HTML_BACKUP, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 5. corinpapaStatements 부분 교체
    print("5. HTML 파일 수정 중...")
    
    # JS 배열 문자열 생성 (JSON 특수문자 이스케이프 포함)
    js_statements = json.dumps(corinpapa_statements, ensure_ascii=False, indent=12)
    
    # corinpapaStatements 변수 패턴 찾기
    pattern = r'var corinpapaStatements = \[\s*\{[^}]*\}[^}]*\s*\];'
    replacement = f'var corinpapaStatements = {js_statements};'
    
    # 교체 실행
    new_html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    # 6. 인플루언서 메타데이터의 stmtCount 업데이트
    print("6. 인플루언서 메타데이터 업데이트 중...")
    
    # 코린이 아빠의 stmtCount를 169로 업데이트
    corinpapa_pattern = r"(\{id: 4, name: '코린이 아빠'[^}]*stmtCount: )\d+(\})"
    corinpapa_replacement = rf"\g<1>{len(corinpapa_statements)}\g<2>"
    
    new_html_content = re.sub(corinpapa_pattern, corinpapa_replacement, new_html_content)
    
    # 7. 수정된 HTML 파일 저장
    print("7. 수정된 HTML 파일 저장 중...")
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_html_content)
    
    print(f"\n[OK] 작업 완료!")
    print(f"   - {len(corinpapa_statements)}개 시그널이 test-timeline.html에 통합됨")
    print(f"   - 백업 파일: {HTML_BACKUP}")
    print(f"   - 인플루언서 메타데이터 stmtCount 업데이트: {len(corinpapa_statements)}")
    print(f"\n[확인] 확인 방법:")
    print(f"   1. 파일을 브라우저에서 열기: {HTML_FILE}")
    print(f"   2. 인플루언서 탭 → 발언 서브탭 → 코린이 아빠 시그널 확인")
    print(f"   3. localhost:3001에서 Next.js 개발 서버로 확인 (실행 중인 경우)")

if __name__ == "__main__":
    main()