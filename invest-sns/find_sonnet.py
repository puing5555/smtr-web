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

# Sonnet 모델들 시도
sonnet_models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-v2",
    "claude-3-5-sonnet",
    "claude-3-sonnet-20240229"
]

working_model = None

for model in sonnet_models:
    try:
        print(f"Testing Sonnet model: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=20,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print(f"SUCCESS with Sonnet model: {model}")
        working_model = model
        break
    except Exception as e:
        print(f"FAILED: {model}")

if working_model:
    print(f"Working Sonnet model found: {working_model}")
else:
    print("No working Sonnet model found. Will use Haiku as fallback.")
    working_model = "claude-3-haiku-20240307"

print(f"Final model to use: {working_model}")