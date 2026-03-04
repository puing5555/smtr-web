#!/usr/bin/env python3
"""
Test database connection and count signals needing enhancement
"""

import requests

# Configuration
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

def test_connection_and_count():
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_ROLE_KEY
    }
    base_url = f"{SUPABASE_URL}/rest/v1"
    
    # Test basic connection
    print("Testing database connection...")
    url = f"{base_url}/influencer_signals"
    params = {
        "select": "count",
        "limit": 1
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Database connection failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print("Database connection successful!")
    
    # Get sample data to understand structure
    print("\nFetching sample signals...")
    params = {
        "select": "id,stock,ticker,signal,key_quote,reasoning",
        "limit": 5
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        signals = response.json()
        print(f"Sample signals retrieved: {len(signals)}")
        
        for signal in signals:
            reasoning = signal.get('reasoning', '') or ''
            key_quote = signal.get('key_quote', '') or ''
            
            print(f"\nSignal ID: {signal['id']}")
            print(f"Stock: {signal['stock']}")
            print(f"Signal: {signal['signal']}")
            print(f"Reasoning length: {len(reasoning)} chars")
            print(f"Key quote length: {len(key_quote)} chars")
            print(f"Needs reasoning enhancement: {len(reasoning) < 100}")
            print(f"Needs key_quote enhancement: {len(key_quote) < 50}")
    
    # Count signals needing enhancement
    print("\nCounting signals needing enhancement...")
    
    # Get all signals to count manually (since Supabase query might be complex)
    params = {
        "select": "id,reasoning,key_quote",
        "limit": 1000  # Adjust if needed
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        all_signals = response.json()
        total_signals = len(all_signals)
        
        reasoning_needs_enhancement = 0
        key_quote_needs_enhancement = 0
        both_need_enhancement = 0
        
        for signal in all_signals:
            reasoning = signal.get('reasoning', '') or ''
            key_quote = signal.get('key_quote', '') or ''
            
            needs_reasoning = len(reasoning) < 100
            needs_key_quote = len(key_quote) < 50
            
            if needs_reasoning:
                reasoning_needs_enhancement += 1
            if needs_key_quote:
                key_quote_needs_enhancement += 1
            if needs_reasoning and needs_key_quote:
                both_need_enhancement += 1
        
        signals_needing_enhancement = len([s for s in all_signals if 
                                         len(s.get('reasoning', '') or '') < 100 or 
                                         len(s.get('key_quote', '') or '') < 50])
        
        print(f"\nEnhancement Statistics:")
        print(f"   - Total signals in DB: {total_signals}")
        print(f"   - Signals needing reasoning enhancement: {reasoning_needs_enhancement}")
        print(f"   - Signals needing key_quote enhancement: {key_quote_needs_enhancement}")
        print(f"   - Signals needing both: {both_need_enhancement}")
        print(f"   - Total signals needing enhancement: {signals_needing_enhancement}")
        
        # Cost estimation
        estimated_tokens_per_call = 450  # 250 input + 200 output
        estimated_calls = reasoning_needs_enhancement + key_quote_needs_enhancement
        estimated_cost = (estimated_calls * estimated_tokens_per_call * 3) / 1000000  # Sonnet pricing
        
        print(f"\nCost Estimation:")
        print(f"   - Estimated API calls: {estimated_calls}")
        print(f"   - Estimated tokens: {estimated_calls * estimated_tokens_per_call:,}")
        print(f"   - Estimated cost: ${estimated_cost:.2f}")

if __name__ == "__main__":
    test_connection_and_count()