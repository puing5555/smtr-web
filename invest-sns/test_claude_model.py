#!/usr/bin/env python3
"""
Claude 모델 테스트 스크립트
"""
import os
import anthropic

# .env 파일에서 API 키 읽기
env_path = r"C:\Users\Mario\work\invest-engine\.env"
api_key = None

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('ANTHROPIC_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break

if not api_key:
    print("ANTHROPIC_API_KEY not found")
    exit(1)

# 클라이언트 생성
client = anthropic.Anthropic(api_key=api_key)

# 여러 모델명 시도
models_to_test = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229"
]

for model in models_to_test:
    try:
        print(f"Testing model: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=0.1,
            messages=[{
                "role": "user",
                "content": "Hello, please respond with 'Model working'"
            }]
        )
        print(f"✅ {model}: SUCCESS - {response.content[0].text}")
        break
    except Exception as e:
        print(f"❌ {model}: FAILED - {e}")

print("Model test completed.")