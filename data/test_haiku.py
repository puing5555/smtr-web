import requests, json
r = requests.post('https://api.anthropic.com/v1/messages',
    headers={'x-api-key': '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',
             'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
    json={'model': 'claude-3-haiku-20240307', 'max_tokens': 100, 'messages': [{'role': 'user', 'content': 'Say hello'}]},
    timeout=30)
print(r.status_code)
print(r.text[:500])
