"""
한국 시장 심리지수 v7 - 데이터 소스 테스트
각 지표의 데이터 수집 가능 여부 테스트
"""

import warnings
warnings.filterwarnings('ignore')

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time

TODAY = datetime.today().strftime('%Y%m%d')
YESTERDAY = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
DATE_30AGO = (datetime.today() - timedelta(days=90)).strftime('%Y%m%d')

RESULTS = {}


# ─────────────────────────────────────────────
# 1. 모멘텀: 코스피 vs 50일 이평
# ─────────────────────────────────────────────
def fetch_momentum(date=None):
    """코스피 현재가 vs 50일 이동평균 괴리율 (%)"""
    try:
        import yfinance as yf
        ks11 = yf.download("^KS11", period="120d", progress=False, auto_adjust=True)
        if ks11.empty or len(ks11) < 50:
            return None
        close = ks11['Close'].squeeze()
        current = float(close.iloc[-1])
        ma50 = float(close.iloc[-50:].mean())
        raw = (current - ma50) / ma50 * 100  # % 괴리율
        return raw, current, ma50
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 2. 주가강도: 52주 신고가/신저가 비율
# ─────────────────────────────────────────────
def fetch_price_strength(date=None):
    """신고가/(신고가+신저가) 비율"""
    try:
        from pykrx import stock
        # 최근 거래일 기준 종목별 시가/고가/저가/종가
        tickers = stock.get_market_ticker_list(TODAY, market="KOSPI")
        if not tickers:
            tickers = stock.get_market_ticker_list(YESTERDAY, market="KOSPI")
        
        start_52w = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')
        
        high_52w_count = 0
        low_52w_count = 0
        
        # 샘플링 (상위 100종목)
        sample = tickers[:100]
        for ticker in sample:
            try:
                df = stock.get_market_ohlcv_by_date(start_52w, TODAY, ticker)
                if df.empty or len(df) < 10:
                    continue
                current_close = float(df['종가'].iloc[-1])
                high_52w = float(df['고가'].max())
                low_52w = float(df['저가'].min())
                
                if current_close >= high_52w * 0.98:
                    high_52w_count += 1
                elif current_close <= low_52w * 1.02:
                    low_52w_count += 1
            except:
                continue
        
        total = high_52w_count + low_52w_count
        if total == 0:
            return None, "신고가+신저가=0", None
        raw = high_52w_count / total
        return raw, high_52w_count, low_52w_count
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 3. 시장폭: 상승/하락 종목 비율 (KRX OTP 방식)
# ─────────────────────────────────────────────
def fetch_market_breadth_krx(date=None):
    """KRX 직접 크롤링으로 상승/하락 종목 수"""
    try:
        # 최근 영업일 찾기
        target_date = datetime.today()
        if target_date.weekday() >= 5:  # 토/일
            target_date -= timedelta(days=target_date.weekday() - 4)
        date_str = target_date.strftime('%Y%m%d')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://data.krx.co.kr/'
        }
        
        # OTP 생성
        otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
        otp_params = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
            "name": "fileDown",
            "filetype": "csv",
            "mktId": "STK",
            "trdDd": date_str,
            "share": "1",
            "money": "1",
            "csvxls_isNo": "false"
        }
        
        r = requests.post(otp_url, data=otp_params, headers=headers, timeout=10)
        otp = r.text.strip()
        
        if not otp or len(otp) > 100:
            return None, f"OTP 실패: {otp[:50]}", None
        
        # 데이터 다운로드
        dl_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
        r2 = requests.post(dl_url, data={"code": otp}, headers=headers, timeout=15)
        
        # CSV 파싱
        import io
        content = r2.content.decode('euc-kr', errors='replace')
        df = pd.read_csv(io.StringIO(content))
        
        if df.empty:
            return None, "빈 데이터", None
        
        # 등락 컬럼 찾기
        col_candidates = [c for c in df.columns if '등락' in c or '대비' in c or '증감' in c]
        
        # 대비 컬럼으로 상승/하락 계산
        change_col = None
        for col in df.columns:
            if '대비' in col:
                change_col = col
                break
        
        if change_col is None:
            # 숫자형 컬럼 중 변동률
            for col in df.columns:
                if '등락률' in col or '등락' in col:
                    change_col = col
                    break
        
        if change_col:
            df[change_col] = pd.to_numeric(df[change_col].astype(str).str.replace(',', ''), errors='coerce')
            up = int((df[change_col] > 0).sum())
            down = int((df[change_col] < 0).sum())
        else:
            # 컬럼 추정 실패
            return None, f"컬럼 미발견: {list(df.columns)}", None
        
        total = up + down
        if total == 0:
            return None, "상승+하락=0", None
        raw = up / total
        return raw, up, down
    except Exception as e:
        return None, str(e), None


