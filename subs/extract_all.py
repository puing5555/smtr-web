"""Extract transcripts for all target videos using youtube-transcript-api"""
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi

SUBS_DIR = "C:/Users/Mario/work/subs"

# Videos to extract - investment-related only
VIDEOS = {
    # 슈카월드
    "syuka_4QlLhzLfhzU": {"id": "4QlLhzLfhzU", "channel": "슈카월드"},
    "syuka_g19QLu5tZlo": {"id": "g19QLu5tZlo", "channel": "슈카월드"},
    "syuka_wPKfa2qWh4U": {"id": "wPKfa2qWh4U", "channel": "슈카월드"},
    # 이효석 - investment related
    "hyoseok_B2ARIKugV-k": {"id": "B2ARIKugV-k", "channel": "이효석아카데미"},
    "hyoseok_rpoGBOJZ2fk": {"id": "rpoGBOJZ2fk", "channel": "이효석아카데미"},
    "hyoseok_xtl0nnxAYKc": {"id": "xtl0nnxAYKc", "channel": "이효석아카데미"},
    "hyoseok_fDZnPoK5lyc": {"id": "fDZnPoK5lyc", "channel": "이효석아카데미"},
    "hyoseok_ZXuQCpuVCYc": {"id": "ZXuQCpuVCYc", "channel": "이효석아카데미"},
    "hyoseok_tSXkj2Omz34": {"id": "tSXkj2Omz34", "channel": "이효석아카데미"},
    # 부읽남TV - investment related (skip Xv-wNA91EPE already done)
    "booread_BVRoApF0c8k": {"id": "BVRoApF0c8k", "channel": "부읽남TV"},
    "booread_nwuAhWEoAng": {"id": "nwuAhWEoAng", "channel": "부읽남TV"},
    "booread_CFY_pEYLpaU": {"id": "CFY_pEYLpaU", "channel": "부읽남TV"},
    "booread_vVurVxsXvoM": {"id": "vVurVxsXvoM", "channel": "부읽남TV"},
    "booread_f3XyT2v2WVc": {"id": "f3XyT2v2WVc", "channel": "부읽남TV"},
    "booread_zh2ucctO00c": {"id": "zh2ucctO00c", "channel": "부읽남TV"},
    "booread_lfsT3hO1GqQ": {"id": "lfsT3hO1GqQ", "channel": "부읽남TV"},
    "booread_8Nn3qerCt44": {"id": "8Nn3qerCt44", "channel": "부읽남TV"},
    # 달란트투자 - investment related
    "dalrant_MrBnIb0jOk": {"id": "_MrBnIb0jOk", "channel": "달란트투자"},
    "dalrant_kFa9RxL4HnA": {"id": "kFa9RxL4HnA", "channel": "달란트투자"},
}

results = {"success": [], "failed": []}

for key, info in VIDEOS.items():
    outpath = os.path.join(SUBS_DIR, f"{key}.json")
    # Skip if already has transcript data
    if os.path.exists(outpath):
        try:
            with open(outpath, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            if existing.get('subtitles') and len(existing['subtitles']) > 0:
                print(f"SKIP {key}: already has {len(existing['subtitles'])} segments")
                results["success"].append(key)
                continue
        except:
            pass
    
    vid = info["id"]
    print(f"Extracting {key} ({vid})...", end=" ")
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(vid, languages=['ko', 'en'])
        transcript = fetched.to_raw_data()
        data = {
            "video_id": vid,
            "channel": info["channel"],
            "subtitles": transcript
        }
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"OK ({len(transcript)} segments)")
        results["success"].append(key)
    except Exception as e:
        print(f"FAILED: {e}")
        results["failed"].append({"key": key, "error": str(e)})

print(f"\n=== Results: {len(results['success'])} success, {len(results['failed'])} failed ===")
for f in results["failed"]:
    print(f"  FAILED: {f['key']} - {f['error'][:80]}")
