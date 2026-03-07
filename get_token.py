import re, os
config_path = os.path.expanduser(r'~/.openclaw/openclaw.json')
with open(config_path, 'r') as f:
    raw = f.read()
token_match = re.search(r"token:\s*'([^']+)'", raw)
if token_match:
    print('TOKEN:', token_match.group(1))
else:
    print('NO TOKEN FOUND')