def fetch_market_breadth(date=None):
    """pykrx로 시장폭 계산"""
    try:
        from pykrx import stock
        # 오늘 날짜로 시도, 실패하면 어제
        for d in [TODAY, YESTERDAY, (datetime.today() - timedelta(days=2)).strftime('%Y%m%d')]:
            try:
                df = stock.get_market_ohlcv_by_ticker(d, market="KOSPI")
                if df is not None and not df.empty:
                    break
            except:
                continue
        
        if df is None or df.empty:
            return fetch_market_breadth_krx(date)
        
        # 등락률 컬럼 확인
        if '등락률' in df.columns:
            up = int((df['등락률'] > 0).sum())
            down = int((df['등락률'] < 0).sum())
        elif '대비' in df.columns:
            up = int((df['대비'] > 0).sum())
            down = int((df['대비'] < 0).sum())
        else:
            return fetch_market_breadth_krx(date)
        
        total = up + down
        if total == 0:
            return None, "상승+하락=0", None
        raw = up / total
        return raw, up, down
    except Exception as e:
        return fetch_market_breadth_krx(date)


# ─────────────────────────────────────────────
# 4. 풋/콜 비율: KOSPI200 옵션 P/C
# ─────────────────────────────────────────────
def fetch_put_call_ratio(date=None):
    """KRX OTP 방식으로 KOSPI200 옵션 P/C 비율"""
    try:
        target_date = datetime.today()
        if target_date.weekday() >= 5:
            target_date -= timedelta(days=target_date.weekday() - 4)
        date_str = target_date.strftime('%Y%m%d')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'http://data.krx.co.kr/'
        }
        
        # 옵션 거래량 OTP
        otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
        # KOSPI200 옵션 거래량 조회
        otp_params = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT12601",
            "name": "fileDown",
            "filetype": "csv",
            "trdDd": date_str,
            "mktTpCd": "O",
            "idxIndMktClss": "02",
            "csvxls_isNo": "false"
        }
        
        r = requests.post(otp_url, data=otp_params, headers=headers, timeout=10)
        otp = r.text.strip()
        
        if not otp or len(otp) > 100:
            # 다른 방식 시도
            otp_params2 = {
                "bld": "dbms/MDC/STAT/standard/MDCSTAT12001",
                "name": "fileDown",
                "filetype": "csv",
                "trdDd": date_str,
                "csvxls_isNo": "false"
            }
            r = requests.post(otp_url, data=otp_params2, headers=headers, timeout=10)
            otp = r.text.strip()
            if not otp or len(otp) > 100:
                return None, f"OTP 실패", None
        
        dl_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
        r2 = requests.post(dl_url, data={"code": otp}, headers=headers, timeout=15)
        
        import io
        content = r2.content.decode('euc-kr', errors='replace')
        df = pd.read_csv(io.StringIO(content))
        
        if df.empty:
            return None, "빈 데이터", None
        
        # 풋/콜 컬럼 찾기
        call_vol = put_vol = 0
        for col in df.columns:
            if '콜' in col and '거래량' in col:
                call_vol = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').sum()
            if '풋' in col and '거래량' in col:
                put_vol = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').sum()
        
        if call_vol == 0:
            return None, f"콜거래량 0, 컬럼: {list(df.columns)[:5]}", None
        
        raw = put_vol / call_vol
        return raw, put_vol, call_vol
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 5. 변동성: VKOSPI vs 50일 이평
# ─────────────────────────────────────────────
def fetch_volatility(date=None):
    """VKOSPI 현재 vs 50일 이평 괴리율"""
    try:
        from pykrx import stock
        end = TODAY
        start = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
        
        # VKOSPI 지수 코드: 1004
        df = stock.get_index_ohlcv_by_date(start, end, "1004")
        
        if df is None or df.empty or len(df) < 10:
            return None, "VKOSPI 데이터 없음", None
        
        close_col = '종가' if '종가' in df.columns else df.columns[3]
        close = df[close_col].astype(float)
        
        current = float(close.iloc[-1])
        ma50 = float(close.iloc[-min(50, len(close)):].mean())
        raw = (current - ma50) / ma50  # 비율
        return raw, current, ma50
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 6. 안전자산 수요: 코스피 vs 국채 ETF
# ─────────────────────────────────────────────
def fetch_safe_haven(date=None):
    """코스피 60일 수익률 - 국채ETF 60일 수익률"""
    try:
        import yfinance as yf
        
        ks11 = yf.download("^KS11", period="90d", progress=False, auto_adjust=True)
        bond = yf.download("114820.KS", period="90d", progress=False, auto_adjust=True)
        
        if ks11.empty or bond.empty:
            return None, "데이터 없음", None
        
        ks_close = ks11['Close'].squeeze()
        bond_close = bond['Close'].squeeze()
        
        # 60일 수익률
        ks_ret = float((ks_close.iloc[-1] / ks_close.iloc[-min(60, len(ks_close))]) - 1) * 100
        bond_ret = float((bond_close.iloc[-1] / bond_close.iloc[-min(60, len(bond_close))]) - 1) * 100
        
        # 차이: 코스피 수익률이 높을수록 위험자산 선호 (탐욕)
        raw = ks_ret - bond_ret
        return raw, ks_ret, bond_ret
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 7. 정크본드: 회사채 AA- vs BBB- 스프레드
# ─────────────────────────────────────────────
def fetch_junk_bond(date=None):
    """한국은행 ECOS API로 회사채 스프레드 (BBB- - AA-)"""
    try:
        end_date = datetime.today().strftime('%Y%m%d')
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')
        
        api_key = "sample"
        base_url = "https://ecos.bok.or.kr/api/StatisticSearch"
        
        def get_rate(item_code):
            url = f"{base_url}/{api_key}/json/kr/1/10/721Y001/D/{start_date}/{end_date}/{item_code}"
            r = requests.get(url, timeout=10)
            data = r.json()
            if 'StatisticSearch' not in data:
                return None
            rows = data['StatisticSearch'].get('row', [])
            if not rows:
                return None
            # 최신 값
            latest = rows[-1]
            return float(latest.get('DATA_VALUE', 0))
        
        aa_minus = get_rate("5030000")  # AA-
        bbb_minus = get_rate("5040000")  # BBB-
        
        if aa_minus is None or bbb_minus is None:
            return None, f"AA-={aa_minus}, BBB-={bbb_minus}", None
        
        # 스프레드: BBB- - AA- (클수록 공포)
        raw = bbb_minus - aa_minus
        return raw, bbb_minus, aa_minus
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 8. 외국인 수급: 5일 순매수 누적
# ─────────────────────────────────────────────
def fetch_foreign_flow(date=None):
    """외국인 5일 순매수 누적 (억원)"""
    try:
        from pykrx import stock
        end = TODAY
        start = (datetime.today() - timedelta(days=14)).strftime('%Y%m%d')
        
        df = stock.get_market_trading_value_by_investor(start, end, "KOSPI")
        
        if df is None or df.empty:
            return None, "데이터 없음", None
        
        # 외국인 컬럼 찾기
        foreign_col = None
        for col in df.columns:
            if '외국인' in str(col) or '외인' in str(col):
                foreign_col = col
                break
        
        if foreign_col is None:
            # 다중 인덱스일 수 있음
            if hasattr(df.columns, 'levels'):
                # MultiIndex
                foreign_col = [c for c in df.columns if '외국인' in str(c)]
                if foreign_col:
                    foreign_col = foreign_col[0]
        
        if foreign_col is None:
            return None, f"외국인 컬럼 없음: {list(df.columns)}", None
        
        # 최근 5일
        recent5 = df[foreign_col].iloc[-5:]
        raw = float(recent5.sum()) / 1e8  # 억원
        return raw, float(recent5.sum()), list(recent5.values)
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 9. 신용잔고: 금투협 크롤링
# ─────────────────────────────────────────────
def fetch_credit_balance(date=None):
    """금투협 신용거래 융자 잔고"""
    try:
        url = "http://freesis.kofia.or.kr/stats/M10050060000.do"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://freesis.kofia.or.kr/stats/M10050060000.do'
        }
        
        today_str = datetime.today().strftime('%Y%m%d')
        month_ago = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')
        
        data = {
            'strtDd': month_ago,
            'endDd': today_str,
            'isuTpcd': '1',  # KOSPI
        }
        
        r = requests.post(url, data=data, headers=headers, timeout=10)
        r.raise_for_status()
        
        # JSON 응답 시도
        try:
            result = r.json()
            if result:
                # 데이터 구조 파악
                return None, f"JSON응답: {str(result)[:200]}", None
        except:
            pass
        
        # HTML/텍스트 응답
        content = r.text
        if '융자' in content or 'content' in content.lower():
            # 숫자 추출 시도
            import re
            numbers = re.findall(r'[\d,]+(?:\.\d+)?', content)
            if numbers:
                # 큰 숫자 찾기 (융자 잔고는 조 단위)
                big_nums = [float(n.replace(',', '')) for n in numbers if len(n.replace(',', '')) >= 8]
                if big_nums:
                    raw = big_nums[0] / 1e12  # 조원
                    return raw, big_nums[0], None
        
        return None, f"파싱 실패 (status={r.status_code}, len={len(r.text)})", None
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 10. 고객예탁금: 금투협 크롤링
# ─────────────────────────────────────────────
def fetch_customer_deposit(date=None):
    """금투협 투자자 예탁금"""
    try:
        url = "http://freesis.kofia.or.kr/stats/M10050040000.do"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://freesis.kofia.or.kr/stats/M10050040000.do'
        }
        
        today_str = datetime.today().strftime('%Y%m%d')
        month_ago = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')
        
        data = {
            'strtDd': month_ago,
            'endDd': today_str,
        }
        
        r = requests.post(url, data=data, headers=headers, timeout=10)
        r.raise_for_status()
        
        try:
            result = r.json()
            if result:
                return None, f"JSON응답: {str(result)[:200]}", None
        except:
            pass
        
        content = r.text
        import re
        numbers = re.findall(r'[\d,]+(?:\.\d+)?', content)
        if numbers:
            big_nums = [float(n.replace(',', '')) for n in numbers if len(n.replace(',', '')) >= 8]
            if big_nums:
                raw = big_nums[0] / 1e12
                return raw, big_nums[0], None
        
        return None, f"파싱 실패 (status={r.status_code})", None
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 11. 코스닥/코스피 상대강도
# ─────────────────────────────────────────────
def fetch_kosdaq_kospi_ratio(date=None):
    """코스닥/코스피 60일 상대강도"""
    try:
        import yfinance as yf
        
        kq = yf.download("^KQ11", period="90d", progress=False, auto_adjust=True)
        ks = yf.download("^KS11", period="90d", progress=False, auto_adjust=True)
        
        if kq.empty or ks.empty:
            return None, "데이터 없음", None
        
        kq_close = kq['Close'].squeeze()
        ks_close = ks['Close'].squeeze()
        
        # 현재 비율
        current_ratio = float(kq_close.iloc[-1]) / float(ks_close.iloc[-1])
        # 60일 전 비율
        n = min(60, len(kq_close), len(ks_close))
        prev_ratio = float(kq_close.iloc[-n]) / float(ks_close.iloc[-n])
        
        # 상대강도 변화 (코스닥이 코스피보다 강할수록 탐욕)
        raw = (current_ratio - prev_ratio) / prev_ratio * 100
        return raw, current_ratio, prev_ratio
    except Exception as e:
        return None, str(e), None


