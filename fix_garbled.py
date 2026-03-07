import json
import urllib.request
import urllib.parse

KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals"

def patch(filter_str, body_dict, label):
    url = f"{BASE}?{filter_str}"
    body = json.dumps(body_dict).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=body,
        method='PATCH',
        headers={
            'apikey': KEY,
            'Authorization': f'Bearer {KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            print(f"OK [{label}]: {len(result)}건 UPDATE")
            return len(result)
    except Exception as e:
        print(f"FAIL [{label}]: {e}")
        return 0

total = 0

# Fix garbled records using ticker filter + stock=like.*?*
# Since the garbled stocks contain "?", use ticker to identify them

# 000660: SK???? → SK하이닉스
total += patch("ticker=eq.000660&stock=neq.SK%ED%95%98%EC%9D%B4%EB%8B%89%EC%8A%A4", {"stock": "SK하이닉스"}, "000660 SK하이닉스")

# 005380: ??? → 현대차
total += patch("ticker=eq.005380&stock=neq.%ED%98%84%EB%8C%80%EC%B0%A8", {"stock": "현대차"}, "005380 현대차")

# 005930: ???? → 삼성전자
total += patch("ticker=eq.005930&stock=neq.%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90", {"stock": "삼성전자"}, "005930 삼성전자")

# 267260: 현대일렉트릭앤에너지시스템 → HD현대일렉트릭
total += patch("ticker=eq.267260&stock=neq.HD%ED%98%84%EB%8C%80%EC%9D%BC%EB%A0%89%ED%8A%B8%EB%A6%AD", {"stock": "HD현대일렉트릭"}, "267260 HD현대일렉트릭")

# ARM: ARM??? → ARM홀딩스
total += patch("ticker=eq.ARM&stock=neq.ARM%ED%99%80%EB%94%A9%EC%8A%A4", {"stock": "ARM홀딩스"}, "ARM ARM홀딩스")

# BAC: ???????? → 뱅크오브아메리카
total += patch("ticker=eq.BAC&stock=neq.%EB%B1%85%ED%81%AC%EC%98%A4%EB%B8%8C%EC%95%84%EB%A9%94%EB%A6%AC%EC%B9%B4", {"stock": "뱅크오브아메리카"}, "BAC 뱅크오브아메리카")

# BRK.A: ??? ???? → 버크셔 해서웨이
total += patch("ticker=eq.BRK.A&stock=neq.%EB%B2%84%ED%81%AC%EC%85%94%20%ED%95%B4%EC%84%9C%EC%9B%A8%EC%9D%B4", {"stock": "버크셔 해서웨이"}, "BRK.A 버크셔해서웨이")

# BTC: ???? → 비트코인
total += patch("ticker=eq.BTC&stock=neq.%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8", {"stock": "비트코인"}, "BTC 비트코인")

# CB: ?? → 처브
total += patch("ticker=eq.CB&stock=neq.%EC%B2%98%EB%B8%8C", {"stock": "처브"}, "CB 처브")

# CDNS: ???? ??? → 케이던스 디자인
total += patch("ticker=eq.CDNS&stock=neq.%EC%BC%80%EC%9D%B4%EB%8D%98%EC%8A%A4%20%EB%94%94%EC%9E%90%EC%9D%B8", {"stock": "케이던스 디자인"}, "CDNS 케이던스디자인")

# GLD: ? → 금
total += patch("ticker=eq.GLD&stock=neq.%EA%B8%88", {"stock": "금"}, "GLD 금")

# GOOGL: ?? → 구글
total += patch("ticker=eq.GOOGL&stock=neq.%EA%B5%AC%EA%B8%80", {"stock": "구글"}, "GOOGL 구글")

# MSFT: ??????? → 마이크로소프트
total += patch("ticker=eq.MSFT&stock=neq.%EB%A7%88%EC%9D%B4%ED%81%AC%EB%A1%9C%EC%86%8C%ED%94%84%ED%8A%B8", {"stock": "마이크로소프트"}, "MSFT 마이크로소프트")

# MU: ???? → 마이크론
total += patch("ticker=eq.MU&stock=neq.%EB%A7%88%EC%9D%B4%ED%81%AC%EB%A1%A0", {"stock": "마이크론"}, "MU 마이크론")

# NVDA: ???? → 엔비디아
total += patch("ticker=eq.NVDA&stock=neq.%EC%97%94%EB%B9%84%EB%94%94%EC%95%84", {"stock": "엔비디아"}, "NVDA 엔비디아")

# OXY: ???? ????? → 옥시덴탈 페트롤리엄
total += patch("ticker=eq.OXY&stock=neq.%EC%98%A5%EC%8B%9C%EB%8D%B4%ED%83%88%20%ED%8E%98%ED%8A%B8%EB%A1%A4%EB%A6%AC%EC%97%84", {"stock": "옥시덴탈 페트롤리엄"}, "OXY 옥시덴탈페트롤리엄")

# PLTR: ???? → 팔란티어
total += patch("ticker=eq.PLTR&stock=neq.%ED%8C%94%EB%9E%80%ED%8B%B0%EC%96%B4", {"stock": "팔란티어"}, "PLTR 팔란티어")

# STZ: ?????? ??? → 컨스텔레이션 브랜즈
total += patch("ticker=eq.STZ&stock=neq.%EC%BB%A8%EC%8A%A4%ED%85%94%EB%A0%88%EC%9D%B4%EC%85%98%20%EB%B8%8C%EB%9E%9C%EC%A6%88", {"stock": "컨스텔레이션 브랜즈"}, "STZ 컨스텔레이션브랜즈")

# GEV check - update any remaining non-standard
total += patch("ticker=eq.GEV&stock=neq.GE%EB%B2%84%EB%85%B8%EB%B0%94", {"stock": "GE버노바"}, "GEV GE버노바")

# IREN check
total += patch("ticker=eq.IREN&stock=neq.IREN", {"stock": "IREN"}, "IREN cleanup")

print(f"\n총 {total}건 재수정 완료")
