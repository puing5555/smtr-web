#!/usr/bin/env python3
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(os.path.join('C:\\Users\\Mario\\work\\invest-engine', '.env'))

api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"API key found: {'Yes' if api_key else 'No'}")
print(f"API key starts with: {api_key[:10] if api_key else 'None'}...")

try:
    client = Anthropic(api_key=api_key)
    
    # Try simplest model name
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello, just say 'working' in Korean."}]
    )
    
    print("Success!")
    print(response.content[0].text)
    
except Exception as e:
    print(f"Error: {e}")
    
    # Try different model
    try:
        print("Trying different model...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello, just say 'working' in Korean."}]
        )
        
        print("Success with Haiku!")
        print(response.content[0].text)
    except Exception as e2:
        print(f"Haiku also failed: {e2}")