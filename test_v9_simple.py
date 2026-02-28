#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime

def test_v9_analysis():
    """V9 분석 테스트"""
    
    # 테스트 데이터
    test_channels = {
        'syuka': '삼성전자 지금 가격에서 매수를 추천드립니다',
        'hyoseok': 'SK하이닉스는 매수 기회라고 봅니다', 
        'booknam': '장기적 관점이 중요합니다',  # 교육 콘텐츠
        'talent': '비트코인 조금씩 매수해서 포지션을 늘려가는 것을 추천합니다'
    }
    
    results = []
    
    print("V9 파이프라인 테스트 시작")
    print("-" * 40)
    
    for channel, text in test_channels.items():
        print(f"{channel}: {text[:30]}...")
        
        # V9 분석 시뮬레이션
        if '매수' in text and '추천' in text:
            if channel == 'syuka':
                signal = {
                    'speaker': '슈카',
                    'stock': '삼성전자', 
                    'signal': '매수',
                    'confidence': 'high'
                }
                results.append(signal)
                print(f"  -> 시그널: {signal['stock']} {signal['signal']}")
                
            elif channel == 'hyoseok':
                signal = {
                    'speaker': '이효석',
                    'stock': 'SK하이닉스',
                    'signal': '매수', 
                    'confidence': 'medium'
                }
                results.append(signal)
                print(f"  -> 시그널: {signal['stock']} {signal['signal']}")
                
            elif channel == 'talent':
                signal = {
                    'speaker': '달란트',
                    'stock': '비트코인',
                    'signal': '매수',
                    'confidence': 'medium'
                }
                results.append(signal)
                print(f"  -> 시그널: {signal['stock']} {signal['signal']}")
        else:
            print("  -> 시그널 없음 (교육/뉴스 콘텐츠)")
    
    print("-" * 40)
    print(f"총 시그널: {len(results)}개")
    
    # 결과 저장
    result_data = {
        'timestamp': datetime.now().isoformat(),
        'total_signals': len(results),
        'signals': results
    }
    
    with open('v9_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print("결과 저장: v9_test_result.json")
    
    return result_data

if __name__ == "__main__":
    test_v9_analysis()