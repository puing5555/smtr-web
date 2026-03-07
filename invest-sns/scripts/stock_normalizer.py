# stock_normalizer.py - 종목명 정규화 모듈
# V11 파이프라인에서 Claude 추출 후 종목명/티커를 표준화
"""
문제: Claude가 같은 종목을 다른 이름으로 추출
  - "엔비디아 (NVDA)" vs "엔비디아" vs "nvidia"
  - "구글" vs "알파벳" vs "Alphabet"
  - "버크셀" (오타) vs "버크셔해서웨이"

해결: 추출 직후 표준 이름으로 자동 변환
"""

import re
from typing import Optional, Tuple

# ─── 1. 표준 종목명 매핑 (ticker → 표준 한글명) ──────────────────────────
TICKER_TO_STANDARD: dict[str, str] = {
    # 미국 주요 종목
    'NVDA': '엔비디아',
    'AAPL': '애플',
    'MSFT': '마이크로소프트',
    'GOOGL': '구글',
    'GOOG': '구글',
    'META': '메타',
    'AMZN': '아마존',
    'TSLA': '테슬라',
    'TSM': 'TSMC',
    'ASML': 'ASML',
    'AMD': 'AMD',
    'INTC': '인텔',
    'QCOM': '퀄컴',
    'MU': '마이크론',
    'ARM': 'ARM',
    'AVGO': '브로드컴',
    'ORCL': '오라클',
    'NFLX': '넷플릭스',
    'PLTR': '팔란티어',
    'SMCI': '슈퍼마이크로',
    'MSTR': '마이크로스트래티지',
    'COIN': '코인베이스',
    'SQ': '블록',
    'PYPL': '페이팔',
    'JPM': 'JP모건',
    'BAC': '뱅크오브아메리카',
    'GS': '골드만삭스',
    'BRK.A': '버크셔해서웨이',
    'BRK.B': '버크셔해서웨이',
    'LLY': '일라이릴리',
    'NVO': '노보노디스크',
    'GE': 'GE',
    'GEV': 'GE버노바',
    'NEE': '넥스트에라에너지',
    'FSLR': '퍼스트솔라',
    'ENPH': '인페이즈에너지',
    'RKLB': '로켓랩',
    'IONQ': '아이온큐',
    'BABA': '알리바바',
    'BIDU': '바이두',
    'IREN': '아이렌',
    'RIOT': '라이엇플랫폼',
    'MARA': '마라',
    'CLSK': '클린스파크',
    'AFRM': '어펌',
    'GME': '게임스탑',
    'AMC': 'AMC',
    'SOXX': '필라델피아반도체ETF',
    'GLD': '금ETF',
    # 한국 주요 종목
    '005930': '삼성전자',
    '000660': 'SK하이닉스',
    '005380': '현대차',
    '035420': '네이버',
    '035720': '카카오',
    '051910': 'LG화학',
    '006400': '삼성SDI',
    '207940': '삼성바이오로직스',
    '068270': '셀트리온',
    '373220': 'LG에너지솔루션',
    '066570': 'LG전자',
    '009150': '삼성전기',
    '036570': '엔씨소프트',
    '267260': '현대일렉트릭',
    '009830': '한화솔루션',
    '015760': '한국전력',
    '105560': 'KB금융',
    '316140': '우리금융지주',
    '086790': '하나금융지주',
}

# ─── 2. 오타/별칭 → 표준명 매핑 ─────────────────────────────────────────
ALIAS_TO_STANDARD: dict[str, tuple[str, str | None]] = {
    # (표준명, 표준 ticker)
    # 오타
    '버크셀': ('버크셔해서웨이', 'BRK.A'),
    '버크셀해서웨이': ('버크셔해서웨이', 'BRK.A'),
    '버크셔': ('버크셔해서웨이', 'BRK.A'),
    '브랜드': ('브랜즈홀딩스', None),       # 정확한 ticker 불명확
    # 구글/알파벳
    '알파벳': ('구글', 'GOOGL'),
    'Alphabet': ('구글', 'GOOGL'),
    'alphabet': ('구글', 'GOOGL'),
    'google': ('구글', 'GOOGL'),
    'Google': ('구글', 'GOOGL'),
    # 엔비디아 변종
    'nvidia': ('엔비디아', 'NVDA'),
    'NVIDIA': ('엔비디아', 'NVDA'),
    'Nvidia': ('엔비디아', 'NVDA'),
    # TSMC 변종
    '대만반도체': ('TSMC', 'TSM'),
    '대만적체전로제조': ('TSMC', 'TSM'),
    # 현대일렉트릭 티커 오류 (종목명은 맞고 ticker만 잘못된 경우)
    '현대일렉트릭': ('현대일렉트릭', '267260'),
}

