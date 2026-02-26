import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from youtube_transcript_api import YouTubeTranscriptApi

videos = [
    ("fSvZbVw0ils", "코인 폭락과 코인무당에게 벗어나기"),
    ("7AaksU-R3dg", "XRP 헤어질 결심 (WLFI 마라라고 포럼 이팩트)"),
    ("ULXCspCxaSg", "CNTN이라 부르지 마세요, 이제부터 캔톤입니다!"),
    ("YxI_Tx5Y-qY", "하락장에도 버티는 내 투자는 신념일까 망상일까"),
    ("3eeUC7UBaG4", "트럼프일가와 캔톤네트워크"),
    ("oC-mHWKj8m8", "당신의 코인이 폭락해도 코인 유튜버가 영웅이 되는 이유"),
    ("A7qHwvcGh9A", "바보야 문제는 실적이야 (코인시장 붕괴의 이유)"),
    ("-brWAKvRaqI", "비트마인(BMNR)과 욕망의 삼각형"),
    ("IiPJSJ42H4o", "캔톤이 흡수한 리플 에너지"),
    ("pRTYEzspqyU", "캔톤이 흡수한 이더 에너지"),
    ("XxlsTMRDR_o", "캔톤이 흡수한 비트 에너지"),
    ("PGQW7nyoRRI", "캔톤은 기관전용 코인이다? 그건 니 생각이고~"),
    ("Vy2jrX-uCbY", "AI버블 붕괴가 와도 캔톤이 살아남는 이유"),
    ("5nfe_ZdUSoA", "미국도 희토류 없으면 개털"),
    ("_SfpKELSL70", "서학개미 환전 막아도 환율 1500 간다"),
    ("Pb_RkyKhOcM", "인사이더 인사이트를 읽고서 (금융의 본질과 캔톤)"),
    ("82TEaq8GIfc", "캔톤, 업비트 상장 초읽기"),
    ("TjKVuAGhC1M", "클래러티 법안 무기한 연기파장"),
    ("awXkJ9hK-a0", "캔톤이 다크코인? 천만의 말씀!"),
]

api = YouTubeTranscriptApi()
results = {}
for vid, title in videos:
    try:
        t = api.fetch(vid, languages=['ko'])
        text = ' '.join([x.text for x in t.snippets])
        results[vid] = {"title": title, "transcript": text[:5000], "length": len(text)}
    except Exception as e:
        results[vid] = {"title": title, "error": str(e)}
    
with open('C:/Users/Mario/work/corinpapa_transcripts.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Done. {len(results)} videos processed.")
for vid, data in results.items():
    if 'error' in data:
        print(f"  ERROR {vid}: {data['error']}")
    else:
        print(f"  OK {vid}: {data['title']} ({data['length']} chars)")
