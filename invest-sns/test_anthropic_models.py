#!/usr/bin/env python3
"""Anthropic 모델 테스트"""
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# 여러 모델명 시도
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest", 
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229"
]

for model in models_to_try:
    try:
        print(f"Testing model: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=0,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print(f"  SUCCESS: {response.content[0].text[:50]}...")
        break
    except Exception as e:
        print(f"  FAILED: {e}")

print("Done.")