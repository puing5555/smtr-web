import json, subprocess, sys

channels = {
    "한국주식": {
        "삼프로TV": "@3protv",
        "부읽남TV": "@buridnam",
        "주코노미": "@jooconomy",
        "염승환 투자노트": "@yeominvest",
        "한국경제TV": "@WOWTV",
        "이효석아카데미": "@hyoseokacademy",
        "소수몽키": "@sosumonkey",
        "삼성증권": "@SamsungSecurities",
        "미래에셋증권": "@MiraeAssetSecurities",
        "달란트투자": "@dalranttuja",
        "KB증권": "@kbsec",
        "세상학개론": "@sesanghak",
        "이베스트스탁": "@ebesttv",
        "코린이아빠": "@coriniappa",
    },
    "미국주식": {
        "미주은": "@mijueun",
        "미부": "@mibustocks",
        "뉴욕주민": "@newyorkjumin",
        "재테크하는 공대누나": "@gongdaenuna",
        "한그루": "@hangru",
        "수페TV": "@supetv",
        "머스야": "@meosya",
        "래퍼투자": "@rappertuja",
        "미국주식 주주총회": "@jujuchonghoe",
        "배당쟁이": "@baedangjaengi",
        "정신과의사 투자클럽": "@psychiatrist_invest",
        "미래에셋 글로벌": "@MiraeAssetGlobal",
        "나스닥매니아": "@nasdaqmania",
        "테크형": "@techhyung",
        "노미의 글로벌 투자": "@nomi_global",
        "미국주식 사관학교": "@usstock_academy",
    },
    "크립토": {
        "김치코인": "@kimchicoin",
        "크립토지니": "@cryptogenie",
        "비트코인갤러리": "@bitcoingallery",
        "코인읽어주는남자": "@coinman",
        "크립토퀀트": "@CryptoQuant",
        "땡글아카데미": "@ddangle",
    },
}

results = []
for category, ch_dict in channels.items():
    for name, handle in ch_dict.items():
        url = f"https://www.youtube.com/{handle}/videos"
        print(f"Fetching {name} ({handle})...", flush=True)
        try:
            r = subprocess.run(
                ["python", "-m", "yt_dlp", "--dump-single-json", "--flat-playlist", url],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0 and r.stdout.strip():
                data = json.loads(r.stdout.strip())
                video_count = data.get("playlist_count", 0) or len(data.get("entries", []))
                real_handle = handle
                if data.get("uploader_id"):
                    uid = data["uploader_id"]
                    real_handle = uid if uid.startswith("@") else f"@{uid}"
                
                # Try to get subscriber count from channel metadata
                sub = data.get("channel_follower_count", "N/A")
                if isinstance(sub, int):
                    if sub >= 10000:
                        sub_str = f"{sub//10000}만"
                    elif sub >= 1000:
                        sub_str = f"{sub/1000:.1f}천"
                    else:
                        sub_str = str(sub)
                else:
                    sub_str = "N/A"
                
                results.append({
                    "name": name,
                    "category": category,
                    "youtube_handle": real_handle,
                    "video_count": video_count,
                    "subscriber_estimate": sub_str
                })
                print(f"  -> {video_count} videos, {sub_str} subs", flush=True)
            else:
                err = r.stderr[:300] if r.stderr else "no output"
                print(f"  -> FAILED: {err}", flush=True)
                results.append({
                    "name": name,
                    "category": category,
                    "youtube_handle": handle,
                    "video_count": -1,
                    "subscriber_estimate": "N/A"
                })
        except Exception as e:
            print(f"  -> ERROR: {e}", flush=True)
            results.append({
                "name": name,
                "category": category,
                "youtube_handle": handle,
                "video_count": -1,
                "subscriber_estimate": "N/A"
            })

with open(r"C:\Users\Mario\work\data\channel_video_counts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone! {len(results)} channels saved.")
for r in results:
    status = f"{r['video_count']} videos" if r['video_count'] > 0 else "FAILED"
    print(f"  {r['name']}: {status}")
