import json, subprocess, re, sys

channels = {
    "한국주식": {
        "삼프로TV": "@3protv",
        "부읽남TV": "@buridnam",
        "주코노미": "@jooconomy",
        "염승환 투자노트": "@yeominvest",
        "한국경제TV": "@wolowtv",
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
                ["python", "-m", "yt_dlp", "--flat-playlist", "--dump-json", "--playlist-end", "1", url],
                capture_output=True, text=True, timeout=30
            )
            # Try to get channel metadata from the playlist info
            # Use playlist-items 0 approach instead
            r2 = subprocess.run(
                ["python", "-m", "yt_dlp", "--dump-single-json", "--flat-playlist", "--playlist-end", "0", url],
                capture_output=True, text=True, timeout=30
            )
            if r2.returncode == 0 and r2.stdout.strip():
                data = json.loads(r2.stdout.strip())
                video_count = data.get("playlist_count") or len(data.get("entries", []))
                # Try to find subscriber count in channel metadata
                uploader = data.get("uploader", name)
                channel_url = data.get("channel_url", f"https://www.youtube.com/{handle}")
                actual_handle = data.get("channel_id", handle)
                
                # Get the webpage URL to find the actual handle
                webpage = data.get("webpage_url", "")
                real_handle = handle
                if "uploader_id" in data and data["uploader_id"]:
                    real_handle = data["uploader_id"] if data["uploader_id"].startswith("@") else f"@{data['uploader_id']}"
                
                results.append({
                    "name": name,
                    "category": category,
                    "youtube_handle": real_handle,
                    "video_count": video_count,
                    "subscriber_estimate": "N/A"
                })
                print(f"  -> {video_count} videos", flush=True)
            else:
                print(f"  -> FAILED: {r2.stderr[:200]}", flush=True)
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
# Summary
for r in results:
    status = f"{r['video_count']} videos" if r['video_count'] > 0 else "FAILED"
    print(f"  {r['name']}: {status}")
