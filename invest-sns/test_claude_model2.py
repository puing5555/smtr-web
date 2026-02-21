import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# 더 많은 모델 시도
models_to_test = [
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",  
    "claude-3-5-sonnet",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku-20240307",
    "claude-3-haiku"
]

working_models = []

for model in models_to_test:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Test"}]
        )
        print(f"OK {model}")
        working_models.append(model)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"NOT FOUND {model}")
        else:
            print(f"OTHER ERROR {model}: {error_msg[:50]}")

print(f"\nWorking models: {working_models}")