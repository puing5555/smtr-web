"""
A/B Test: V10.10 (단일) vs V10.11 (2단계)
"""
import json, os, time, random, re, sys
from pathlib import Path
from datetime import datetime

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx

# === Config ===
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
MODEL = "claude-sonnet-4-20250514"
MAX_COST = 10.0
SAMPLE_SIZE = 30
MAX_SUB_CHARS = 12000
OUTPUT_DIR = Path("C:/Users/Mario/work/data/research")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load API key from .env.local
def load_api_key():
    for line in Path("C:/Users/Mario/work/invest-sns/.env.local").read_text().splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    return os.environ.get("ANTHROPIC_API_KEY", "")

ANTHROPIC_KEY = load_api_key()
INPUT_CPT = 3.0 / 1_000_000
OUTPUT_CPT = 15.0 / 1_000_000

# === Prompts ===
PROMPT_A = """당신은 투자 자막 분석 전문가입니다. 아래 자막에서 투자 시그널을 추출하세요.

채널: {channel_name} | 제목: {video_title}
자막:
{subtitle}

## 시그널 5단계만 사용: 매수/긍정/중립/부정/매도
- 매수: "사라, 담아라" 등 명확한 매수 액션
- 긍정: "좋아보인다" 등 호의적이나 매수 권유 아님
- 중립: 뉴스/리포트/교육 전달
- 부정/매도: 각각 부정적/명확한 매도

## 매수 vs 긍정: "본인이 샀거나 사라고 했는가?" Yes=매수, No=긍정

## 규칙
- 1영상 1종목 1시그널, key_quote에 종목명 필수, 20자+, 타임스탬프 필수
- 한국/미국주식/크립토만, 교육/뉴스만이면 시그널 없음
- 논거 종목은 최대 긍정까지

JSON만 출력:
{{"signals": [{{"speaker":"","stock_name":"","stock_code":"","market":"","mention_type":"","signal_type":"","confidence":"","timestamp":"","key_quote":"","reasoning":""}}]}}
시그널 없으면 {{"signals": []}}"""

PROMPT_B1 = """아래 자막에서 언급된 투자 종목만 추출하세요.

채널: {channel_name} | 제목: {video_title}
자막:
{subtitle}

규칙: 한국/미국주식/크립토만, 정식 종목명, 지수 제외, 비종목 제외

JSON만:
{{"stocks": [{{"stock_name":"","stock_code":"","market":""}}]}}
종목 없으면 {{"stocks": []}}"""

PROMPT_B2 = """아래 자막에서 **{stock_name}**에 대한 투자 시그널을 판단하세요.

채널: {channel_name} | 제목: {video_title}
자막:
{subtitle}

## 시그널: 매수/긍정/중립/부정/매도
매수 vs 긍정: "본인이 샀거나 사라고 했는가?" Yes=매수, No=긍정
- 매수: 본인 매매 공개, "사라/담아라", 포트폴리오 편입, 분할매수 지시
- 긍정: "좋아보인다", "관심가져라", "전망 밝다", 분석만 제공

규칙: 논거→최대긍정, 교육/뉴스→시그널없음, key_quote에 종목명+근거 20자+, 타임스탬프 필수

JSON만:
{{"signal": {{"speaker":"","stock_name":"","stock_code":"","market":"","mention_type":"","signal_type":"","confidence":"","timestamp":"","key_quote":"","reasoning":""}}}}
시그널 없으면 {{"signal": null, "reason": ""}}"""

# === Helpers ===
class Cost:
    def __init__(self):
        self.inp = 0; self.out = 0; self.calls = 0
    @property
    def usd(self): return self.inp * INPUT_CPT + self.out * OUTPUT_CPT
    def add(self, i, o): self.inp += i; self.out += o; self.calls += 1

client = httpx.Client(timeout=180)

def claude(prompt, cost, max_tokens=2000):
    print(f"    [claude] calling, prompt_len={len(prompt)}...", flush=True)
    for attempt in range(3):
        try:
            r = client.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": MODEL, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]})
            if r.status_code == 429:
                w = min(60, 2**attempt * 10)
                print(f"  rate limited, wait {w}s")
                time.sleep(w); continue
            if r.status_code == 529:
                print(f"  overloaded, wait 30s")
                time.sleep(30); continue
            r.raise_for_status()
            d = r.json()
            cost.add(d["usage"]["input_tokens"], d["usage"]["output_tokens"])
            if cost.usd > MAX_COST / 2:
                raise Exception(f"Budget exceeded: ${cost.usd:.2f}")
            return d["content"][0]["text"]
        except httpx.HTTPStatusError as e:
            if attempt == 2: raise
            time.sleep(5)
    return None

def parse_json(text):
    if not text: return None
    for pat in [r'```json\s*(.*?)\s*```', r'```\s*(.*?)\s*```', r'(\{.*\})']:
        m = re.search(pat, text, re.DOTALL)
        if m:
            try: return json.loads(m.group(1))
            except: continue
    try: return json.loads(text)
    except: return None

