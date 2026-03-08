#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""?몄긽?숆컻濡??쒓렇??57媛??꾩닔 QA"""
import json, re, sys, time, requests
from collections import defaultdict, Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
ANTHROPIC_KEY = "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"
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# ??? ?곗씠??濡쒕뱶 ???????????????????????????????
with open("C:/Users/Mario/work/sesang_signals_full.json", encoding="utf-8") as f:
    signals = json.load(f)
print(f"濡쒕뱶: {len(signals)}媛?)

# ??? 1. 湲곕낯 ?듦퀎 ?????????????????????????????
sig_dist = Counter(s["signal"] for s in signals)
mention_dist = Counter(s["mention_type"] for s in signals)
print(f"\n[?쒓렇??遺꾪룷] {dict(sig_dist)}")
print(f"[mention_type] {dict(mention_dist)}")

# ??? 2. 猷?湲곕컲 泥댄겕 ??????????????????????????
issues = defaultdict(list)

INVALID_STOCKS = {
    "肄붿뒪??, "肄붿뒪??, "S&P500", "S&P 500", "?섏뒪??, "?ㅼ슦", "?ㅼ슦議댁뒪",
    "?덉???, "KOSPI", "KOSDAQ", "?щ윭", "?먰솕", "?뷀솕", "?꾩븞??,
    "湲?, "?", "?먯쑀", "梨꾧텒", "USD", "KRW", "JPY", "EUR",
    "?쒖옣", "利앹떆", "吏??, "?섏쑉", "湲덈━",
}

CONDITIONAL_KEYWORDS = ["留뚯빟", "~?덈떎硫?, "?댁뿀?ㅻ㈃", "??ㅻ㈃", "?쒕떎硫?, "?쒕떎硫?, "媛??]

video_stock_map = defaultdict(list)  # video_id ??[stock, ...]

for s in signals:
    sid = s["id"]
    stock = s.get("stock", "") or ""
    sig = s.get("signal", "")
    mtype = s.get("mention_type", "") or ""
    ts = s.get("timestamp", "") or ""
    kq = s.get("key_quote", "") or ""
    reasoning = s.get("reasoning", "") or ""
    vid = s.get("video_id", "")

    # 2-1. 鍮꾩쥌紐??ㅼ텛異?    if stock in INVALID_STOCKS or s.get("market") == "INDEX":
        issues["鍮꾩쥌紐??ㅼ텛異?].append({
            "id": sid, "stock": stock, "signal": sig,
            "ticker": s.get("ticker"), "market": s.get("market"),
            "title": s.get("_video_title", ""),
        })

    # 2-2. ??꾩뒪?ы봽 ?좏슚??(HH:MM:SS or MM:SS)
    ts_valid = bool(re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", ts.strip())) if ts else False
    if not ts_valid:
        issues["??꾩뒪?ы봽_?ㅻ쪟"].append({
            "id": sid, "stock": stock, "signal": sig,
            "timestamp": ts, "title": s.get("_video_title", ""),
        })

    # 2-3. 以묐났 (媛숈? video_id + stock)
    video_stock_map[vid].append((sid, stock))

    # 2-4. key_quote ?덉쭏
    if not kq or len(kq) < 20:
        issues["key_quote_遺議?].append({
            "id": sid, "stock": stock, "signal": sig,
            "key_quote": kq[:80], "title": s.get("_video_title", ""),
        })
    # 媛?뺥삎 諛쒖뼵
    if any(kw in kq for kw in CONDITIONAL_KEYWORDS):
        issues["媛?뺥삎_諛쒖뼵"].append({
            "id": sid, "stock": stock, "signal": sig,
            "key_quote": kq[:100], "title": s.get("_video_title", ""),
        })
    # reasoning 吏?섏튂寃?湲?(?붿빟 ?ㅽ뙣)
    if len(reasoning) > 600:
        issues["reasoning_怨쇰떎"].append({
            "id": sid, "stock": stock, "signal": sig,
            "reasoning_len": len(reasoning),
        })

    # 2-5. mention_type vs signal 遺덉씪移?    if mtype in ("援먯쑁", "?댁뒪") and sig == "留ㅼ닔":
        issues["mention_signal_遺덉씪移?].append({
            "id": sid, "stock": stock, "signal": sig,
            "mention_type": mtype, "key_quote": kq[:80],
        })
    if mtype == "寃곕줎" and sig == "以묐┰":
        issues["寃곕줎_以묐┰_?섏떖"].append({
            "id": sid, "stock": stock, "signal": sig,
            "mention_type": mtype, "key_quote": kq[:80],
        })
    # ?쇨굅/援먯쑁?몃뜲 留ㅼ닔
    if mtype in ("?쇨굅", "援먯쑁", "蹂댁쑀", "?댁뒪") and sig == "留ㅼ닔":
        issues["?쇨굅_留ㅼ닔_?섏떖"].append({
            "id": sid, "stock": stock, "signal": sig,
            "mention_type": mtype, "key_quote": kq[:80],
        })

