#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple database connection test
"""

import requests

# Supabase configuration
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

# Headers for Supabase API
HEADERS = {
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "apikey": SUPABASE_SERVICE_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

print("Testing Supabase database connection...")

try:
    # Test basic connection
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {
        "select": "*",
        "limit": "5"
    }
    
    print("Sending request to Supabase...")
    response = requests.get(url, headers=HEADERS, params=params, timeout=30)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Retrieved {len(data)} records")
        
        # Print columns available
        if data:
            print(f"Available columns: {list(data[0].keys())}")
            print()
        
        for item in data:
            print(f"Video ID: {item['video_id']}")
            print(f"Title: {item.get('title', 'N/A')}")
            print(f"Channel: {item.get('channel', 'N/A')}")
            print(f"Has subtitle: {item.get('has_subtitle', 'N/A')}")
            summary = item.get('video_summary')
            if summary:
                print(f"Summary: {summary[:100]}...")
            else:
                print(f"Summary: NULL")
            subtitle = item.get('subtitle_text')
            if subtitle:
                print(f"Subtitle: {subtitle[:50]}...")
            else:
                print(f"Subtitle: NULL")
            print("---")
    else:
        print(f"Failed with status {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Database test complete.")