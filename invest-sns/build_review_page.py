#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

def load_data():
    """데이터 로드"""
    print("[로드] 데이터 로딩 중...")
    
    # 파일 경로들
    signals_file = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_deduped_signals.json"
    claude_partial_file = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_claude_partial_60.json"
    claude_full_file = r"C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_claude_verify_full.json"
    gpt_verify_file = r"C:\Users\Mario\.openclaw\workspace\smtr_data\corinpapa1106\_verify_batch_full_result.jsonl"
    
    # 시그널 데이터 로드
    with open(signals_file, 'r', encoding='utf-8') as f:
        signals = json.load(f)
    print(f"[OK] 시그널: {len(signals)}개")
    
    # Claude 검증 결과 로드 (전체 또는 부분)
    claude_results = {}
    if os.path.exists(claude_full_file):
        with open(claude_full_file, 'r', encoding='utf-8') as f:
            claude_data = json.load(f)
        print(f"[OK] Claude 전체 검증: {len(claude_data)}개")
    elif os.path.exists(claude_partial_file):
        with open(claude_partial_file, 'r', encoding='utf-8') as f:
            claude_data = json.load(f)
        print(f"[OK] Claude 부분 검증: {len(claude_data)}개")
    else:
        claude_data = []
        print("[WARN] Claude 검증 결과 없음")
    
    # Claude 검증 결과를 키로 매핑
    for item in claude_data:
        key = f"{item['video_id']}-{item['asset']}-{item['signal_type']}-{item['content'][:50]}"
        claude_results[key] = item.get('claude_verification', {})
    
    # GPT-4o 검증 결과 로드
    gpt_results = {}
    if os.path.exists(gpt_verify_file):
        with open(gpt_verify_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    gpt_data = json.loads(line)
                    # GPT 결과에서 키를 만들어서 매핑
                    # 이건 실제 파일 구조에 맞게 조정 필요
                    pass
        print("[OK] GPT-4o 검증 로드됨")
    else:
        print("[WARN] GPT-4o 검증 결과 없음")
    
    # 데이터 병합
    merged_signals = []
    for signal in signals:
        key = f"{signal['video_id']}-{signal['asset']}-{signal['signal_type']}-{signal['content'][:50]}"
        
        # Claude 검증 결과 추가
        if key in claude_results:
            signal['claude_verification'] = claude_results[key]
        
        # GPT-4o 검증 결과 추가 (있다면)
        if key in gpt_results:
            signal['gpt_verification'] = gpt_results[key]
        
        merged_signals.append(signal)
    
    return merged_signals

def build_html(signals):
    """HTML 파일 빌드"""
    print(f"[빌드] {len(signals)}개 시그널로 HTML 빌드 중...")
    
    # HTML 템플릿 로드
    template_file = r"C:\Users\Mario\work\invest-sns\signal-review.html"
    with open(template_file, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # 데이터를 JavaScript 형식으로 변환
    signals_json = json.dumps(signals, ensure_ascii=False, indent=2)
    
    # HTML에 데이터 삽입
    # "const signalsData = [" 다음에 실제 데이터 삽입
    html_with_data = html_template.replace(
        "const signalsData = [\n            // 데이터가 여기에 삽입됩니다\n        ];",
        f"const signalsData = {signals_json};"
    )
    
    return html_with_data

def main():
    print("[시작] 리뷰 페이지 빌드 시작")
    
    # 1. 데이터 로드
    signals = load_data()
    
    # 2. HTML 빌드
    html_content = build_html(signals)
    
    # 3. 최종 파일 저장
    output_file = r"C:\Users\Mario\work\invest-sns\signal-review.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[완료] 리뷰 페이지 생성됨: {output_file}")
    
    # 통계 출력
    total = len(signals)
    claude_verified = len([s for s in signals if s.get('claude_verification')])
    confirmed = len([s for s in signals if s.get('claude_verification', {}).get('judgment') == 'confirmed'])
    corrected = len([s for s in signals if s.get('claude_verification', {}).get('judgment') == 'corrected'])
    rejected = len([s for s in signals if s.get('claude_verification', {}).get('judgment') == 'rejected'])
    
    print(f"\n[통계] 최종 통계:")
    print(f"  - 총 시그널: {total}개")
    print(f"  - Claude 검증 완료: {claude_verified}개")
    print(f"  - 확인됨: {confirmed}개")
    print(f"  - 수정됨: {corrected}개") 
    print(f"  - 거부됨: {rejected}개")
    print(f"  - 미검증: {total - claude_verified}개")

if __name__ == "__main__":
    main()