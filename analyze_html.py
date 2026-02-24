import re

# Read HTML file
with open(r'C:\Users\Mario\work\invest-sns\signal-review-v3.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all fetch calls
fetch_pattern = r'fetch\([^)]+\)'
fetches = re.findall(fetch_pattern, content)

print("Found fetch calls:")
for i, fetch in enumerate(fetches):
    print(f"{i+1}: {fetch}")

# Find script sections that might contain API calls
script_sections = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"\nFound {len(script_sections)} script sections")

# Look for localhost references
localhost_refs = re.findall(r'localhost:\d+[^"\'\s]*', content)
print(f"\nLocalhost references:")
for ref in localhost_refs:
    print(f"  {ref}")

# Find async function definitions
async_functions = re.findall(r'async\s+function\s+\w+[^{]+{', content)
print(f"\nAsync functions:")
for func in async_functions:
    print(f"  {func}")