#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V9 파이프라인 테스트 - 더미 데이터로 프롬프트 및 Supabase 연동 테스트
"""

import json
import time
from datetime import datetime

# 더미 자막 데이터
DUMMY_SUBTITLES = {
    'syuka': """
    안녕하세요 슈카입니다. 오늘은 삼성전자에 대해서 이야기해보려고 합니다.
    삼성전자 같은 경우에는 이번 4분기 실적이 정말 좋게 나올 것 같아요.
    특히 메모리 반도체 쪽에서 가격 상승이 본격화되고 있거든요.
    저는 개인적으로 삼성전자 지금 가격에서 매수를 추천드립니다.
    목표주가는 90만원 정도로 보고 있어요.
    """,
    'hyoseok': """
    이효석입니다. 최근 반도체 섹터 전반에 대해 말씀드리겠습니다.
    SK하이닉스는 HBM3 양산이 본격화되면서 수익성이 크게 개선될 전망입니다.
    현재 주가가 조정을 받고 있지만 이것은 매수 기회라고 봅니다.
    반도체 업사이클이 시작되었다고 판단하고 있습니다.
    """,
    'booknam': """
    부읽남입니다. 오늘은 책을 통해 투자 철학에 대해 이야기하려고 합니다.
    가치투자의 아버지 벤저민 그레이엄이 말했듯이 장기적 관점이 중요합니다.
    단기적인 주가 변동에 흔들리지 말고 기업의 본질적 가치를 봐야 합니다.
    """,
    'talent': """
    달란트입니다. 최근 비트코인 상황을 분석해보겠습니다.
    비트코인이 70,000달러를 돌파하면서 상승 추세가 확실해졌습니다.
    ETF 자금 유입이 지속되고 있고 기관투자자들의 관심도 높아지고 있어요.
    지금 시점에서는 조금씩 매수해서 포지션을 늘려가는 것을 추천합니다.
    """
}

def analyze_with_v9_prompt(channel_name, subtitle_text):
    """V9 프롬프트로 분석 (시뮬레이션)"""
    
    # V9 프롬프트 규칙 적용 시뮬레이션
    signals = []
    
    if channel_name == 'syuka':
        if '삼성전자' in subtitle_text and '매수' in subtitle_text:
            signals.append({
                'speaker': '슈카',
                'stock': '삼성전자',
                'ticker': '005930',
                'market': 'KR',
                'mention_type': '결론',
                'signal': '매수',
                'confidence': 'high',
                'timestamp': '3:45',
                'key_quote': '삼성전자 지금 가격에서 매수를 추천드립니다',
                'reasoning': '명확한 매수 권유 표현, 목표주가 제시로 강한 확신'
            })
    
    elif channel_name == 'hyoseok':
        if 'SK하이닉스' in subtitle_text and '매수' in subtitle_text:
            signals.append({
                'speaker': '이효석',
                'stock': 'SK하이닉스',
                'ticker': '000660',
                'market': 'KR',
                'mention_type': '결론',
                'signal': '매수',
                'confidence': 'medium',
                'timestamp': '5:12',
                'key_quote': '이것은 매수 기회라고 봅니다',
                'reasoning': '매수 기회 표현하지만 조건부 뉘앙스로 medium'
            })
    
    elif channel_name == 'talent':
        if '비트코인' in subtitle_text and ('매수' in subtitle_text or '추천' in subtitle_text):
            signals.append({
                'speaker': '달란트',
                'stock': '비트코인',
                'ticker': 'BTC',
                'market': 'CRYPTO',
                'mention_type': '결론',
                'signal': '매수',
                'confidence': 'medium',
                'timestamp': '7:30',
                'key_quote': '조금씩 매수해서 포지션을 늘려가는 것을 추천합니다',
                'reasoning': '단계적 매수 추천, 강한 권유는 아니므로 medium'
            })
    
    # 부읽남은 교육 콘텐츠로 분류 (시그널 없음)
    if channel_name == 'booknam':
        signals = []  # 투자 철학 교육 → 시그널 생성 안 함
    
    analysis_result = {
        'channel': channel_name,
        'signals': signals,
        'summary': f'{channel_name} 영상 분석 완료. 총 {len(signals)}개 시그널 추출',
        'analysis_time': datetime.now().isoformat()
    }
    
    return analysis_result

def insert_to_supabase_simulation(signals):
    """Supabase 삽입 시뮬레이션"""
    
    # 실제로는 supabase-py 사용
    # supabase.table('influencer_signals').insert(signals).execute()
    
    success_count = 0
    for signal in signals:
        # 시뮬레이션: 90% 성공률
        import random
        if random.random() > 0.1:
            success_count += 1
            print(f"  ✅ {signal['speaker']} - {signal['stock']} ({signal['signal']}) 삽입 성공")
        else:
            print(f"  ❌ {signal['speaker']} - {signal['stock']} 삽입 실패")
    
    return {
        'total': len(signals),
        'success': success_count,
        'failed': len(signals) - success_count
    }

def simulate_v9_pipeline():
    """V9 파이프라인 전체 시뮬레이션"""
    
    print("V9 자막 추출 & 분석 시뮬레이션 시작")
    print("=" * 50)
    
    all_signals = []
    channel_results = {}
    
    # 4개 채널 처리
    channels = ['syuka', 'hyoseok', 'booknam', 'talent']
    
    for channel in channels:
        print(f"\n📺 {channel} 채널 처리 중...")
        
        # 1. 자막 추출 (시뮬레이션)
        subtitle = DUMMY_SUBTITLES[channel]
        print(f"📝 자막 추출 완료: {len(subtitle)}자")
        
        # 2. V9 분석
        analysis = analyze_with_v9_prompt(channel, subtitle)
        print(f"🤖 V9 분석 완료: {len(analysis['signals'])}개 시그널")
        
        # 3. 시그널 수집
        all_signals.extend(analysis['signals'])
        channel_results[channel] = analysis
        
        # 4. 60초 간격 (시뮬레이션에서는 1초)
        print("⏱️ 60초 대기 중... (시뮬레이션: 1초)")
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 분석 결과 요약")
    print("=" * 50)
    
    for channel, result in channel_results.items():
        signals_count = len(result['signals'])
        print(f"{channel:10} | {signals_count}개 시그널")
        
        for signal in result['signals']:
            print(f"           | └ {signal['speaker']} - {signal['stock']} ({signal['signal']})")
    
    print(f"\n📈 총 시그널 수: {len(all_signals)}개")
    
    # 5. Supabase 삽입 시뮬레이션
    if all_signals:
        print("\n💾 Supabase 삽입 시뮬레이션...")
        db_result = insert_to_supabase_simulation(all_signals)
        print(f"✅ 삽입 완료: {db_result['success']}/{db_result['total']} 성공")
    
    # 6. 결과 JSON 저장
    result_data = {
        'timestamp': datetime.now().isoformat(),
        'total_channels': len(channels),
        'total_signals': len(all_signals),
        'channel_results': channel_results,
        'db_insertion': db_result if all_signals else None
    }
    
    with open('v9_pipeline_result.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 결과 저장: v9_pipeline_result.json")
    
    return result_data

def main():
    """메인 실행"""
    try:
        result = simulate_v9_pipeline()
        
        print("\n🎉 V9 파이프라인 시뮬레이션 완료!")
        print(f"📊 처리 결과: {result['total_channels']}개 채널, {result['total_signals']}개 시그널")
        
        # 텔레그램 보고 메시지 생성
        report = f"""🔥 V9 파이프라인 시뮬레이션 완료!

✅ 처리된 채널: {result['total_channels']}개
📊 추출된 시그널: {result['total_signals']}개
💾 DB 삽입: {result['db_insertion']['success'] if result['db_insertion'] else 0}개 성공

채널별 결과:"""
        
        for channel, channel_result in result['channel_results'].items():
            signals_count = len(channel_result['signals'])
            report += f"\n• {channel}: {signals_count}개 시그널"
        
        report += "\n\n⏭️ 다음: 실제 YouTube 자막 추출 준비 완료"
        
        print("\n📱 텔레그램 보고 메시지:")
        print("-" * 40)
        print(report)
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    main()