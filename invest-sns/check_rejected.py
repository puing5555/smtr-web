import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('smtr_data/corinpapa1106/_review_results.json','r',encoding='utf-8') as f:
    reviews = json.load(f)
with open('smtr_data/corinpapa1106/_deduped_signals_8types_dated.json','r',encoding='utf-8') as f:
    signals = json.load(f)

rejected = {k:v for k,v in reviews.items() if v['status']=='rejected'}
print(f"거부된 시그널: {len(rejected)}개\n")

for sig_id, rev in rejected.items():
    matched = [s for s in signals if s.get('video_id','')+'_'+s.get('asset','') == sig_id]
    sig = matched[0] if matched else {}
    asset = sig.get('asset', '?')
    stype = sig.get('signal_type', '?')
    date = sig.get('date', '?')
    content = (sig.get('content', '?') or '?')[:120]
    reason = rev.get('reason', '')
    title = (sig.get('title', '') or '')[:50]
    print(f"[{sig_id}]")
    print(f"  종목: {asset} | 시그널: {stype} | 날짜: {date}")
    print(f"  영상: {title}")
    print(f"  내용: {content}")
    print(f"  거부사유: {reason}")
    print()
