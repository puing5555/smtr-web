#!/usr/bin/env python3
"""
?몄긽?숆컻濡?V11 ?щ텇???ㅽ겕由쏀듃
- DB?먯꽌 ?몄긽?숆컻濡?梨꾨꼸 ?쒓렇?먯쓣 媛?몄? V11 ?꾨＼?꾪듃濡??щ텇??- 鍮꾨뵒?ㅻ퀎 洹몃９?묒쑝濡?API ?몄텧 ?⑥쑉??(媛숈? ?곸긽???쒓렇?먯? 1踰덈쭔 ?몄텧)
- 寃곌낵瑜?DB??UPDATE?섍퀬 吏꾪뻾?곹솴 ???"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import anthropic
import requests

# ??? ?섍꼍 ?ㅼ젙 ???????????????????????????????????????????????
SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
ANTHROPIC_KEY = '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'
MODEL = 'claude-sonnet-4-6'
PROMPT_FILE = 'C:/Users/Mario/work/prompts/pipeline_v11.md'
PROGRESS_FILE = 'C:/Users/Mario/work/data/sesang_v11_progress.json'

# API 鍮꾩슜 異붿쟻 (claude-sonnet-4 湲곗?: input $3/M, output $15/M)
INPUT_PRICE_PER_TOKEN = 3.0 / 1_000_000
OUTPUT_PRICE_PER_TOKEN = 15.0 / 1_000_000

# ??? Supabase ?대씪?댁뼵????????????????????????????????????????
class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
        }

    def select(self, table: str, query: str = '') -> list:
        url = f"{self.url}/rest/v1/{table}?{query}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def update(self, table: str, match: dict, data: dict) -> dict:
        conditions = '&'.join(f"{k}=eq.{v}" for k, v in match.items())
        url = f"{self.url}/rest/v1/{table}?{conditions}"
        resp = requests.patch(url, headers={**self.headers, 'Prefer': 'return=representation'}, json=data)
        resp.raise_for_status()
        return resp.json()


# ??? 吏꾪뻾?곹솴 ???遺덈윭?ㅺ린 ??????????????????????????????????
def load_progress() -> dict:
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'processed_video_ids': [], 'updated_signal_ids': [], 'total_cost': 0.0, 'started_at': datetime.now().isoformat()}


def save_progress(progress: dict):
    Path(PROGRESS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


# ??? V11 ?꾨＼?꾪듃 濡쒕뱶 ???????????????????????????????????????
def load_v11_prompt() -> str:
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()


# ??? ?щ텇???꾨＼?꾪듃 ?앹꽦 ????????????????????????????????????
def build_reanalysis_prompt(v11_prompt: str, video_title: str, subtitle: str, signals: list) -> str:
    """
    V11 ?꾨＼?꾪듃 + 湲곗〈 ?쒓렇??紐⑸줉 + ?먮쭑?쇰줈 ?щ텇???붿껌 ?꾨＼?꾪듃 ?앹꽦
    """
    signal_list = '\n'.join(
        f"  - ?쒓렇?륤D={s['id']}, 醫낅ぉ={s.get('stock','?')}, ?꾩옱?좏샇={s.get('signal','?')}, ?꾩옱??꾩뒪?ы봽={s.get('timestamp','?')}"
        for s in signals
    )

    return f"""
{v11_prompt}

---

## ?щ텇???붿껌

?꾨옒 ?곸긽??湲곗〈 ?쒓렇?먮뱾??V11 洹쒖튃???곕씪 ?ш??좏븯?몄슂.

**?곸긽 ?쒕ぉ**: {video_title}

**?먮쭑**:
{subtitle[:15000] if subtitle else '(?먮쭑 ?놁쓬)'}