# 以묐났 泥댄겕
for vid, items in video_stock_map.items():
    stock_counter = Counter(stock for _, stock in items)
    for stock, cnt in stock_counter.items():
        if cnt >= 2:
            dup_ids = [sid for sid, s in items if s == stock]
            issues["以묐났_?쒓렇??].append({
                "video_id": vid, "stock": stock, "count": cnt,
                "signal_ids": dup_ids,
            })

# ??? 3. AI ?ш?利?(Haiku) ?????????????????????
print(f"\n[AI ?ш?利? Haiku濡?57媛?寃利?以?..")
ai_results = []

def haiku_verify(batch):
    """Haiku濡?諛곗튂 寃利?""
    items_text = ""
    for i, s in enumerate(batch):
        items_text += f"""
{i+1}. ID: {s['id']}
   醫낅ぉ: {s.get('stock','')} | ?꾩옱 ?쒓렇?? {s.get('signal','')} | ?좏삎: {s.get('mention_type','')}
   ?듭떖諛쒖뼵: {(s.get('key_quote','') or '')[:150]}
"""

    prompt = f"""?ㅼ쓬 ?ъ옄 ?쒓렇?먮뱾??寃利앺빐以?

?먮떒 湲곗?:
- 留ㅼ닔: 蹂몄씤??吏곸젒 留ㅼ닔?덇굅??泥?쨷?먭쾶 紐낇솗??留ㅼ닔 沅뚯쑀
- 湲띿젙: 湲띿젙???꾨쭩/遺꾩꽍?댁?留?吏곸젒 留ㅼ닔 沅뚯쑀 ?놁쓬
- 以묐┰: ?ъ떎 ?꾨떖, ?묐㈃ 遺꾩꽍, 援먯쑁???ㅻ챸
- 寃쎄퀎: 二쇱쓽/?꾪뿕 寃쎄퀬
- 遺?? 遺?뺤쟻 ?꾨쭩, 留ㅻ룄 ?댁쑀
- 留ㅻ룄: 吏곸젒 留ㅻ룄 沅뚯쑀 ?먮뒗 蹂몄씤 留ㅻ룄 怨듦컻

