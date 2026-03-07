#!/usr/bin/env python3
"""
세상학개론 V11 재분석 스크립트
- DB에서 세상학개론 채널 시그널을 가져와 V11 프롬프트로 재분석
- 비디오별 그룹핑으로 API 호출 효율화 (같은 영상의 시그널은 1번만 호출)
- 결과를 DB에 UPDATE하고 진행상황 저장
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import anthropic
import requests

# ─── 환경 설정 ───────────────────────────────────────────────
SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
ANTHROPIC_KEY = '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'
MODEL = 'claude-sonnet-4-20250514'
PROMPT_FILE = 'C:/Users/Mario/work/prompts/pipeline_v11.md'
PROGRESS_FILE = 'C:/Users/Mario/work/data/sesang_v11_progress.json'

# API 비용 추적 (claude-sonnet-4 기준: input $3/M, output $15/M)
INPUT_PRICE_PER_TOKEN = 3.0 / 1_000_000
OUTPUT_PRICE_PER_TOKEN = 15.0 / 1_000_000

# ─── Supabase 클라이언트 ──────────────────────────────────────
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


# ─── 진행상황 저장/불러오기 ──────────────────────────────────
def load_progress() -> dict:
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'processed_video_ids': [], 'updated_signal_ids': [], 'total_cost': 0.0, 'started_at': datetime.now().isoformat()}


def save_progress(progress: dict):
    Path(PROGRESS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


# ─── V11 프롬프트 로드 ───────────────────────────────────────
def load_v11_prompt() -> str:
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()


# ─── 재분석 프롬프트 생성 ────────────────────────────────────
def build_reanalysis_prompt(v11_prompt: str, video_title: str, subtitle: str, signals: list) -> str:
    """
    V11 프롬프트 + 기존 시그널 목록 + 자막으로 재분석 요청 프롬프트 생성
    """
    signal_list = '\n'.join(
        f"  - 시그널ID={s['id']}, 종목={s.get('stock','?')}, 현재신호={s.get('signal','?')}, 현재타임스탬프={s.get('timestamp','?')}"
        for s in signals
    )

    return f"""
{v11_prompt}

---

## 재분석 요청

아래 영상의 기존 시그널들을 V11 규칙에 따라 재검토하세요.

**영상 제목**: {video_title}

**자막**:
{subtitle[:15000] if subtitle else '(자막 없음)'}

**기존 시그널 목록** (재분석 대상):
{signal_list}

---

## 출력 요구사항

각 시그널 ID별로 다음 형식의 JSON을 출력하세요:

```json
{{
  "results": [
    {{
      "signal_id": "<기존 시그널 ID>",
      "action": "update" | "reject",
      "signal": "매수|긍정|중립|부정|매도",
      "timestamp": "MM:SS 또는 HH:MM:SS 형식만",
      "key_quote": "핵심 발언 원문 20자 이상",
      "reasoning": "V11 규칙 기준 분류 이유",
      "reject_reason": "action=reject일 때만: 거부 이유 (가정형발언/지수종목/타임스탬프없음 등)"
    }}
  ]
}}
```

**V11 핵심 체크리스트**:
1. 가정형 발언("만약/~했다면/~이었다면") → action=reject
2. 지수/달러/원자재(코스피/달러/금 등) → action=reject
3. 타임스탬프를 자막에서 최대한 찾아 MM:SS 형식으로 → 찾을 수 없으면 confidence=low
4. 매수 기준: "본인이 샀거나 사라고 했는가?" → Yes=매수 / No=긍정

