#!/usr/bin/env python3
import os
import anthropic

# API 키 로드
env_path = r"C:\Users\Mario\work\invest-engine\.env"
api_key = None

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('ANTHROPIC_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break

client = anthropic.Anthropic(api_key=api_key)

# 다양한 모델명 시도
models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet",
    "claude-3-sonnet-20240229"
]

for model in models:
    try:
        print(f"Testing: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Test"}]
        )
        print(f"✅ SUCCESS with {model}")
        print(f"Response: {response.content[0].text}")
        break
    except Exception as e:
        print(f"❌ FAILED: {model} - {e}")