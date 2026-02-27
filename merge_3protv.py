import os

files = [
    '3protv_g1.md',
    '3protv_g2.md', 
    '3protv_g3.md',
    '3protv_g4.md',
    '3protv_g5.md',
    '3protv_g6.md',
]

header = """# 삼프로TV V4 파이프라인 분석 보고서

**채널**: 삼프로TV (@3protv)
**분석 일자**: 2026-02-27
**분석 영상**: 19개 (최근 30개 중 투자 관련 필터링)
**파이프라인**: V4 (결론/논거/뉴스 분류 + 8가지 시그널)

---

"""

combined = header
for fname in files:
    path = f'C:/Users/Mario/work/{fname}'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove individual file headers, keep just the analysis
        lines = content.split('\n')
        # Skip header lines until first #### or ##
        start = 0
        for i, line in enumerate(lines):
            if line.startswith('#### ') or (line.startswith('## 영상별') and i > 0):
                start = i
                break
        combined += '\n'.join(lines[start:]) + '\n\n---\n\n'

# Also include groupB analysis
gb_path = 'C:/Users/Mario/work/3protv_groupB.md'
if os.path.exists(gb_path):
    with open(gb_path, 'r', encoding='utf-8') as f:
        gb = f.read()
    # Check if groupB has unique content not in g3/g4
    # groupB covers: hxpOT8n_ICw, R6w3T3eUVIs, WWtau8xFUU4, zdMneplXBvQ, -US4r1E1kOQ, lXxz7WJj76Y
    # These overlap with g3 (hxpOT8n_ICw, R6w3T3eUVIs) and g4 (WWtau8xFUU4, zdMneplXBvQ, -US4r1E1kOQ)
    # and g5 (lXxz7WJj76Y) - so skip groupB to avoid duplicates

with open('C:/Users/Mario/work/3protv_analysis_final.md', 'w', encoding='utf-8') as f:
    f.write(combined)

print(f'Final report: {len(combined)} chars')