def fetch_videos():
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    ch = httpx.get(f"{SUPABASE_URL}/rest/v1/influencer_channels?select=id,channel_name", headers=h).json()
    ch_map = {c["id"]: c["channel_name"] for c in ch}
    
    vids = httpx.get(f"{SUPABASE_URL}/rest/v1/influencer_videos?select=id,video_id,title,channel_id,subtitle_text&has_subtitle=eq.true&limit=500&order=published_at.desc", headers=h).json()
    vids = [v for v in vids if v.get("subtitle_text") and len(v["subtitle_text"]) > 500]
    for v in vids:
        v["channel_name"] = ch_map.get(v.get("channel_id"), "unknown")
        v["subtitle"] = v.pop("subtitle_text", "")
    print(f"Found {len(vids)} videos with subtitles")
    if len(vids) > SAMPLE_SIZE:
        vids = random.sample(vids, SAMPLE_SIZE)
    return vids

def trunc(s, n=MAX_SUB_CHARS):
    return s[:n] + "\n...(잘림)" if len(s) > n else s

# === Methods ===
def method_a(video, cost):
    p = PROMPT_A.format(channel_name=video["channel_name"], video_title=video["title"], subtitle=trunc(video["subtitle"]))
    text = claude(p, cost, 3000)
    r = parse_json(text)
    return r if r and "signals" in r else {"signals": []}

def method_b(video, cost):
    sub = trunc(video["subtitle"])
    # Step 1
    p1 = PROMPT_B1.format(channel_name=video["channel_name"], video_title=video["title"], subtitle=sub)
    t1 = claude(p1, cost, 1000)
    r1 = parse_json(t1)
    if not r1 or not r1.get("stocks"):
        return {"signals": [], "stocks_found": 0}
    
    stocks = r1["stocks"][:5]
    signals = []
    for s in stocks:
        name = s.get("stock_name", "")
        if not name: continue
        p2 = PROMPT_B2.format(stock_name=name, channel_name=video["channel_name"], video_title=video["title"], subtitle=sub)
        t2 = claude(p2, cost, 800)
        r2 = parse_json(t2)
        if r2 and r2.get("signal"):
            sig = r2["signal"]
            sig["stock_code"] = sig.get("stock_code") or s.get("stock_code", "")
            sig["market"] = sig.get("market") or s.get("market", "")
            signals.append(sig)
        time.sleep(0.3)
    return {"signals": signals, "stocks_found": len(r1["stocks"])}