**湲곗〈 ?쒓렇??紐⑸줉** (?щ텇?????:
{signal_list}

---

## 異쒕젰 ?붽뎄?ы빆

媛??쒓렇??ID蹂꾨줈 ?ㅼ쓬 ?뺤떇??JSON??異쒕젰?섏꽭??

```json
{{
  "results": [
    {{
      "signal_id": "<湲곗〈 ?쒓렇??ID>",
      "action": "update" | "reject",
      "signal": "留ㅼ닔|湲띿젙|以묐┰|遺??留ㅻ룄",
      "timestamp": "MM:SS ?먮뒗 HH:MM:SS ?뺤떇留?,
      "key_quote": "?듭떖 諛쒖뼵 ?먮Ц 20???댁긽",
      "reasoning": "V11 洹쒖튃 湲곗? 遺꾨쪟 ?댁쑀",
      "reject_reason": "action=reject???뚮쭔: 嫄곕? ?댁쑀 (媛?뺥삎諛쒖뼵/吏?섏쥌紐???꾩뒪?ы봽?놁쓬 ??"
    }}
  ]
}}
```

**V11 ?듭떖 泥댄겕由ъ뒪??*:
1. 媛?뺥삎 諛쒖뼵("留뚯빟/~?덈떎硫?~?댁뿀?ㅻ㈃") ??action=reject
2. 吏???щ윭/?먯옄??肄붿뒪???щ윭/湲??? ??action=reject
3. ??꾩뒪?ы봽瑜??먮쭑?먯꽌 理쒕???李얠븘 MM:SS ?뺤떇?쇰줈 ??李얠쓣 ???놁쑝硫?confidence=low
4. 留ㅼ닔 湲곗?: "蹂몄씤???嫄곕굹 ?щ씪怨??덈뒗媛?" ??Yes=留ㅼ닔 / No=湲띿젙

JSON留?異쒕젰?섏꽭?? ?ㅻⅨ ?ㅻ챸 ?놁씠.
"""


# ??? API ?묐떟 ?뚯떛 ???????????????????????????????????????????
def parse_api_response(content: str) -> list:
    """API ?묐떟?먯꽌 JSON 寃곌낵 異붿텧"""
    # ```json ... ``` 釉붾줉 異붿텧
    match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # JSON 釉붾줉 ?놁쑝硫??꾩껜?먯꽌 { "results": ... } ?⑦꽩 李얘린
        match = re.search(r'\{.*?"results".*?\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            print(f"  ?좑툘  JSON ?뚯떛 ?ㅽ뙣. ?묐떟 ?댁슜:\n{content[:500]}")
            return []

    try:
        data = json.loads(json_str)
        return data.get('results', [])
    except json.JSONDecodeError as e:
        print(f"  ?좑툘  JSON ?붿퐫???ㅻ쪟: {e}")
        return []


# ??? ??꾩뒪?ы봽 ?좏슚??寃利???????????????????????????????????
def is_valid_timestamp(ts: str) -> bool:
    """HH:MM:SS ?먮뒗 MM:SS ?뺤떇?몄? ?뺤씤"""
    if not ts:
        return False
    # 湲덉? ?⑦꽩
    forbidden = ['N/A', 'n/a', '?놁쓬', '誘몄긽', '珥덈컲', '以묐컲', '?꾨컲', '?꾩껜', '?좎쭨', '??, '??]
    for f in forbidden:
        if f in str(ts):
            return False
    # ?뺤떇 泥댄겕
    pattern = r'^\d{1,2}:\d{2}(:\d{2})?$'
    if not re.match(pattern, str(ts)):
        return False
    # 0:00 湲덉?
    if ts in ['0:00', '00:00', '00:00:00']:
        return False
    return True


# ??? 硫붿씤 ?ㅽ뻾 ???????????????????????????????????????????????
def main():
    print("=" * 60)
    print("?몄긽?숆컻濡?V11 ?щ텇???ㅽ겕由쏀듃")
    print(f"?쒖옉 ?쒓컖: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ?대씪?댁뼵??珥덇린??    db = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    ai = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    # V11 ?꾨＼?꾪듃 濡쒕뱶
    print("\n[以鍮? V11 ?꾨＼?꾪듃 濡쒕뱶 以?..")
    v11_prompt = load_v11_prompt()
    print(f"  ???꾨＼?꾪듃 濡쒕뱶 ?꾨즺 ({len(v11_prompt):,} ??")

    # 吏꾪뻾?곹솴 遺덈윭?ㅺ린
    progress = load_progress()
    total_cost = progress.get('total_cost', 0.0)
    updated_ids = progress.get('updated_signal_ids', [])
    processed_video_ids = progress.get('processed_video_ids', [])

    # ?? STEP 1: ?몄긽?숆컻濡?梨꾨꼸 ID 李얘린 ??????????????????????
    print("\n[STEP 1] ?몄긽?숆컻濡?梨꾨꼸 李얘린...")
    channels = db.select('influencer_channels', 'channel_name=ilike.*?몄긽?숆컻濡?&select=id,channel_name,channel_id')
    if not channels:
        # ?쒓? ilike媛 ????寃쎌슦 ?꾩껜 議고쉶 ???꾪꽣
        channels = db.select('influencer_channels', 'select=id,channel_name,channel_id')
        channels = [c for c in channels if '?몄긽?숆컻濡? in (c.get('channel_name') or '')]

    if not channels:
        print("  ???몄긽?숆컻濡?梨꾨꼸??李얠쓣 ???놁뒿?덈떎.")
        print("  ??influencer_channels ?뚯씠釉붿쓽 channel_name 而щ읆???뺤씤?섏꽭??")
        return

    channel = channels[0]
    channel_db_id = channel['id']
    channel_yt_id = channel.get('channel_id', '')
    print(f"  ??梨꾨꼸 諛쒓껄: {channel['channel_name']} (DB ID: {channel_db_id})")

    # ?? STEP 2: ?몄긽?숆컻濡??곸긽 紐⑸줉 媛?몄삤湲?????????????????
    print("\n[STEP 2] ?몄긽?숆컻濡??곸긽 紐⑸줉 議고쉶...")
    videos = db.select(
        'influencer_videos',
        f'channel_id=eq.{channel_db_id}&select=id,video_id,title,subtitle,transcript'
    )
    if not videos:
        # channel_id媛 YouTube channel_id瑜?李몄“?섎뒗 寃쎌슦
        videos = db.select(
            'influencer_videos',
            f'channel_id=eq.{channel_yt_id}&select=id,video_id,title,subtitle,transcript'
        )

    print(f"  ???곸긽 {len(videos)}媛?諛쒓껄")

    if not videos:
        print("  ???곸긽 ?곗씠?곌? ?놁뒿?덈떎. DB 援ъ“瑜??뺤씤?섏꽭??")
        return

    video_map = {v['id']: v for v in videos}
    video_ids = [v['id'] for v in videos]

    # ?? STEP 3: ?쒓렇??媛?몄삤湲?(review_status != rejected) ??
    print("\n[STEP 3] ?몄긽?숆컻濡??쒓렇??議고쉶...")
    # video_id IN (...)濡?荑쇰━
    if not video_ids:
        print("  ???곸긽 ID媛 ?놁뒿?덈떎.")
        return

    # Supabase REST API?먯꽌 IN 荑쇰━: video_id=in.(id1,id2,...)
    ids_str = ','.join(str(vid) for vid in video_ids)
    all_signals = db.select(
        'influencer_signals',
        f'video_id=in.({ids_str})&review_status=neq.rejected&select=id,video_id,stock,signal,timestamp,key_quote,reasoning,speaker,pipeline_version'
    )

    print(f"  ???쒓렇??{len(all_signals)}媛?諛쒓껄 (rejected ?쒖쇅)")

    if not all_signals:
        print("  ???щ텇?앺븷 ?쒓렇?먯씠 ?놁뒿?덈떎.")
        return

    # ?? STEP 4: 鍮꾨뵒?ㅻ퀎 洹몃９????????????????????????????????
    video_signals: dict[str, list] = {}
    for sig in all_signals:
        vid = str(sig['video_id'])
        if vid not in video_signals:
            video_signals[vid] = []
        video_signals[vid].append(sig)

    total_videos = len(video_signals)
    total_signals = len(all_signals)
    print(f"\n  ?뱤 遺꾩꽍 ??? ?곸긽 {total_videos}媛? ?쒓렇??{total_signals}媛?)
    print(f"  ??툘  ?댁쟾 吏꾪뻾: ?곸긽 {len(processed_video_ids)}媛??꾨즺\n")

    # ?? STEP 5: ?곸긽蹂??щ텇??????????????????????????????????
    update_count = 0
    reject_count = 0
    error_count = 0

    for video_idx, (vid_id, signals) in enumerate(video_signals.items(), 1):
        if vid_id in processed_video_ids:
            print(f"  ??툘  [{video_idx}/{total_videos}] ?대? 泥섎━?? 嫄대꼫?")
            continue

        video = video_map.get(int(vid_id) if vid_id.isdigit() else vid_id)
        if not video:
            print(f"  ?좑툘  [{video_idx}/{total_videos}] ?곸긽 ?뺣낫 ?놁쓬 (id={vid_id})")
            continue

        title = video.get('title', '?쒕ぉ ?놁쓬')
        subtitle = video.get('subtitle') or video.get('transcript') or ''
        sig_count = len(signals)

        print(f"\n[吏꾪뻾] ?곸긽 {video_idx}/{total_videos}: {title[:50]} (?쒓렇??{sig_count}媛?")

        if not subtitle:
            print(f"  ?좑툘  ?먮쭑 ?놁쓬. ?쒓렇??{sig_count}媛?嫄대꼫?.")
            processed_video_ids.append(vid_id)
            save_progress({**progress, 'processed_video_ids': processed_video_ids,
                           'updated_signal_ids': updated_ids, 'total_cost': total_cost})
            continue

        # V11 ?щ텇???꾨＼?꾪듃 ?앹꽦
        prompt = build_reanalysis_prompt(v11_prompt, title, subtitle, signals)

        # API ?몄텧
        try:
            response = ai.messages.create(
                model=MODEL,
                max_tokens=4096,
                messages=[{'role': 'user', 'content': prompt}]
            )
            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            call_cost = input_tokens * INPUT_PRICE_PER_TOKEN + output_tokens * OUTPUT_PRICE_PER_TOKEN
            total_cost += call_cost
            print(f"  ?뮠 API ?몄텧 ?꾨즺 (in={input_tokens:,}tok, out={output_tokens:,}tok, 鍮꾩슜=${call_cost:.4f})")
        except Exception as e:
            print(f"  ??API ?몄텧 ?ㅽ뙣: {e}")
            error_count += 1
            time.sleep(5)
            continue

        # ?묐떟 ?뚯떛
        results = parse_api_response(content)
        if not results:
            print(f"  ?좑툘  ?뚯떛??寃곌낵 ?놁쓬.")
            error_count += 1
            continue

        # 寃곌낵 留ㅽ븨 (signal_id ??result)
        result_map = {str(r.get('signal_id', '')): r for r in results}

        # 媛??쒓렇??泥섎━
        for sig in signals:
            sig_id = str(sig['id'])
            result = result_map.get(sig_id)

            if not result:
                print(f"  ?좑툘  ?쒓렇??{sig_id} 寃곌낵 ?놁쓬")
                continue

            action = result.get('action', 'update')
            stock = sig.get('stock', '?')

            if action == 'reject':
                # rejected濡??낅뜲?댄듃
                reject_reason = result.get('reject_reason', 'V11 洹쒖튃 ?꾨컲')
                db.update('influencer_signals', {'id': sig_id}, {
                    'review_status': 'rejected',
                    'reasoning': f"[V11 ?먮룞 嫄곕?] {reject_reason}",
                    'pipeline_version': 'V11'
                })
                print(f"  ?슟 {stock}: 嫄곕? ??{reject_reason[:50]}")
                reject_count += 1

            else:
                # ?낅뜲?댄듃
                new_signal = result.get('signal', sig.get('signal'))
                new_timestamp = result.get('timestamp', sig.get('timestamp'))
                new_key_quote = result.get('key_quote', sig.get('key_quote'))
                new_reasoning = result.get('reasoning', sig.get('reasoning'))

                # ??꾩뒪?ы봽 ?좏슚??寃利?                if not is_valid_timestamp(new_timestamp):
                    # ?좏슚?섏? ?딆쑝硫?湲곗〈 媛??좎? ?먮뒗 寃쎄퀬
                    print(f"  ?좑툘  {stock}: ??꾩뒪?ы봽 ?뺤떇 遺덈웾 '{new_timestamp}' ??湲곗〈 媛??좎?")
                    new_timestamp = sig.get('timestamp')

                update_data = {
                    'signal': new_signal,
                    'timestamp': new_timestamp,
                    'key_quote': new_key_quote,
                    'reasoning': new_reasoning,
                    'pipeline_version': 'V11'
                }

                db.update('influencer_signals', {'id': sig_id}, update_data)
                old_signal = sig.get('signal', '?')
                changed = '?? if new_signal != old_signal else '  '
                print(f"  {changed} {stock}: {old_signal} ??{new_signal} | timestamp: {new_timestamp}")
                update_count += 1
                updated_ids.append(sig_id)

        # 吏꾪뻾?곹솴 ???        processed_video_ids.append(vid_id)
        progress_data = {
            'processed_video_ids': processed_video_ids,
            'updated_signal_ids': updated_ids,
            'total_cost': total_cost,
            'started_at': progress.get('started_at', datetime.now().isoformat()),
            'last_updated': datetime.now().isoformat()
        }
        save_progress(progress_data)

        # API ?덉씠?몃━諛?諛⑹?
        time.sleep(2)

    # ?? ?꾨즺 由ы룷????????????????????????????????????????????
    print("\n" + "=" * 60)
    print("???꾨즺 由ы룷??)
    print("=" * 60)
    print(f"  泥섎━???곸긽:        {len(processed_video_ids)} / {total_videos}媛?)
    print(f"  ?낅뜲?댄듃???쒓렇??  {update_count}媛?)
    print(f"  嫄곕????쒓렇??      {reject_count}媛?)
    print(f"  ?ㅻ쪟 諛쒖깮:          {error_count}嫄?)
    print(f"  珥?API 鍮꾩슜:        ${total_cost:.4f}")
    print(f"  吏꾪뻾?곹솴 ?뚯씪:      {PROGRESS_FILE}")
    print(f"  ?꾨즺 ?쒓컖:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()