# ─── 3. 괄호+영문 제거 패턴 ────────────────────────────────────────────
# "엔비디아 (NVDA)" → "엔비디아"
# "삼성전자 (005930)" → "삼성전자"
_BRACKET_PATTERN = re.compile(r'\s*[\(\[（【]\s*[A-Z0-9\.]+\s*[\)\]）】]\s*$', re.IGNORECASE)


def normalize_stock_name(stock: str, ticker: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """
    종목명과 티커를 표준화한다.

    Returns:
        (normalized_stock, normalized_ticker)
    """
    if not stock:
        return stock, ticker

    original = stock.strip()

    # 1. 괄호 안 영문 티커 제거: "엔비디아 (NVDA)" → "엔비디아"
    cleaned = _BRACKET_PATTERN.sub('', original).strip()

    # 2. 오타/별칭 체크
    if cleaned in ALIAS_TO_STANDARD:
        std_name, std_ticker = ALIAS_TO_STANDARD[cleaned]
        return std_name, std_ticker if std_ticker else ticker

    if original in ALIAS_TO_STANDARD:
        std_name, std_ticker = ALIAS_TO_STANDARD[original]
        return std_name, std_ticker if std_ticker else ticker

    # 3. ticker로 표준명 조회
    effective_ticker = ticker or _extract_ticker_from_brackets(original)
    if effective_ticker and effective_ticker.upper() in TICKER_TO_STANDARD:
        std_name = TICKER_TO_STANDARD[effective_ticker.upper()]
        return std_name, effective_ticker

    # 4. cleaned 이름 반환 (괄호만 제거)
    return cleaned, ticker


def normalize_ticker(ticker: Optional[str]) -> Optional[str]:
    """
    티커 오류 수정.
    예: 298040 → 267260 (현대일렉트릭 잘못된 티커)
    """
    TICKER_FIXES: dict[str, str] = {
        '298040': '267260',  # 현대일렉트릭 잘못된 → 올바른 코드
    }
    if ticker and ticker in TICKER_FIXES:
        return TICKER_FIXES[ticker]
    return ticker


def _extract_ticker_from_brackets(name: str) -> Optional[str]:
    """
    "종목명 (TICKER)" 패턴에서 티커 추출
    """
    m = re.search(r'[\(\[（【]\s*([A-Z0-9\.]{1,10})\s*[\)\]）】]', name, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return None


def normalize_signal(signal: dict) -> dict:
    """
    시그널 딕셔너리에서 stock과 ticker를 정규화한다.
    pipeline에서 Claude 응답 파싱 직후 이 함수를 호출.
    """
    stock = signal.get('stock', '')
    ticker = signal.get('ticker')

    # ticker 오류 수정 먼저
    ticker = normalize_ticker(ticker)

    # 종목명 정규화
    norm_stock, norm_ticker = normalize_stock_name(stock, ticker)

    result = signal.copy()
    result['stock'] = norm_stock
    if norm_ticker:
        result['ticker'] = norm_ticker

    # 변경 로깅
    if norm_stock != stock or norm_ticker != ticker:
        changes = []
        if norm_stock != stock:
            changes.append(f"stock: '{stock}' → '{norm_stock}'")
        if norm_ticker != ticker:
            changes.append(f"ticker: '{ticker}' → '{norm_ticker}'")
        print(f"[NORMALIZE] {', '.join(changes)}")

    return result


# ─── 테스트 ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    test_cases = [
        ('엔비디아 (NVDA)', 'NVDA'),
        ('엔비디아 (nvda)', None),
        ('nvidia', None),
        ('NVIDIA', 'NVDA'),
        ('구글', 'GOOGL'),
        ('알파벳', 'GOOGL'),
        ('버크셀', None),
        ('버크셔해서웨이', 'BRK.A'),
        ('아이렌 (iren)', None),
        ('아이렌', 'IREN'),
        ('현대일렉트릭', '298040'),
        ('삼성전자', '005930'),
        ('테슬라', 'TSLA'),
    ]

    print("=== stock_normalizer 테스트 ===")
    for stock, ticker in test_cases:
        norm_stock, norm_ticker = normalize_stock_name(stock, ticker)
        print(f"  '{stock}' (ticker={ticker}) → '{norm_stock}' (ticker={norm_ticker})")
