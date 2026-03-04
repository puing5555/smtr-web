import requests, json, time, os, sys

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
ANTHROPIC_KEY = "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"

HEADERS_SB = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

def fetch_all_signals():
    """Fetch all signals with video titles"""
    signals = []
    offset = 0
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id,video_id,stock,ticker,signal,key_quote,reasoning,confidence&order=id&offset={offset}&limit=1000",
            headers={**HEADERS_SB, "Prefer": "count=exact"}
        )
        data = r.json()
        if not data:
            break
        signals.extend(data)
        if len(data) < 1000:
            break
        offset += 1000
    
    # Fetch video titles
    video_ids = list(set(s['video_id'] for s in signals if s.get('video_id')))
    video_map = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        ids_str = ",".join(f'"{v}"' for v in batch)
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_videos?select=id,title,channel_id&id=in.({','.join(batch)})",
            headers=HEADERS_SB
        )
        for v in r.json():
            video_map[v['id']] = v
    
    for s in signals:
        vid = video_map.get(s.get('video_id'), {})
        s['_title'] = vid.get('title', '제목없음')
        s['_channel_id'] = vid.get('channel_id', 'unknown')
    
    return signals

def call_anthropic(model, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            if r.status_code == 429:
                print(f"  429 rate limit, waiting 30s (attempt {attempt+1})")
                time.sleep(30)
                continue
            r.raise_for_status()
            text = r.json()['content'][0]['text']
            # Parse JSON from response
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON
            import re
            m = re.search(r'\{[^}]+\}', text)
            if m:
                return json.loads(m.group())
            return {"relevance": "?", "opinion": "?", "evidence": "?", "verdict": "불량", "reason": "JSON 파싱 실패"}
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Error: {e}, retrying in 10s")
                time.sleep(10)
            else:
                return {"relevance": "?", "opinion": "?", "evidence": "?", "verdict": "불량", "reason": f"API 오류: {str(e)[:50]}"}

def make_prompt(s):
    return f"""다음 시그널의 품질을 검증하세요.

영상 제목: {s['_title']}
시그널 종목: {s['stock']} ({s['ticker']})
시그널 타입: {s['signal']}
핵심 발언: {s.get('key_quote', '')}
근거: {s.get('reasoning', '')}
confidence: {s.get('confidence', '')}

판정 항목 (각각 O 또는 X):
1. 종목관련성: 영상 제목/주제와 시그널 종목이 관련 있는가?
2. 투자의견: key_quote가 해당 종목에 대한 실제 투자 의견(매수/매도/전망)인가? (단순 언급은 X)
3. 근거충분: reasoning이 구체적 근거를 포함하는가?

최종판정: 정상 / 의심 / 불량

JSON으로만 응답:
{{"relevance": "O", "opinion": "O", "evidence": "O", "verdict": "정상", "reason": "한줄 사유"}}"""

def log_telegram(msg):
    """Print and flush for the main agent to pick up"""
    try:
        print(f"[TG] {msg}", flush=True)
    except UnicodeEncodeError:
        print(f"[TG] {msg.encode('utf-8', errors='replace').decode('utf-8')}", flush=True)

def main():
    print("=== Fetching signals from DB ===", flush=True)
    signals = fetch_all_signals()
    total = len(signals)
    print(f"Fetched {total} signals", flush=True)
    log_telegram(f"🔍 [QA] 1단계 Haiku 검증 시작: 총 {total}개")

    # Phase 1: Haiku
    results = []
    input_tokens_1 = 0
    output_tokens_1 = 0
    
    # Check for checkpoint
    checkpoint_file = "data/qa_checkpoint.json"
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
            results = checkpoint.get('results', [])
            print(f"Resumed from checkpoint: {len(results)} already done", flush=True)
    
    done_ids = set(r['id'] for r in results)
    
    for i, s in enumerate(signals):
        if s['id'] in done_ids:
            continue
        
        prompt = make_prompt(s)
        verdict = call_anthropic("claude-3-haiku-20240307", prompt)
        
        results.append({
            "id": s['id'],
            "stock": s['stock'],
            "ticker": s.get('ticker', ''),
            "signal": s.get('signal', ''),
            "key_quote": s.get('key_quote', ''),
            "video_title": s['_title'],
            "channel_id": s.get('_channel_id', 'unknown'),
            "haiku_verdict": verdict.get('verdict', '불량'),
            "haiku_reason": verdict.get('reason', ''),
            "haiku_detail": verdict,
            "sonnet_verdict": None,
            "final_verdict": verdict.get('verdict', '불량'),
            "reason": verdict.get('reason', '')
        })
        
        time.sleep(0.5)
        
        count = len(results)
        if count % 100 == 0:
            log_telegram(f"🔍 [QA] 1단계 Haiku 검증 진행: {count}/{total}")
            # Save checkpoint
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump({"results": results}, f, ensure_ascii=False)
        
        if count % 10 == 0:
            print(f"  Progress: {count}/{total}", flush=True)
    
    # Phase 1 stats
    h_normal = sum(1 for r in results if r['haiku_verdict'] == '정상')
    h_suspect = sum(1 for r in results if r['haiku_verdict'] == '의심')
    h_bad = sum(1 for r in results if r['haiku_verdict'] == '불량')
    log_telegram(f"🔍 [QA] 1단계 완료: 정상 {h_normal} / 의심 {h_suspect} / 불량 {h_bad}")
    
    # Phase 2: Sonnet for suspect/bad
    need_sonnet = [r for r in results if r['haiku_verdict'] in ('의심', '불량')]
    log_telegram(f"🔍 [QA] 2단계 Sonnet: {len(need_sonnet)}건 재확인 시작")
    
    signal_map = {s['id']: s for s in signals}
    
    for i, r in enumerate(need_sonnet):
        s = signal_map.get(r['id'])
        if not s:
            continue
        prompt = make_prompt(s)
        verdict = call_anthropic("claude-sonnet-4-20250514", prompt)
        
        r['sonnet_verdict'] = verdict.get('verdict', '불량')
        r['sonnet_detail'] = verdict
        r['final_verdict'] = verdict.get('verdict', '불량')
        r['reason'] = verdict.get('reason', r['reason'])
        
        time.sleep(0.5)
        
        if (i+1) % 50 == 0:
            log_telegram(f"🔍 [QA] 2단계 Sonnet 진행: {i+1}/{len(need_sonnet)}")
            print(f"  Sonnet progress: {i+1}/{len(need_sonnet)}", flush=True)
    
    # Final stats
    f_normal = sum(1 for r in results if r['final_verdict'] == '정상')
    f_suspect = sum(1 for r in results if r['final_verdict'] == '의심')
    f_bad = sum(1 for r in results if r['final_verdict'] == '불량')
    
    # Flipped count
    flipped = sum(1 for r in results if r['sonnet_verdict'] and r['sonnet_verdict'] != r['haiku_verdict'])
    
    # Channel stats
    channel_stats = {}
    for r in results:
        ch = r.get('channel_id', 'unknown')
        if ch not in channel_stats:
            channel_stats[ch] = {'total': 0, 'bad': 0, 'suspect': 0}
        channel_stats[ch]['total'] += 1
        if r['final_verdict'] == '불량':
            channel_stats[ch]['bad'] += 1
        elif r['final_verdict'] == '의심':
            channel_stats[ch]['suspect'] += 1
    
    # Cost estimate
    haiku_cost = total * 400 / 1_000_000 * 0.25 + total * 100 / 1_000_000 * 1.25  # input + output
    sonnet_input = len(need_sonnet) * 400 / 1_000_000 * 3.0
    sonnet_output = len(need_sonnet) * 100 / 1_000_000 * 15.0
    total_cost = haiku_cost + sonnet_input + sonnet_output
    
    # Save results
    os.makedirs("data", exist_ok=True)
    
    # Clean results for JSON (remove internal fields)
    clean_results = []
    for r in results:
        clean_results.append({
            "id": r['id'],
            "stock": r['stock'],
            "ticker": r.get('ticker', ''),
            "video_title": r.get('video_title', ''),
            "channel_id": r.get('channel_id', ''),
            "haiku_verdict": r['haiku_verdict'],
            "sonnet_verdict": r['sonnet_verdict'],
            "final_verdict": r['final_verdict'],
            "reason": r['reason']
        })
    
    with open("data/signal_quality_full_audit.json", 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, ensure_ascii=False, indent=2)
    
    # Defects markdown
    defects_md = f"""# 시그널 품질 검증 결과

## 통계 요약
- 총 시그널: {total}개
- **1단계 Haiku**: 정상 {h_normal} / 의심 {h_suspect} / 불량 {h_bad}
- **2단계 Sonnet**: {len(need_sonnet)}건 재확인, {flipped}건 판정 변경
- **최종**: 정상 {f_normal} / 의심 {f_suspect} / 불량 {f_bad}
- **추정 비용**: ${total_cost:.2f}

## 채널별 불량률
| 채널 | 총 시그널 | 불량 | 의심 | 불량률 |
|------|----------|------|------|--------|
"""
    for ch, st in sorted(channel_stats.items(), key=lambda x: x[1]['bad'], reverse=True):
        rate = (st['bad'] / st['total'] * 100) if st['total'] > 0 else 0
        defects_md += f"| {ch} | {st['total']} | {st['bad']} | {st['suspect']} | {rate:.1f}% |\n"
    
    defects_md += "\n## 불량 시그널 상세\n\n"
    for r in results:
        if r['final_verdict'] == '불량':
            defects_md += f"### {r['stock']} ({r.get('ticker','')})\n"
            defects_md += f"- ID: `{r['id']}`\n"
            defects_md += f"- 영상: {r.get('video_title','')}\n"
            defects_md += f"- key_quote: {r.get('key_quote','')[:100]}\n"
            defects_md += f"- 사유: {r['reason']}\n\n"
    
    defects_md += "\n## 의심 시그널 상세\n\n"
    for r in results:
        if r['final_verdict'] == '의심':
            defects_md += f"### {r['stock']} ({r.get('ticker','')})\n"
            defects_md += f"- ID: `{r['id']}`\n"
            defects_md += f"- 영상: {r.get('video_title','')}\n"
            defects_md += f"- key_quote: {r.get('key_quote','')[:100]}\n"
            defects_md += f"- 사유: {r['reason']}\n\n"
    
    with open("data/signal_defects.md", 'w', encoding='utf-8') as f:
        f.write(defects_md)
    
    summary = f"""🔍 [QA] 전체 검증 완료!

📊 1단계 Haiku: 정상 {h_normal} / 의심 {h_suspect} / 불량 {h_bad}
🔬 2단계 Sonnet: {len(need_sonnet)}건 재확인, {flipped}건 판정 변경
✅ 최종: 정상 {f_normal} / 의심 {f_suspect} / 불량 {f_bad}
💰 비용: ~${total_cost:.2f}"""
    
    log_telegram(summary)
    print("\n" + summary, flush=True)
    print("\nFiles saved: data/signal_quality_full_audit.json, data/signal_defects.md", flush=True)
    
    # Clean up checkpoint
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

if __name__ == "__main__":
    main()
