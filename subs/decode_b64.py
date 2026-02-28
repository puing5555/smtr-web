import base64, json, sys

b64_file = sys.argv[1]
out_file = sys.argv[2]

with open(b64_file, 'r') as f:
    b64 = f.read().strip()

data = json.loads(base64.b64decode(b64).decode('utf-8'))
print(f"Segments: {len(data['subtitles'])}")

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Saved to {out_file}")