JSON만 출력하세요. 다른 설명 없이.
"""


# ─── API 응답 파싱 ───────────────────────────────────────────
def parse_api_response(content: str) -> list:
    """API 응답에서 JSON 결과 추출"""
    # ```json ... ``` 블록 추출
    match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # JSON 블록 없으면 전체에서 { "results": ... } 패턴 찾기
        match = re.search(r'\{.*?"results".*?\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            print(f"  ⚠️  JSON 파싱 실패. 응답 내용:\n{content[:500]}")
            return []

    try:
        data = json.loads(json_str)
        return data.get('results', [])
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON 디코드 오류: {e}")
        return []


# ─── 타임스탬프 유효성 검증 ──────────────────────────────────
def is_valid_timestamp(ts: str) -> bool:
    """HH:MM:SS 또는 MM:SS 형식인지 확인"""
    if not ts:
        return False
    # 금지 패턴
    forbidden = ['N/A', 'n/a', '없음', '미상', '초반', '중반', '후반', '전체', '날짜', '월', '일']
    for f in forbidden:
        if f in str(ts):
            return False
    # 형식 체크
    pattern = r'^\d{1,2}:\d{2}(:\d{2})?$'
    if not re.match(pattern, str(ts)):
        return False
    # 0:00 금지
    if ts in ['0:00', '00:00', '00:00:00']:
        return False
    return True


# ─── 메인 실행 ───────────────────────────────────────────────
def main():
    print("=" * 60)
    print("세상학개론 V11 재분석 스크립트")
    print(f"시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 클라이언트 초기화
    db = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    ai = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    # V11 프롬프트 로드
    print("\n[준비] V11 프롬프트 로드 중...")
    v11_prompt = load_v11_prompt()
    print(f"  ✓ 프롬프트 로드 완료 ({len(v11_prompt):,} 자)")

    # 진행상황 불러오기
    progress = load_progress()
    total_cost = progress.get('total_cost', 0.0)
    updated_ids = progress.get('updated_signal_ids', [])
    processed_video_ids = progress.get('processed_video_ids', [])

    # ── STEP 1: 세상학개론 채널 ID 찾기 ──────────────────────
    print("\n[STEP 1] 세상학개론 채널 찾기...")
    channels = db.select('influencer_channels', 'channel_name=ilike.*세상학개론*&select=id,channel_name,channel_id')
    if not channels:
        # 한글 ilike가 안 될 경우 전체 조회 후 필터
        channels = db.select('influencer_channels', 'select=id,channel_name,channel_id')
        channels = [c for c in channels if '세상학개론' in (c.get('channel_name') or '')]

    if not channels:
        print("  ❌ 세상학개론 채널을 찾을 수 없습니다.")
        print("  → influencer_channels 테이블의 channel_name 컬럼을 확인하세요.")
        return

    channel = channels[0]
    channel_db_id = channel['id']
    channel_yt_id = channel.get('channel_id', '')
    print(f"  ✓ 채널 발견: {channel['channel_name']} (DB ID: {channel_db_id})")

    # ── STEP 2: 세상학개론 영상 목록 가져오기 ────────────────
    print("\n[STEP 2] 세상학개론 영상 목록 조회...")
    videos = db.select(
        'influencer_videos',
        f'channel_id=eq.{channel_db_id}&select=id,video_id,title,subtitle,transcript'
    )
    if not videos:
        # channel_id가 YouTube channel_id를 참조하는 경우
        videos = db.select(
            'influencer_videos',
            f'channel_id=eq.{channel_yt_id}&select=id,video_id,title,subtitle,transcript'
        )

    print(f"  ✓ 영상 {len(videos)}개 발견")

    if not videos:
        print("  ❌ 영상 데이터가 없습니다. DB 구조를 확인하세요.")
        return

    video_map = {v['id']: v for v in videos}
    video_ids = [v['id'] for v in videos]

    # ── STEP 3: 시그널 가져오기 (review_status != rejected) ──
    print("\n[STEP 3] 세상학개론 시그널 조회...")
    # video_id IN (...)로 쿼리
    if not video_ids:
        print("  ❌ 영상 ID가 없습니다.")
        return

    # Supabase REST API에서 IN 쿼리: video_id=in.(id1,id2,...)
    ids_str = ','.join(str(vid) for vid in video_ids)
    all_signals = db.select(
        'influencer_signals',
        f'video_id=in.({ids_str})&review_status=neq.rejected&select=id,video_id,stock,signal,timestamp,key_quote,reasoning,speaker,pipeline_version'
    )

    print(f"  ✓ 시그널 {len(all_signals)}개 발견 (rejected 제외)")

    if not all_signals:
        print("  ❌ 재분석할 시그널이 없습니다.")
        return

    # ── STEP 4: 비디오별 그룹핑 ──────────────────────────────
    video_signals: dict[str, list] = {}
    for sig in all_signals:
        vid = str(sig['video_id'])
        if vid not in video_signals:
            video_signals[vid] = []
        video_signals[vid].append(sig)

    total_videos = len(video_signals)
    total_signals = len(all_signals)
    print(f"\n  📊 분석 대상: 영상 {total_videos}개, 시그널 {total_signals}개")
    print(f"  ⏭️  이전 진행: 영상 {len(processed_video_ids)}개 완료\n")

    # ── STEP 5: 영상별 재분석 ────────────────────────────────
    update_count = 0
    reject_count = 0
    error_count = 0

    for video_idx, (vid_id, signals) in enumerate(video_signals.items(), 1):
        if vid_id in processed_video_ids:
            print(f"  ⏭️  [{video_idx}/{total_videos}] 이미 처리됨, 건너뜀")
            continue

        video = video_map.get(int(vid_id) if vid_id.isdigit() else vid_id)
        if not video:
            print(f"  ⚠️  [{video_idx}/{total_videos}] 영상 정보 없음 (id={vid_id})")
            continue

        title = video.get('title', '제목 없음')
        subtitle = video.get('subtitle') or video.get('transcript') or ''
        sig_count = len(signals)

        print(f"\n[진행] 영상 {video_idx}/{total_videos}: {title[:50]} (시그널 {sig_count}개)")

        if not subtitle:
            print(f"  ⚠️  자막 없음. 시그널 {sig_count}개 건너뜀.")
            processed_video_ids.append(vid_id)
            save_progress({**progress, 'processed_video_ids': processed_video_ids,
                           'updated_signal_ids': updated_ids, 'total_cost': total_cost})
            continue

        # V11 재분석 프롬프트 생성
        prompt = build_reanalysis_prompt(v11_prompt, title, subtitle, signals)

        # API 호출
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
            print(f"  💬 API 호출 완료 (in={input_tokens:,}tok, out={output_tokens:,}tok, 비용=${call_cost:.4f})")
        except Exception as e:
            print(f"  ❌ API 호출 실패: {e}")
            error_count += 1
            time.sleep(5)
            continue

        # 응답 파싱
        results = parse_api_response(content)
        if not results:
            print(f"  ⚠️  파싱된 결과 없음.")
            error_count += 1
            continue

        # 결과 매핑 (signal_id → result)
        result_map = {str(r.get('signal_id', '')): r for r in results}

        # 각 시그널 처리
        for sig in signals:
            sig_id = str(sig['id'])
            result = result_map.get(sig_id)

            if not result:
                print(f"  ⚠️  시그널 {sig_id} 결과 없음")
                continue

            action = result.get('action', 'update')
            stock = sig.get('stock', '?')

            if action == 'reject':
                # rejected로 업데이트
                reject_reason = result.get('reject_reason', 'V11 규칙 위반')
                db.update('influencer_signals', {'id': sig_id}, {
                    'review_status': 'rejected',
                    'reasoning': f"[V11 자동 거부] {reject_reason}",
                    'pipeline_version': 'V11'
                })
                print(f"  🚫 {stock}: 거부 → {reject_reason[:50]}")
                reject_count += 1

            else:
                # 업데이트
                new_signal = result.get('signal', sig.get('signal'))
                new_timestamp = result.get('timestamp', sig.get('timestamp'))
                new_key_quote = result.get('key_quote', sig.get('key_quote'))
                new_reasoning = result.get('reasoning', sig.get('reasoning'))

                # 타임스탬프 유효성 검증
                if not is_valid_timestamp(new_timestamp):
                    # 유효하지 않으면 기존 값 유지 또는 경고
                    print(f"  ⚠️  {stock}: 타임스탬프 형식 불량 '{new_timestamp}' → 기존 값 유지")
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
                changed = '✅' if new_signal != old_signal else '  '
                print(f"  {changed} {stock}: {old_signal} → {new_signal} | timestamp: {new_timestamp}")
                update_count += 1
                updated_ids.append(sig_id)

        # 진행상황 저장
        processed_video_ids.append(vid_id)
        progress_data = {
            'processed_video_ids': processed_video_ids,
            'updated_signal_ids': updated_ids,
            'total_cost': total_cost,
            'started_at': progress.get('started_at', datetime.now().isoformat()),
            'last_updated': datetime.now().isoformat()
        }
        save_progress(progress_data)

        # API 레이트리밋 방지
        time.sleep(2)

    # ── 완료 리포트 ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ 완료 리포트")
    print("=" * 60)
    print(f"  처리된 영상:        {len(processed_video_ids)} / {total_videos}개")
    print(f"  업데이트된 시그널:  {update_count}개")
    print(f"  거부된 시그널:      {reject_count}개")
    print(f"  오류 발생:          {error_count}건")
    print(f"  총 API 비용:        ${total_cost:.4f}")
    print(f"  진행상황 파일:      {PROGRESS_FILE}")
    print(f"  완료 시각:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
