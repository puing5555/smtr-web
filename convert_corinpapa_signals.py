#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코린이 아빠 시그널 169개를 smtr-v3.html 형식으로 변환
"""
import json
import re

def convert_signal_to_smtr_format(signal):
    """소스 시그널을 smtr-v3.html의 corinpapaStatements 형식으로 변환"""
    
    # asset에서 티커 제거 (예: "비트마인 (BMNR)" → "비트마인")
    stock = signal.get('asset', '').strip()
    if '(' in stock and ')' in stock:
        stock = stock.split('(')[0].strip()
    
    # signal_type을 소문자로 변환
    dir_type = signal.get('signal_type', 'neutral').lower()
    
    # content에서 headline 생성 (첫 50자)
    content = signal.get('content', '')
    headline = content[:50] + ('...' if len(content) > 50 else '')
    
    # timestamp에서 대괄호 제거
    ts = signal.get('timestamp', '')
    if ts.startswith('[') and ts.endswith(']'):
        ts = ts[1:-1]
    
    # video_id를 사용해 URL 생성
    video_id = signal.get('video_id', '')
    video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
    
    # smtr 형식으로 변환
    smtr_signal = {
        "stock": stock,
        "dirType": dir_type,
        "headline": headline,
        "quote": content,
        "detail": signal.get('context', ''),
        "date": signal.get('date', ''),
        "ts": ts,
        "url": video_url,
        "videoUrl": video_url,
        "speaker": "코린이 아빠",
        "video_id": video_id,
        "influencer": "코린이 아빠",
        "influencer_id": 99
    }
    
    return smtr_signal

def main():
    # 소스 데이터 읽기
    with open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_deduped_signals_8types_dated.json', 'r', encoding='utf-8') as f:
        source_signals = json.load(f)
    
    print(f"소스 데이터: {len(source_signals)}개 시그널")
    
    # 변환
    converted_signals = []
    for signal in source_signals:
        try:
            converted = convert_signal_to_smtr_format(signal)
            converted_signals.append(converted)
        except Exception as e:
            print(f"변환 에러 발생: {e}")
            print(f"문제 시그널: {signal}")
    
    print(f"변환 완료: {len(converted_signals)}개 시그널")
    
    # JavaScript 배열 형태로 변환
    js_array = "var corinpapaStatements = " + json.dumps(converted_signals, ensure_ascii=False, indent=2) + ";"
    
    # 결과 저장
    with open(r'C:\Users\Mario\work\corinpapa_statements_converted.js', 'w', encoding='utf-8') as f:
        f.write(js_array)
    
    print("변환된 JavaScript 파일 저장됨: corinpapa_statements_converted.js")
    print(f"첫 번째 시그널 예시:")
    if converted_signals:
        print(json.dumps(converted_signals[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()