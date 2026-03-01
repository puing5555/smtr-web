# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict

def detailed_analysis():
    print("=== Detailed Signal Analysis for V10 Planning ===")
    
    with open('pipeline_v9_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all signals
    all_signals = []
    for video in data:
        if video.get('signals'):
            for signal in video['signals']:
                signal['video_title'] = video.get('title', '')
                signal['video_summary'] = video.get('summary', '')
                signal['channel_name'] = video['channel']['name']
                all_signals.append(signal)
    
    print(f"Total signals found: {len(all_signals)}")
    
    # Display all signals with details
    print("\n=== All Signal Details ===")
    for i, signal in enumerate(all_signals, 1):
        print(f"\n{i}. SIGNAL DETAILS:")
        print(f"   Speaker: {signal.get('speaker', 'N/A')}")
        print(f"   Channel: {signal.get('channel_name', 'N/A')}")
        print(f"   Stock: {signal.get('stock', 'N/A')}")
        print(f"   Ticker: {signal.get('ticker', 'N/A')}")
        print(f"   Market: {signal.get('market', 'N/A')}")
        print(f"   Signal: {signal.get('signal', 'N/A')}")
        print(f"   Mention Type: {signal.get('mention_type', 'N/A')}")
        print(f"   Confidence: {signal.get('confidence', 'N/A')}")
        print(f"   Timestamp: {signal.get('timestamp', 'N/A')}")
        print(f"   Key Quote: {signal.get('key_quote', 'N/A')}")
        print(f"   Reasoning: {signal.get('reasoning', 'N/A')}")
    
    # Analyze potential issues for V10
    print("\n=== Potential Issues for V10 Improvement ===")
    
    # 1. Check mention_type vs signal consistency
    print("\n1. Mention_type vs Signal Consistency:")
    conclusion_signals = [s for s in all_signals if s.get('mention_type') == '결론']
    argument_signals = [s for s in all_signals if s.get('mention_type') == '논거']
    
    print(f"   결론 (Conclusion) signals: {len(conclusion_signals)}")
    for signal in conclusion_signals:
        print(f"      - {signal.get('speaker')}: {signal.get('stock')} = {signal.get('signal')}")
    
    print(f"   논거 (Argument) signals: {len(argument_signals)}")  
    for signal in argument_signals:
        print(f"      - {signal.get('speaker')}: {signal.get('stock')} = {signal.get('signal')}")
    
    # 2. Check confidence vs mention_type
    print("\n2. Confidence vs Mention_type Analysis:")
    for signal in all_signals:
        mention_type = signal.get('mention_type', '')
        confidence = signal.get('confidence', '')
        signal_type = signal.get('signal', '')
        
        # Check if 논거 should not be 매수
        if mention_type == '논거' and signal_type == '매수':
            print(f"   [ISSUE] 논거 but 매수 signal: {signal.get('speaker')} - {signal.get('stock')}")
        
        # Check if high confidence is appropriate
        if confidence == 'high' and mention_type == '논거':
            print(f"   [REVIEW] High confidence for 논거: {signal.get('speaker')} - {signal.get('stock')}")
    
    # 3. Speaker name consistency
    print("\n3. Speaker Name Analysis:")
    speakers = Counter(s.get('speaker') for s in all_signals)
    channels = Counter(s.get('channel_name') for s in all_signals)
    
    print(f"   Speakers: {dict(speakers)}")
    print(f"   Channels: {dict(channels)}")
    
    # Check for potential speaker normalization issues
    speaker_list = list(speakers.keys())
    print("\n   Potential speaker normalization issues:")
    for i, speaker1 in enumerate(speaker_list):
        for speaker2 in speaker_list[i+1:]:
            if speaker1 and speaker2:
                # Simple similarity check
                if any(name in speaker2 for name in speaker1.split()) or any(name in speaker1 for name in speaker2.split()):
                    print(f"      - Similar names: '{speaker1}' vs '{speaker2}'")
    
    # 4. Key quote quality analysis
    print("\n4. Key Quote Quality Analysis:")
    quotes_by_length = defaultdict(list)
    for signal in all_signals:
        quote = signal.get('key_quote', '')
        length = len(quote.strip())
        quotes_by_length[length].append(signal)
    
    print("   Quote length distribution:")
    for length in sorted(quotes_by_length.keys()):
        count = len(quotes_by_length[length])
        print(f"      {length} chars: {count} signals")
        if length < 20:  # Short quotes
            for signal in quotes_by_length[length]:
                print(f"         - {signal.get('speaker')}: '{signal.get('key_quote', '')}'")
    
    # 5. Market distribution and V9 scope compliance
    print("\n5. Market Scope Analysis (V9 scope: KR + US + CRYPTO only):")
    markets = Counter(s.get('market') for s in all_signals)
    v9_allowed_markets = {'KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI', 'SECTOR', 'INDEX', 'ETF', 'OTHER'}
    v9_scope_markets = {'KR', 'US', 'US_ADR', 'CRYPTO', 'CRYPTO_DEFI'}
    
    for market, count in markets.most_common():
        if market not in v9_allowed_markets:
            status = "[ERROR] Invalid market"
        elif market not in v9_scope_markets:
            status = "[WARNING] Outside V9 scope"
        else:
            status = "[OK] V9 compliant"
        print(f"      {status}: {market} - {count} signals")

if __name__ == "__main__":
    detailed_analysis()