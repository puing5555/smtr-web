# -*- coding: utf-8 -*-
import httpx
import json

DART_API_KEY = "e4523175bccca28542cb423e21adb2ef080cc2f5"
BOT_TOKEN = "8372148836:AAESXt8bGqST7G053yTUE4P2PS8RLMIyGBk"
CHAT_ID = "-1003764256213"

# 1. DART 공시 가져오기
print("Fetching DART filings...")
r = httpx.get("https://opendart.fss.or.kr/api/list.json", params={
    "crtfc_key": DART_API_KEY,
    "bgn_de": "20260219",
    "end_de": "20260220",
})
data = r.json()
filings = data.get("list", [])
print(f"Found {len(filings)} filings")

# 2. 알림 메시지 만들기
msg = "\U0001f4e2 DART \uacf5\uc2dc \uc54c\ub9bc (2026-02-19 ~ 02-20)\n\n"
for f in filings:
    corp = f["corp_name"]
    report = f["report_nm"]
    date = f["rcept_dt"]
    rcept_no = f["rcept_no"]
    link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
    msg += f"\u2022 {corp} - {report}\n  {link}\n\n"

msg += f"\ucd1d {len(filings)}\uac74"

# 3. 텔레그램으로 보내기
print("Sending to Telegram...")
r = httpx.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True}
)
result = r.json()
print(f"OK: {result.get('ok')}")
