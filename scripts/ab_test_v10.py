"""
A/B Test: V10.10 (?⑥씪) vs V10.11 (2?④퀎)
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
MODEL = "claude-sonnet-4-6"
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
PROMPT_A = """?뱀떊? ?ъ옄 ?먮쭑 遺꾩꽍 ?꾨Ц媛?낅땲?? ?꾨옒 ?먮쭑?먯꽌 ?ъ옄 ?쒓렇?먯쓣 異붿텧?섏꽭??

梨꾨꼸: {channel_name} | ?쒕ぉ: {video_title}
?먮쭑:
{subtitle}

## ?쒓렇??5?④퀎留??ъ슜: 留ㅼ닔/湲띿젙/以묐┰/遺??留ㅻ룄
- 留ㅼ닔: "?щ씪, ?댁븘?? ??紐낇솗??留ㅼ닔 ?≪뀡
- 湲띿젙: "醫뗭븘蹂댁씤?? ???몄쓽?곸씠??留ㅼ닔 沅뚯쑀 ?꾨떂
- 以묐┰: ?댁뒪/由ы룷??援먯쑁 ?꾨떖
- 遺??留ㅻ룄: 媛곴컖 遺?뺤쟻/紐낇솗??留ㅻ룄

## 留ㅼ닔 vs 湲띿젙: "蹂몄씤???嫄곕굹 ?щ씪怨??덈뒗媛?" Yes=留ㅼ닔, No=湲띿젙

## 洹쒖튃
- 1?곸긽 1醫낅ぉ 1?쒓렇?? key_quote??醫낅ぉ紐??꾩닔, 20??, ??꾩뒪?ы봽 ?꾩닔
- ?쒓뎅/誘멸뎅二쇱떇/?щ┰?좊쭔, 援먯쑁/?댁뒪留뚯씠硫??쒓렇???놁쓬
- ?쇨굅 醫낅ぉ? 理쒕? 湲띿젙源뚯?

JSON留?異쒕젰:
{{"signals": [{{"speaker":"","stock_name":"","stock_code":"","market":"","mention_type":"","signal_type":"","confidence":"","timestamp":"","key_quote":"","reasoning":""}}]}}
?쒓렇???놁쑝硫?{{"signals": []}}"""

PROMPT_B1 = """?꾨옒 ?먮쭑?먯꽌 ?멸툒???ъ옄 醫낅ぉ留?異붿텧?섏꽭??

梨꾨꼸: {channel_name} | ?쒕ぉ: {video_title}
?먮쭑:
{subtitle}

洹쒖튃: ?쒓뎅/誘멸뎅二쇱떇/?щ┰?좊쭔, ?뺤떇 醫낅ぉ紐? 吏???쒖쇅, 鍮꾩쥌紐??쒖쇅

JSON留?
{{"stocks": [{{"stock_name":"","stock_code":"","market":""}}]}}
醫낅ぉ ?놁쑝硫?{{"stocks": []}}"""

PROMPT_B2 = """?꾨옒 ?먮쭑?먯꽌 **{stock_name}**??????ъ옄 ?쒓렇?먯쓣 ?먮떒?섏꽭??

梨꾨꼸: {channel_name} | ?쒕ぉ: {video_title}
?먮쭑:
{subtitle}

## ?쒓렇?? 留ㅼ닔/湲띿젙/以묐┰/遺??留ㅻ룄
留ㅼ닔 vs 湲띿젙: "蹂몄씤???嫄곕굹 ?щ씪怨??덈뒗媛?" Yes=留ㅼ닔, No=湲띿젙
- 留ㅼ닔: 蹂몄씤 留ㅻℓ 怨듦컻, "?щ씪/?댁븘??, ?ы듃?대━???몄엯, 遺꾪븷留ㅼ닔 吏??- 湲띿젙: "醫뗭븘蹂댁씤??, "愿?ш??몃씪", "?꾨쭩 諛앸떎", 遺꾩꽍留??쒓났

洹쒖튃: ?쇨굅?믪턀?湲띿젙, 援먯쑁/?댁뒪?믪떆洹몃꼸?놁쓬, key_quote??醫낅ぉ紐?洹쇨굅 20??, ??꾩뒪?ы봽 ?꾩닔

JSON留?
{{"signal": {{"speaker":"","stock_name":"","stock_code":"","market":"","mention_type":"","signal_type":"","confidence":"","timestamp":"","key_quote":"","reasoning":""}}}}
?쒓렇???놁쑝硫?{{"signal": null, "reason": ""}}"""

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
    return s[:n] + "\n...(?섎┝)" if len(s) > n else s

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
            print(f"{sf} stocks ??{len(rb['signals'])} sigs (${cost_b.usd:.3f})")
            
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
        c = {"留ㅼ닔":0,"湲띿젙":0,"以묐┰":0,"遺??:0,"留ㅻ룄":0,"湲고?":0}
        for r in rs:
            if "error" in r: continue
            for s in r[k]["signals"]:
                t = s.get("signal_type","湲고?")
                c[t] = c.get(t, 0) + 1
        return c

    ta_t, tb_t = types(results,"method_a"), types(results,"method_b")
    
    # Buy/positive diffs
    diffs = []
    for r in valid:
        ma = {s.get("stock_name"): s.get("signal_type") for s in r["method_a"]["signals"]}
        mb = {s.get("stock_name"): s.get("signal_type") for s in r["method_b"]["signals"]}
        for st in set(ma) & set(mb):
            if ma[st] != mb[st] and {ma[st], mb[st]} & {"留ㅼ닔","湲띿젙"}:
                diffs.append({"video": r["video_id"][:20], "stock": st, "a": ma[st], "b": mb[st]})

    # False positives
    bad = ["肄붿뒪??,"肄붿뒪??,"?섏뒪??,"S&P","?ㅼ슦","湲덈━","?섏쑉","?щ윭","?좉?","遺?숈궛","梨꾧텒"]
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
    md = f"""# A/B ?뚯뒪??寃곌낵: V10.10 vs V10.11 2?④퀎 援ъ“

