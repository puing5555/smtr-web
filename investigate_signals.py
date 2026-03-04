#!/usr/bin/env python3
"""
Investigate signals more thoroughly
"""

import requests

# Configuration
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

def investigate_signals():
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_ROLE_KEY
    }
    base_url = f"{SUPABASE_URL}/rest/v1"
    url = f"{base_url}/influencer_signals"
    
    print("Investigating signal data...")
    
    # Get all signals with various conditions
    params = {
        "select": "id,stock,signal,key_quote,reasoning",
        "limit": 1000
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch signals: {response.status_code}")
        return
    
    signals = response.json()
    total = len(signals)
    print(f"Total signals: {total}")
    
    # Analyze different conditions
    null_reasoning = 0
    empty_reasoning = 0
    short_reasoning = 0
    null_key_quote = 0
    empty_key_quote = 0
    short_key_quote = 0
    
    reasoning_lengths = []
    key_quote_lengths = []
    
    candidates_for_enhancement = []
    
    for signal in signals:
        reasoning = signal.get('reasoning')
        key_quote = signal.get('key_quote')
        
        # Check reasoning
        if reasoning is None:
            null_reasoning += 1
        elif reasoning == '':
            empty_reasoning += 1
        else:
            reasoning_lengths.append(len(reasoning))
            if len(reasoning) < 100:
                short_reasoning += 1
        
        # Check key_quote
        if key_quote is None:
            null_key_quote += 1
        elif key_quote == '':
            empty_key_quote += 1
        else:
            key_quote_lengths.append(len(key_quote))
            if len(key_quote) < 50:
                short_key_quote += 1
        
        # Check if signal needs enhancement
        reasoning_text = reasoning or ''
        key_quote_text = key_quote or ''
        
        needs_reasoning = len(reasoning_text) < 100
        needs_key_quote = len(key_quote_text) < 50
        
        if needs_reasoning or needs_key_quote:
            candidates_for_enhancement.append({
                'id': signal['id'],
                'stock': signal['stock'],
                'signal': signal['signal'],
                'reasoning_len': len(reasoning_text),
                'key_quote_len': len(key_quote_text),
                'needs_reasoning': needs_reasoning,
                'needs_key_quote': needs_key_quote,
                'reasoning': reasoning_text[:100] + '...' if len(reasoning_text) > 100 else reasoning_text,
                'key_quote': key_quote_text[:50] + '...' if len(key_quote_text) > 50 else key_quote_text
            })
    
    print(f"\nReasoning Analysis:")
    print(f"   - Null reasoning: {null_reasoning}")
    print(f"   - Empty reasoning: {empty_reasoning}")
    print(f"   - Reasoning < 100 chars: {short_reasoning}")
    if reasoning_lengths:
        print(f"   - Min reasoning length: {min(reasoning_lengths)}")
        print(f"   - Max reasoning length: {max(reasoning_lengths)}")
        print(f"   - Average reasoning length: {sum(reasoning_lengths)/len(reasoning_lengths):.1f}")
    
    print(f"\nKey Quote Analysis:")
    print(f"   - Null key_quote: {null_key_quote}")
    print(f"   - Empty key_quote: {empty_key_quote}")
    print(f"   - Key quote < 50 chars: {short_key_quote}")
    if key_quote_lengths:
        print(f"   - Min key_quote length: {min(key_quote_lengths)}")
        print(f"   - Max key_quote length: {max(key_quote_lengths)}")
        print(f"   - Average key_quote length: {sum(key_quote_lengths)/len(key_quote_lengths):.1f}")
    
    print(f"\nEnhancement Candidates: {len(candidates_for_enhancement)}")
    
    if candidates_for_enhancement:
        print(f"\nFirst 10 candidates:")
        for i, candidate in enumerate(candidates_for_enhancement[:10]):
            print(f"\n{i+1}. ID: {candidate['id']}")
            print(f"   Stock: {candidate['stock']}")
            print(f"   Signal: {candidate['signal']}")
            print(f"   Reasoning ({candidate['reasoning_len']} chars): {candidate['reasoning']}")
            print(f"   Key Quote ({candidate['key_quote_len']} chars): {candidate['key_quote']}")
            print(f"   Needs reasoning: {candidate['needs_reasoning']}")
            print(f"   Needs key_quote: {candidate['needs_key_quote']}")
    
    # Check for specific patterns that might indicate empty/placeholder content
    placeholder_patterns = ['', 'N/A', 'null', 'None', '-']
    reasoning_with_placeholders = 0
    key_quote_with_placeholders = 0
    
    for signal in signals:
        reasoning = signal.get('reasoning', '') or ''
        key_quote = signal.get('key_quote', '') or ''
        
        if reasoning.lower().strip() in [p.lower() for p in placeholder_patterns]:
            reasoning_with_placeholders += 1
        if key_quote.lower().strip() in [p.lower() for p in placeholder_patterns]:
            key_quote_with_placeholders += 1
    
    print(f"\nPlaceholder Content:")
    print(f"   - Reasoning with placeholders: {reasoning_with_placeholders}")
    print(f"   - Key quotes with placeholders: {key_quote_with_placeholders}")
    
    return candidates_for_enhancement

if __name__ == "__main__":
    candidates = investigate_signals()
    
    if candidates:
        print(f"\n*** READY TO ENHANCE {len(candidates)} SIGNALS ***")
    else:
        print(f"\n*** NO SIGNALS NEED ENHANCEMENT ***")