# === Main ===
def main():
    print("=" * 60)
    print(f"A/B Test: V10.10 vs V10.11 | {datetime.now()}")
    print(f"Sample: {SAMPLE_SIZE}, Budget: ${MAX_COST}")
    print("=" * 60)

    videos = fetch_videos()
    print(f"Testing {len(videos)} videos\n")

    cost_a, cost_b = Cost(), Cost()
    results = []

    for i, v in enumerate(videos):
        title = v["title"][:40]
        print(f"[{i+1}/{len(videos)}] {title}")
        
        try:
            print(f"  A...", end=" ")
            sys.stdout.flush()
            ra = method_a(v, cost_a)
            print(f"{len(ra['signals'])} sigs (${cost_a.usd:.3f})")
            
            time.sleep(1)
            
            print(f"  B...", end=" ")
            sys.stdout.flush()
            rb = method_b(v, cost_b)
            sf = rb.get("stocks_found", 0)
            print(f"{sf} stocks → {len(rb['signals'])} sigs (${cost_b.usd:.3f})")
            
            results.append({
                "video_id": v.get("video_id", v["id"]),
                "title": v["title"], "channel": v["channel_name"],
                "sub_len": len(v["subtitle"]),
                "method_a": {"signals": ra["signals"], "count": len(ra["signals"])},
                "method_b": {"signals": rb["signals"], "count": len(rb["signals"]), "stocks_found": sf}
            })
            time.sleep(1)
        except Exception as e:
            print(f"  ERROR: {e}")
            if "Budget" in str(e): break
            results.append({"video_id": v.get("video_id", "?"), "title": v["title"], "error": str(e)})

    # === Analysis ===
    valid = [r for r in results if "error" not in r]
    ta = sum(r["method_a"]["count"] for r in valid)
    tb = sum(r["method_b"]["count"] for r in valid)
    ts = sum(r["method_b"]["stocks_found"] for r in valid)

    def types(rs, k):
        c = {"매수":0,"긍정":0,"중립":0,"부정":0,"매도":0,"기타":0}
        for r in rs:
            if "error" in r: continue
            for s in r[k]["signals"]:
                t = s.get("signal_type","기타")
                c[t] = c.get(t, 0) + 1
        return c

    ta_t, tb_t = types(results,"method_a"), types(results,"method_b")
    
    # Buy/positive diffs
    diffs = []
    for r in valid:
        ma = {s.get("stock_name"): s.get("signal_type") for s in r["method_a"]["signals"]}
        mb = {s.get("stock_name"): s.get("signal_type") for s in r["method_b"]["signals"]}
        for st in set(ma) & set(mb):
            if ma[st] != mb[st] and {ma[st], mb[st]} & {"매수","긍정"}:
                diffs.append({"video": r["video_id"][:20], "stock": st, "a": ma[st], "b": mb[st]})

    # False positives
    bad = ["코스피","코스닥","나스닥","S&P","다우","금리","환율","달러","유가","부동산","채권"]
    def fps(rs, k):
        return [{"v": r["video_id"][:15], "s": s.get("stock_name","")} 
                for r in rs if "error" not in r 
                for s in r[k]["signals"] 
                if any(b in s.get("stock_name","") for b in bad)]
    fpa, fpb = fps(results,"method_a"), fps(results,"method_b")

    n = len(valid) or 1
    summary = {
        "date": datetime.now().isoformat(),
        "samples": len(videos), "valid": len(valid),
        "cost_a": {"calls": cost_a.calls, "inp": cost_a.inp, "out": cost_a.out, "usd": round(cost_a.usd,4)},
        "cost_b": {"calls": cost_b.calls, "inp": cost_b.inp, "out": cost_b.out, "usd": round(cost_b.usd,4)},
        "total_cost": round(cost_a.usd + cost_b.usd, 4),
        "signals_a": ta, "signals_b": tb, "stocks_b": ts,
        "avg_a": round(ta/n,2), "avg_b": round(tb/n,2),
        "types_a": ta_t, "types_b": tb_t,
        "buy_positive_diffs": diffs, "fp_a": len(fpa), "fp_b": len(fpb)
    }

    # Save JSON
    with open(OUTPUT_DIR/"ab_test_v10_results.json","w",encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)

    # Save markdown
    md = f"""# A/B 테스트 결과: V10.10 vs V10.11 2단계 구조

## 개요
- 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- 샘플: {len(videos)}개 영상, 유효: {len(valid)}개
- 모델: {MODEL}

## 비용
| | A (단일) | B (2단계) |
|--|----------|-----------|
| API 호출 | {cost_a.calls}회 | {cost_b.calls}회 |
| 입력 토큰 | {cost_a.inp:,} | {cost_b.inp:,} |
| 출력 토큰 | {cost_a.out:,} | {cost_b.out:,} |
| 비용 | ${cost_a.usd:.4f} | ${cost_b.usd:.4f} |
| **총합** | **${cost_a.usd + cost_b.usd:.4f}** ||

## 1. 시그널 수
| | A | B |
|--|---|---|
| 총 시그널 | {ta} | {tb} |
| 영상당 평균 | {ta/n:.2f} | {tb/n:.2f} |
| B 종목 추출 | - | {ts} |

## 2. 시그널 타입 분포
| 타입 | A | B | 차이 |
|------|---|---|------|
| 매수 | {ta_t['매수']} | {tb_t['매수']} | {tb_t['매수']-ta_t['매수']:+d} |
| 긍정 | {ta_t['긍정']} | {tb_t['긍정']} | {tb_t['긍정']-ta_t['긍정']:+d} |
| 중립 | {ta_t['중립']} | {tb_t['중립']} | {tb_t['중립']-ta_t['중립']:+d} |
| 부정 | {ta_t['부정']} | {tb_t['부정']} | {tb_t['부정']-ta_t['부정']:+d} |
| 매도 | {ta_t['매도']} | {tb_t['매도']} | {tb_t['매도']-ta_t['매도']:+d} |

## 3. 매수/긍정 분류 차이
{len(diffs)}건 발견:
"""
    for d in diffs[:20]:
        md += f"- **{d['stock']}**: A={d['a']} → B={d['b']}\n"
    
    md += f"""
## 4. 비종목 오추출
| | A | B |
|--|---|---|
| 오추출 | {len(fpa)} | {len(fpb)} |

## 5. 결론
- **시그널 수**: A={ta}, B={tb} ({'B가 더 많음' if tb>ta else 'A가 더 많음' if ta>tb else '동일'})
- **매수/긍정 분류 차이**: {len(diffs)}건
- **비종목 오추출**: A={len(fpa)}, B={len(fpb)}
- **비용**: A=${cost_a.usd:.2f}, B=${cost_b.usd:.2f} (B가 {cost_b.usd/max(cost_a.usd,0.001):.1f}배)
- **종합**: {'2단계(B)가 종목별 집중 분석으로 매수/긍정 구분이 더 정확할 가능성 높음' if len(diffs) > 2 else '두 방식의 차이가 크지 않음'}
"""

    with open(OUTPUT_DIR/"ab_test_v10_results.md","w",encoding="utf-8") as f:
        f.write(md)

    print(f"\n{'='*60}")
    print(f"완료! 총비용: ${cost_a.usd + cost_b.usd:.4f}")
    print(f"A: {ta} signals, B: {tb} signals")
    print(f"매수/긍정 분류차이: {len(diffs)}건")
    print(f"결과: {OUTPUT_DIR/'ab_test_v10_results.md'}")

if __name__ == "__main__":
    main()