# ─────────────────────────────────────────────
# 실행 & 결과 출력
# ─────────────────────────────────────────────
def run_tests():
    tests = [
        ("1. 모멘텀 (코스피 vs 50일 이평)", fetch_momentum),
        ("2. 주가강도 (52주 신고/신저)", fetch_price_strength),
        ("3. 시장폭 (상승/하락 비율)", fetch_market_breadth),
        ("4. 풋/콜 비율", fetch_put_call_ratio),
        ("5. 변동성 (VKOSPI vs 50일)", fetch_volatility),
        ("6. 안전자산 수요 (코스피 vs 국채)", fetch_safe_haven),
        ("7. 정크본드 (AA- vs BBB- 스프레드)", fetch_junk_bond),
        ("8. 외국인 수급 (5일 순매수)", fetch_foreign_flow),
        ("9. 신용잔고", fetch_credit_balance),
        ("10. 고객예탁금", fetch_customer_deposit),
        ("11. 코스닥/코스피 상대강도", fetch_kosdaq_kospi_ratio),
    ]
    
    results = {}
    print(f"\n{'='*60}")
    print(f"한국 시장 심리지수 v7 - 데이터 소스 테스트")
    print(f"테스트 날짜: {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    for name, func in tests:
        try:
            result = func()
            if isinstance(result, tuple):
                raw, detail1, detail2 = result
            else:
                raw = result
                detail1 = detail2 = None
            
            if raw is not None:
                if detail1 is not None and detail2 is not None:
                    print(f"✅ {name}: raw={raw:.4f} | 상세: {detail1} / {detail2}")
                elif detail1 is not None:
                    print(f"✅ {name}: raw={raw:.4f} | 상세: {detail1}")
                else:
                    print(f"✅ {name}: raw={raw:.4f}")
                results[name] = {"status": "OK", "raw": raw}
            else:
                print(f"❌ {name}: 실패 - {detail1}")
                results[name] = {"status": "FAIL", "error": str(detail1)}
        except Exception as e:
            print(f"❌ {name}: 예외 - {e}")
            results[name] = {"status": "FAIL", "error": str(e)}
        
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    ok_count = sum(1 for v in results.values() if v['status'] == 'OK')
    print(f"성공: {ok_count}/{len(tests)}")
    print(f"{'='*60}\n")
    
    # 결과 저장
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    run_tests()