## 媛쒖슂
- ?쇱떆: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- ?섑뵆: {len(videos)}媛??곸긽, ?좏슚: {len(valid)}媛?- 紐⑤뜽: {MODEL}

## 鍮꾩슜
| | A (?⑥씪) | B (2?④퀎) |
|--|----------|-----------|
| API ?몄텧 | {cost_a.calls}??| {cost_b.calls}??|
| ?낅젰 ?좏겙 | {cost_a.inp:,} | {cost_b.inp:,} |
| 異쒕젰 ?좏겙 | {cost_a.out:,} | {cost_b.out:,} |
| 鍮꾩슜 | ${cost_a.usd:.4f} | ${cost_b.usd:.4f} |
| **珥앺빀** | **${cost_a.usd + cost_b.usd:.4f}** ||

## 1. ?쒓렇????| | A | B |
|--|---|---|
| 珥??쒓렇??| {ta} | {tb} |
| ?곸긽???됯퇏 | {ta/n:.2f} | {tb/n:.2f} |
| B 醫낅ぉ 異붿텧 | - | {ts} |

## 2. ?쒓렇?????遺꾪룷
| ???| A | B | 李⑥씠 |
|------|---|---|------|
| 留ㅼ닔 | {ta_t['留ㅼ닔']} | {tb_t['留ㅼ닔']} | {tb_t['留ㅼ닔']-ta_t['留ㅼ닔']:+d} |
| 湲띿젙 | {ta_t['湲띿젙']} | {tb_t['湲띿젙']} | {tb_t['湲띿젙']-ta_t['湲띿젙']:+d} |
| 以묐┰ | {ta_t['以묐┰']} | {tb_t['以묐┰']} | {tb_t['以묐┰']-ta_t['以묐┰']:+d} |
| 遺??| {ta_t['遺??]} | {tb_t['遺??]} | {tb_t['遺??]-ta_t['遺??]:+d} |
| 留ㅻ룄 | {ta_t['留ㅻ룄']} | {tb_t['留ㅻ룄']} | {tb_t['留ㅻ룄']-ta_t['留ㅻ룄']:+d} |

## 3. 留ㅼ닔/湲띿젙 遺꾨쪟 李⑥씠
{len(diffs)}嫄?諛쒓껄:
"""
    for d in diffs[:20]:
        md += f"- **{d['stock']}**: A={d['a']} ??B={d['b']}\n"
    
    md += f"""
## 4. 鍮꾩쥌紐??ㅼ텛異?| | A | B |
|--|---|---|
| ?ㅼ텛異?| {len(fpa)} | {len(fpb)} |

## 5. 寃곕줎
- **?쒓렇????*: A={ta}, B={tb} ({'B媛 ??留롮쓬' if tb>ta else 'A媛 ??留롮쓬' if ta>tb else '?숈씪'})
- **留ㅼ닔/湲띿젙 遺꾨쪟 李⑥씠**: {len(diffs)}嫄?- **鍮꾩쥌紐??ㅼ텛異?*: A={len(fpa)}, B={len(fpb)}
- **鍮꾩슜**: A=${cost_a.usd:.2f}, B=${cost_b.usd:.2f} (B媛 {cost_b.usd/max(cost_a.usd,0.001):.1f}諛?
- **醫낇빀**: {'2?④퀎(B)媛 醫낅ぉ蹂?吏묒쨷 遺꾩꽍?쇰줈 留ㅼ닔/湲띿젙 援щ텇?????뺥솗??媛?μ꽦 ?믪쓬' if len(diffs) > 2 else '??諛⑹떇??李⑥씠媛 ?ъ? ?딆쓬'}
"""

    with open(OUTPUT_DIR/"ab_test_v10_results.md","w",encoding="utf-8") as f:
        f.write(md)

    print(f"\n{'='*60}")
    print(f"?꾨즺! 珥앸퉬?? ${cost_a.usd + cost_b.usd:.4f}")
    print(f"A: {ta} signals, B: {tb} signals")
    print(f"留ㅼ닔/湲띿젙 遺꾨쪟李⑥씠: {len(diffs)}嫄?)
    print(f"寃곌낵: {OUTPUT_DIR/'ab_test_v10_results.md'}")

if __name__ == "__main__":
    main()