媛??쒓렇?먯뿉 ???JSON 諛곗뿴濡쒕쭔 ?듯빐 (?ㅻⅨ ?ㅻ챸 ?놁씠):
[{{"id":"...", "correct_signal":"...", "is_wrong":true/false, "reason":"20?먯씠??}}]

?쒓렇??紐⑸줉:
{items_text}"""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-3-5-20241022",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        if r.status_code == 200:
            text = r.json()["content"][0]["text"].strip()
            # JSON 異붿텧
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        else:
            print(f"  API ?ㅻ쪟: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"  ?덉쇅: {e}")
    return []

BATCH_SIZE = 10
for i in range(0, len(signals), BATCH_SIZE):
    batch = signals[i:i+BATCH_SIZE]
    print(f"  諛곗튂 {i//BATCH_SIZE+1}/{(len(signals)+BATCH_SIZE-1)//BATCH_SIZE} ({len(batch)}媛?...")
    results = haiku_verify(batch)
    ai_results.extend(results)
    if i + BATCH_SIZE < len(signals):
        time.sleep(3)

# AI 寃곌낵 留ㅽ븨
ai_map = {r["id"]: r for r in ai_results if isinstance(r, dict) and "id" in r}
ai_wrong = [r for r in ai_results if isinstance(r, dict) and r.get("is_wrong")]
print(f"  AI 寃利??꾨즺: {len(ai_results)}媛? ?ㅻ텇瑜??섏떖: {len(ai_wrong)}媛?)

# ??? 4. ?섏씡瑜??곗씠??泥댄겕 ?????????????????????
import os
price_file = "C:/Users/Mario/work/invest-sns/public/signal_prices.json"
price_data = {}
if os.path.exists(price_file):
    with open(price_file, encoding="utf-8") as f:
        price_data = json.load(f)
    print(f"\n[?섏씡瑜? signal_prices.json: {len(price_data)}媛???ぉ")
    # ?몄긽?숆컻濡??쒓렇??以?媛寃??곗씠???덈뒗 寃?    has_price = sum(1 for s in signals if s["id"] in price_data)
    print(f"  ?몄긽?숆컻濡?媛寃??곗씠???덉쓬: {has_price}/{len(signals)}")
else:
    print("\n[?섏씡瑜? signal_prices.json ?놁쓬")
    has_price = 0

# ??? 5. DB ?먮룞 ?섏젙 ??????????????????????????
print("\n[DB ?섏젙] ?먮룞 ?낅뜲?댄듃 ?쒖옉...")
updated = 0
patch_errors = 0

def patch_signal(signal_id, data):
    global updated, patch_errors
    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{signal_id}",
            json=data,
            headers={**H, "Prefer": "return=representation", "Content-Type": "application/json"},
        )
        if r.status_code in (200, 204):
            updated += 1
        else:
            print(f"  PATCH ?ㅻ쪟 {signal_id[:8]}: {r.status_code}")
            patch_errors += 1
    except Exception as e:
        print(f"  PATCH ?덉쇅: {e}")
        patch_errors += 1

# 鍮꾩쥌紐??ㅼ텛異???rejected
for item in issues["鍮꾩쥌紐??ㅼ텛異?]:
    patch_signal(item["id"], {
        "review_status": "rejected",
        "review_note": f"QA: 吏???듯솕/?쇰컲紐낆궗 ?ㅼ텛異?(stock={item['stock']})",
    })

# AI ?ㅻ텇瑜???needs_review
for item in ai_wrong:
    note = f"QA-AI: {item.get('correct_signal','?')}濡?蹂寃?寃??({item.get('reason','')[:50]})"
    patch_signal(item["id"], {
        "review_status": "needs_review",
        "review_note": note,
    })

# 媛?뺥삎 諛쒖뼵 ??needs_review
for item in issues["媛?뺥삎_諛쒖뼵"]:
    if item["id"] not in {x["id"] for x in ai_wrong}:  # 以묐났 諛⑹?
        patch_signal(item["id"], {
            "review_status": "needs_review",
            "review_note": "QA: 媛?뺥삎 諛쒖뼵 - ?쒓렇???좏슚???ш????꾩슂",
        })

print(f"  DB ?낅뜲?댄듃: {updated}嫄??깃났, {patch_errors}嫄??ㅻ쪟")

# ??? 6. 由ы룷???앹꽦 ???????????????????????????
sev = {"HIGH": "?뵶 HIGH", "MEDIUM": "?윞 MEDIUM", "LOW": "?윟 LOW"}

report_lines = [
    f"# ?몄긽?숆컻濡??쒓렇??QA 由ы룷??,
    f"?앹꽦: {datetime.now().strftime('%Y-%m-%d %H:%M')} (V9.1 ?뚯씠?꾨씪??湲곗?)",
    f"珥??쒓렇?? {len(signals)}媛?,
    "",
    "## ?붿빟",
    "",
    "| 移댄뀒怨좊━ | 臾몄젣 ??| ?ш컖??|",
    "|---------|---------|-------|",
    f"| 鍮꾩쥌紐??ㅼ텛異?| {len(issues['鍮꾩쥌紐??ㅼ텛異?])} | ?뵶 HIGH |",
    f"| ?쒓렇???ㅻ텇瑜?(AI) | {len(ai_wrong)} | ?뵶 HIGH |",
    f"| ??꾩뒪?ы봽 ?ㅻ쪟 | {len(issues['??꾩뒪?ы봽_?ㅻ쪟'])} | ?윞 MEDIUM |",
    f"| ?쇨굅/援먯쑁??留ㅼ닔 | {len(issues['?쇨굅_留ㅼ닔_?섏떖'])} | ?윞 MEDIUM |",
    f"| 以묐났 ?쒓렇??| {len(issues['以묐났_?쒓렇??])} | ?윞 MEDIUM |",
    f"| 媛?뺥삎 諛쒖뼵 | {len(issues['媛?뺥삎_諛쒖뼵'])} | ?윞 MEDIUM |",
    f"| key_quote 遺議?| {len(issues['key_quote_遺議?])} | ?윟 LOW |",
    f"| reasoning 怨쇰떎 | {len(issues['reasoning_怨쇰떎'])} | ?윟 LOW |",
    "",
    f"### ?쒓렇??遺꾪룷",
    f"- 湲띿젙: {sig_dist.get('湲띿젙',0)}媛?({sig_dist.get('湲띿젙',0)*100//len(signals)}%)",
    f"- 留ㅼ닔: {sig_dist.get('留ㅼ닔',0)}媛?({sig_dist.get('留ㅼ닔',0)*100//len(signals)}%)",
    f"- 以묐┰: {sig_dist.get('以묐┰',0)}媛?,
    f"- 遺?? {sig_dist.get('遺??,0)}媛?,
    f"- 寃쎄퀎: {sig_dist.get('寃쎄퀎',0)}媛?,
    f"- 留ㅻ룄: {sig_dist.get('留ㅻ룄',0)}媛?,
    "",
    "**寃쎄퀬: 湲띿젙 70%, 留ㅻ룄/寃쎄퀎 0嫄???遺???쒓렇??媛먯? 留ㅼ슦 ?쏀븿**" if sig_dist.get('寃쎄퀎',0)+sig_dist.get('留ㅻ룄',0) == 0 else "",
]

# 鍮꾩쥌紐??ㅼ텛異?report_lines += ["", "---", "## ?뵶 鍮꾩쥌紐??ㅼ텛異?(利됱떆 ??젣 ?꾩슂)", ""]
for item in issues["鍮꾩쥌紐??ㅼ텛異?]:
    report_lines.append(f"- **{item['stock']}** (ticker: {item['ticker']}, market: {item['market']}) | {item['signal']} | ID: `{item['id'][:8]}`")
    report_lines.append(f"  > ?곸긽: {item['title'][:60]}")

# AI ?ㅻ텇瑜?report_lines += ["", "---", "## ?뵶 ?쒓렇???ㅻ텇瑜?(AI ?ш?利?", ""]
if ai_wrong:
    for item in ai_wrong:
        orig = next((s for s in signals if s["id"] == item["id"]), {})
        report_lines.append(f"- **{orig.get('stock','')}** | {orig.get('signal','')} ??**{item.get('correct_signal','')}** 沅뚯옣")
        report_lines.append(f"  > 洹쇨굅: {item.get('reason','')}")
        report_lines.append(f"  > 諛쒖뼵: {(orig.get('key_quote','') or '')[:80]}")
else:
    report_lines.append("AI 寃利??ㅻ쪟 ?놁쓬 (API ?몄텧 ?ㅽ뙣 ??'?먮윭' ?쒖떆)")

# ??꾩뒪?ы봽
report_lines += ["", "---", "## ?윞 ??꾩뒪?ы봽 ?ㅻ쪟", ""]
for item in issues["??꾩뒪?ы봽_?ㅻ쪟"][:20]:
    report_lines.append(f"- **{item['stock']}** | timestamp: `{item['timestamp']}` | {item['signal']} | ID: `{item['id'][:8]}`")

# ?쇨굅/援먯쑁??留ㅼ닔
report_lines += ["", "---", "## ?윞 mention_type 遺덉씪移?(?쇨굅/援먯쑁/?댁뒪??留ㅼ닔)", ""]
for item in issues["?쇨굅_留ㅼ닔_?섏떖"]:
    report_lines.append(f"- **{item['stock']}** | mention={item['mention_type']} signal=**{item['signal']}** | ID: `{item['id'][:8]}`")
    report_lines.append(f"  > {item['key_quote'][:80]}")

# 以묐났
report_lines += ["", "---", "## ?윞 以묐났 ?쒓렇??, ""]
for item in issues["以묐났_?쒓렇??]:
    report_lines.append(f"- **{item['stock']}** | 媛숈? ?곸긽?먯꽌 {item['count']}踰??깆옣 | video: `{item['video_id'][:8]}`")

# 媛?뺥삎 諛쒖뼵
report_lines += ["", "---", "## ?윞 媛?뺥삎 諛쒖뼵 (議곌굔遺 諛쒖뼵???쒓렇?먮줈 ?깅줉)", ""]
for item in issues["媛?뺥삎_諛쒖뼵"]:
    report_lines.append(f"- **{item['stock']}** | {item['signal']} | ID: `{item['id'][:8]}`")
    report_lines.append(f"  > \"{item['key_quote'][:100]}\"")

# key_quote 遺議?report_lines += ["", "---", "## ?윟 key_quote ?덉쭏 ?댁뒋", ""]
for item in issues["key_quote_遺議?][:10]:
    report_lines.append(f"- **{item['stock']}** | key_quote: `{item['key_quote'][:50]}`")

# ?섏씡瑜?report_lines += ["", "---", "## ?뮥 ?섏씡瑜??곗씠???꾪솴", ""]
report_lines.append(f"- 媛寃??곗씠???덉쓬: {has_price}/{len(signals)}媛?)
report_lines.append(f"- ?꾨씫: {len(signals)-has_price}媛?)

# ?꾨＼?꾪듃 媛쒖꽑 ?쒖븞
report_lines += [
    "", "---",
    "## ?뱷 ?꾨＼?꾪듃 媛쒖꽑 ?쒖븞 (V9.1 ??V10.11 ?댄뻾 ?꾩슂)",
    "",
    "### ?⑦꽩 1: 吏???듯솕瑜?醫낅ぉ?쇰줈 ?ㅼ텛異?,
    f"- 諛쒖깮: {len(issues['鍮꾩쥌紐??ㅼ텛異?])}嫄?,
    "- ?먯씤: V9.1 ?꾨＼?꾪듃??吏???쒖쇅 洹쒖튃???놁쓬",
    "- 媛쒖꽑?? `STEP 2.5 ?뺢퇋?? ?④퀎??紐낆떆???쒖쇅 紐⑸줉 異붽?",
    '  ```',
    '  ?덈? ?쒓렇?먮줈 留뚮뱾吏 留?寃? 肄붿뒪?? 肄붿뒪?? S&P500, ?섏뒪?? ?щ윭, ?먰솕, 湲? ?먯쑀, 吏??,
    '  ```',
    "",
    "### ?⑦꽩 2: ?쇨굅/援먯쑁 ?멸툒??留ㅼ닔濡?遺꾨쪟",
    f"- 諛쒖깮: {len(issues['?쇨굅_留ㅼ닔_?섏떖'])}嫄?,
    "- ?먯씤: mention_type 遺꾨쪟媛 二쇨??? 留ㅼ닔 ?먮떒 湲곗? 遺덈챸??,
    "- 媛쒖꽑??(V10.11 ?대? ?곸슜??: '蹂몄씤???嫄곕굹 ?щ씪怨??덈뒗媛?' ??Yes = 留ㅼ닔",
    "",
    "### ?⑦꽩 3: 媛?뺥삎 諛쒖뼵???쒓렇?먮줈 ?깅줉",
    f"- 諛쒖깮: {len(issues['媛?뺥삎_諛쒖뼵'])}嫄?,
    "- ?먯씤: '留뚯빟 ~?댁뿀?ㅻ㈃' 媛숈? 媛?뺥삎 諛쒖뼵???쒓렇?먮줈 ?ы븿??,
    "- 媛쒖꽑?? 媛?뺥삎 議곌굔遺 諛쒖뼵? ?쒓렇???앹꽦 湲덉? 洹쒖튃 異붽?",
    '  ```',
    '  湲덉?: "留뚯빟", "~?덈떎硫?, "~?댁뿀?ㅻ㈃", "媛?뺥븯硫? ?ы븿 諛쒖뼵? ?쒓렇???앹꽦 遺덇?',
    '  ```',
    "",
    "### ?⑦꽩 4: ??꾩뒪?ы봽 ?뺤떇 ?ㅻ쪟",
    f"- 諛쒖깮: {len(issues['??꾩뒪?ы봽_?ㅻ쪟'])}嫄?,
    "- ?먯씤: ?좎쭨('3??23??)???띿뒪?멸? ??꾩뒪?ы봽濡??낅젰??,
    "- 媛쒖꽑?? ??꾩뒪?ы봽 ?뺤떇 媛뺤젣 (HH:MM:SS or MM:SS留??덉슜)",
    "",
    "### 寃곕줎: V9.1 ??V10.11 ?щ텇???꾩슂",
    "- ?몄긽?숆컻濡?梨꾨꼸? V9.1 ?뚯씠?꾨씪?몄쑝濡?遺꾩꽍??(理쒖떊 V10.11 ?꾨떂)",
    "- ???ㅻ쪟??以??곷떦?섎뒗 V10.11 ?щ텇?앹쑝濡??먮룞 ?닿껐 ?덉긽",
    "- **異붿쿇: ?몄긽?숆컻濡?81媛??곸긽 V10.11濡??щ텇????DB 援먯껜**",
    "",
    "---",
    f"## 議곗튂 ?꾪솴",
    f"- DB ?먮룞 ?섏젙 ?꾨즺: {updated}嫄?,
    f"  - 鍮꾩쥌紐??ㅼ텛異???rejected: {len(issues['鍮꾩쥌紐??ㅼ텛異?])}嫄?,
    f"  - AI ?ㅻ텇瑜???needs_review: {len(ai_wrong)}嫄?,
    f"  - 媛?뺥삎 諛쒖뼵 ??needs_review",
    f"- ?섎룞 寃???꾩슂: needs_review ?곹깭 ?쒓렇???뺤씤",
]

report = "\n".join(report_lines)
with open("C:/Users/Mario/work/sesang_qa_report.md", "w", encoding="utf-8") as f:
    f.write(report)

# 以묎컙 寃곌낵??媛깆떊
with open("C:/Users/Mario/work/sesang_qa_intermediate.json", "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "issues": {k: v for k, v in issues.items()},
        "ai_results": ai_results,
        "ai_wrong": ai_wrong,
        "db_updated": updated,
    }, f, ensure_ascii=False, indent=2)

print(f"\n{'='*50}")
print(f"QA ?꾨즺")
print(f"{'='*50}")
print(f"珥??쒓렇?? {len(signals)}")
print(f"鍮꾩쥌紐??ㅼ텛異? {len(issues['鍮꾩쥌紐??ㅼ텛異?])}嫄?)
print(f"AI ?ㅻ텇瑜??섏떖: {len(ai_wrong)}嫄?)
print(f"??꾩뒪?ы봽 ?ㅻ쪟: {len(issues['??꾩뒪?ы봽_?ㅻ쪟'])}嫄?)
print(f"?쇨굅/援먯쑁??留ㅼ닔: {len(issues['?쇨굅_留ㅼ닔_?섏떖'])}嫄?)
print(f"媛?뺥삎 諛쒖뼵: {len(issues['媛?뺥삎_諛쒖뼵'])}嫄?)
print(f"以묐났 ?쒓렇?? {len(issues['以묐났_?쒓렇??])}嫄?)
print(f"DB ?먮룞 ?섏젙: {updated}嫄?)
print(f"由ы룷?? C:/Users/Mario/work/sesang_qa_report.md")

