#!/usr/bin/env python3
"""
8개 시그널 타입으로 유튜브 자막에서 투자 시그널 재추출
Anthropic Claude API 사용
"""
import json
import os
import glob
import time
import anthropic

SIGNAL_TYPES = """
시그널 타입 (반드시 아래 8개 중 하나만 사용):

1. STRONG_BUY - 강력매수
   예시 표현:
   - "지금 당장 사야 한다", "올인해야 한다"
   - "뭐하고 있어요 빨리 담으세요"
   - "이 가격이면 무조건이다"
   - "안 사면 바보다", "안 사는 게 손해"
   - "전재산 넣어도 된다", "몰빵해도 된다"
   - "역대급 기회다", "이런 기회 다시 안 온다"
   - "지금이 마지막 탑승 기회다"
   - "미친 거 아니냐 이 가격에 안 사면", "눈 감고 사라", "풀매수 갑니다"
   - "이건 못 참지", "지금이 마지막 기회", "후회할 걸요"
   - "레버리지 가도 된다", "영끌해도 된다", "대출받아서라도"
   - "10배 간다", "100배 코인이다"
   - "역대급 기회", "평생 한 번 올까 말까"
   - "이건 그냥 줍줍 구간이다", "말도 안 되는 가격이다"
   - "세력 평단 근처다", "이 가격 다시는 안 온다"
   - "지금 안 사면 나중에 울어요", "여기서 안 들어가면 바보다"
   - "인생 역전 자리", "이거 잡으면 게임 끝"
   - "저는 올인했습니다", "비트 몰빵"
   - "리스크보다 리턴이 훨씬 크다", "리스크 거의 없다"
   - "확률 게임인데 이건 8:2다"

2. BUY - 매수
   예시 표현:
   - "사는 게 좋다", "매수 추천", "들어가도 된다"
   - "계속 올라갈 겁니다"
   - "저는 투자했습니다", "저도 샀습니다"
   - "괜찮은 종목이다", "나쁘지 않다"
   - "분할매수 추천", "조금씩 모아가세요"
   - "관심 가져볼 만하다", "눈여겨보세요"
   - "비중을 늘렸다", "추가 매수했다"
   - "괜찮은 자리다", "여기서 모아가세요"
   - "충분히 매력적이다", "안 살 이유가 없다"
   - "펀더멘탈 좋다", "목표가 상향", "상승 여력 충분하다"
   - "여기서는 접근 가능하다", "저는 담고 있습니다"
   - "리스크 관리 하에 매수", "손절 짧게 보고 들어간다"
   - "이 구간은 리워드가 괜찮다", "리스크 대비 괜찮은 자리"
   - "기술적으로 매수 신호"
   - "눌림목이다"
   - "리스크 감수할 만하다"

3. POSITIVE - 긍정 (직접적 매수 추천 없이 긍정적 전망)
   예시 표현:
   - "전망이 좋다", "성장 가능성 있다"
   - "저점이다", "아직 기회가 있다"
   - "차트가 좋아지고 있다", "흐름이 바뀌고 있다"
   - "실적이 잘 나오고 있다", "펀더멘탈이 탄탄하다"
   - "기관들이 들어오고 있다", "큰손들이 매집 중이다"
   - "기술력이 뛰어나다", "미래가 밝다"
   - "시장에서 주목받고 있다"
   - "바닥 다진 것 같다", "반등 나올 수 있다"
   - "호재가 많다", "재료가 있다"
   - "고래 지갑이 움직인다", "온체인 데이터가 좋다", "TVL 올라가고 있다"
   - "분위기 좋아지고 있다"
   - "시장 분위기 달라졌다", "수급 들어오는 느낌"
   - "외국인 매수 전환", "이상하게 안 빠진다"
   - "이 자리에서 버틴다", "생각보다 강하다"
   - "매물 소화 중", "조정이 건강하다", "저가 매수세 들어온다"
   - "추세 전환 시도 중"
   - "이번 사이클 대장이다", "구조적으로 오른다"
   - "트렌드다 거스를 수 없다", "기관 평단이다", "세력이 매집 중이다"
   - "하방 제한적", "저점 신호 일부 나왔다"

4. HOLD - 보유
   예시 표현:
   - "지금은 들고 있어라", "팔지 마라"
   - "견뎌라", "버텨라", "기다려라"
   - "지금은 기다릴 때다", "아직 때가 아니다"
   - "흔들리지 마라", "패닉셀 하지 마라"
   - "장기적으로 보고 가야 한다"
   - "출렁임에 동요하지 마라"
   - "손절할 자리가 아니다"
   - "여기서 파는 건 바보다", "시간이 필요하다", "장기로 봐라"
   - "멘탈 잡아라", "존버가 답이다"
   - "개미털기다", "아직 시나리오 유효하다", "추세 안 깨졌다"
   - "이건 기다리는 자리", "손절 칠 자리는 아니다"
   - "버티면 보상 온다", "사이클상 아직 끝 아님"
   - "물린 사람은 굳이 팔 필요 없다", "시간이 해결해준다"
   - "저는 홀딩", "평단 관리만 잘하면 된다"

5. NEUTRAL - 중립 (의미있는 분석이지만 방향성 없음)
   예시 표현:
   - "이런 상황입니다" (의견 없이 현황 분석)
   - "양쪽 다 가능성이 있다"
   - "지켜봐야 한다", "아직 판단하기 이르다"
   - "변수가 많다", "상황을 봐야 한다"
   - "지켜보겠습니다", "모니터링 중입니다"
   - "어디로 갈지 모르겠다", "데이터를 더 봐야 한다"
   - "이런 뉴스가 나왔는데요", "팩트만 전달합니다"
   - 단, 단순 뉴스 읽기/정보 나열은 NEUTRAL도 아니며 시그널 자체가 아님

6. CONCERN - 우려 (직접적 매도 추천 없이 부정적 전망)
   예시 표현:
   - "주의해야 한다", "리스크가 있다"
   - "한 방에 들어가지 마라", "분할해서 해라"
   - "어려울 것 같다", "쉽지 않을 거다"
   - "과열됐다", "거품이 있다"
   - "조심해야 할 구간이다"
   - "변동성이 클 수 있다", "하락 가능성 있다"
   - "무리하지 마세요"
   - "좀 불안하다", "과열 아닌가"
   - "물량이 많다", "매도 압력 세다"
   - "펀딩비 너무 높다", "롱 청산 주의"
   - "여기서 추매는 위험하다", "물타기 하지 마라"
   - "욕심부리지 마라"
   - "슬슬 과열 같다", "거래량 너무 붙었다"
   - "여기서 추격은 위험", "FOMO 구간이다"
   - "위꼬리 많이 달린다"
   - "여기서 매수는 모험", "리스크 커졌다"
   - "조정 깊게 나올 수도", "시장 과신 중"
   - "리스크 관리 하자"

7. SELL - 매도
   예시 표현:
   - "팔아라", "빠져라", "손절해라"
   - "끝났다고 생각한다"
   - "탈출하라", "정리하라"
   - "저는 매도했습니다", "저는 빠졌습니다"
   - "언스테이킹/매도 신청했다" (본인이 빠지는 행동)
   - "비중을 줄였다", "정리 들어갔다"
   - "더 이상 가치가 없다"
   - "정리하세요", "비중 줄이세요", "차익실현 하세요"
   - "빠지기 전에 나와라", "탈출해라"
   - "저는 다 팔았습니다", "포지션 정리했어요"
   - "더 이상 안 본다", "관심 종목에서 뺐다"
   - "하락 추세 진입했다", "지지선 깨졌다"
   - "여기서는 빼야 한다"
   - "익절 타이밍", "비중 줄이는 게 맞다"
   - "이제 매도 전략", "추세 꺾였다"
   - "손절가 터졌다", "기술적 반등 끝"
   - "차익 실현 구간", "익절도 매매다"

8. STRONG_SELL - 강력매도
   예시 표현:
   - "당장 던져라", "절대 들고 있으면 안 된다"
   - "사라질 것이다", "멸종할 것이다"
   - "사기다", "스캠이다", "민코인이다"
   - "절대 사지 마라", "손대지 마라"
   - "이건 망한다", "회복 불가능하다"
   - "전량 매도해라", "지금 안 팔면 0원 된다"
   - "대폭락이 온다", "대멸종이다"
   - "도망쳐라", "지금이라도 팔아라"
   - "제로 간다", "상폐될 수 있다"
   - "먹튀다", "러그풀이다", "폰지다"
   - "근처에도 가지 마라", "돈 버리는 거다", "쓰레기다"
   - "팀이 도망갔다", "개발 중단됐다"
   - "여기 남아 있으면 위험하다", "지금 안 팔면 늦는다"
   - "구조적으로 망가졌다", "상폐 리스크"
   - "팀 신뢰 무너졌다", "이건 끝났다"
   - "여기서 버티는 건 도박", "시장 떠나라"

경계가 애매한 표현 판단 가이드:

[BUY vs POSITIVE 구분]
- "이 종목 좋아요, 사세요" → BUY (직접 매수 권유)
- "이 종목 좋아요, 전망 밝아요" → POSITIVE (의견은 있지만 매수 권유 없음)
- "저는 샀습니다" → BUY (본인 행동 = 간접 추천)
- "좋은 기업인 건 맞다" → POSITIVE

[SELL vs CONCERN 구분]
- "조심해야 한다" → CONCERN (경고만)
- "저는 팔았습니다" → SELL (본인 행동 = 간접 매도 권유)
- "위험하니까 빠져라" → SELL (직접 매도 권유)
- "위험할 수 있다" → CONCERN (가능성만 언급)

[STRONG_BUY vs BUY 구분]
- "사도 될 것 같아요" → BUY (일반적 추천)
- "지금 안 사면 후회합니다" → STRONG_BUY (긴급성/강한 확신)
- "올인했습니다" → STRONG_BUY (극단적 행동)
- "조금씩 모아가세요" → BUY (점진적 매수)

[STRONG_SELL vs SELL 구분]
- "정리하는 게 좋겠다" → SELL (일반 매도 권유)
- "당장 던져라, 0원 된다" → STRONG_SELL (긴급성/극단적 하락 전망)
- "망할 겁니다" → STRONG_SELL
- "전망이 안 좋아서 빠졌다" → SELL

[HOLD vs NEUTRAL 구분]
- "팔지 마라, 기다려라" → HOLD (보유 지시)
- "지켜봐야 한다" → NEUTRAL (판단 유보)
- "흔들리지 마라" → HOLD (기존 포지션 유지 지시)
- "아직 모르겠다" → NEUTRAL

[시그널 아닌 것들 — 추출하지 마세요]
- "어제 주가가 5% 올랐습니다" → 사실 전달, 시그널 아님
- "실적이 발표됐습니다" → 뉴스 전달, 시그널 아님  
- "투자하신 분들 축하드립니다" → 축하, 시그널 아님
- "시장이 이렇게 돌아가고 있습니다" → 현황 설명, 시그널 아님
- 다른 종목을 설명하기 위해 비교용으로 언급한 종목 → 시그널 아님

주의사항:
- PRICE_TARGET(가격 목표)은 시그널 타입이 아닙니다. 가격 목표가 언급되면 맥락에 따라 위 8개 중 적절한 것을 선택하세요.
- MARKET_VIEW(시장 전망)도 시그널 타입이 아닙니다. 위 8개 중 선택하세요.
- 단순히 가격이나 수치를 언급하는 것만으로는 시그널이 아닙니다. 화자의 의견/추천이 있어야 합니다.
"""

ASSET_NAME_RULES = """
종목명 작성 규칙 (매우 중요):

1. 종목명은 반드시 한글을 원칙으로 합니다:
   - Bitcoin, BTC → 비트코인
   - Ethereum, ETH → 이더리움
   - Altcoins, Altcoins (General) → 알트코인
   - Solana, SOL → 솔라나
   - Chainlink, LINK → 체인링크
   - Gold → 금
   - Samsung Electronics → 삼성전자
   - Monero → 모네로
   - Stablecoin → 스테이블코인

2. 영문 티커가 공식 명칭인 경우는 영문 유지:
   - XRP → XRP
   - BNB → BNB
   - NVIDIA → 엔비디아 (NVDA)
   - PALANTIR → 팔란티어 (PLTR)
   - MicroStrategy → 마이크로스트래티지 (MSTR)

3. 유사 단어는 반드시 하나로 통일:
   - 켄턴/켄톤/Canton/CANTON/KANTON/Kantone/Canto/Cantonnetwork/Canton Network → 캔톤네트워크 (CC)
   - CC코인/CC Coin/CC/XCC/Canton Coin → 캔톤네트워크 (CC)
   - BITMINE/BITMAIN/BMNR/BTMN/BTMM/MBNR → 비트마인 (BMNR)
   - bitcoin/비트커인/비트쿠인/BTC → 비트코인
   - WLFI/월드 리버티 파이낸셜 → 월드리버티파이낸셜 (WLFI)
   - Circle/CIRCLE/서클 → 서클 (Circle)
   - THAR/Tymune/Tymune Technologies → 타르 (THAR)
   - Etherzilla/이더질라/ATNF → 이더질라 (ATNF)
   - MARA/Marathon Digital → 마라톤디지털 (MARA)
   - RIOT → 라이엇 (RIOT)

4. "시장 전체" 같은 포괄적 대상은 종목이 아닙니다:
   - Crypto Market, Cryptocurrency, Cryptocurrency Market, Cryptocurrency Trading, Cryptocurrency Futures → 시그널로 추출하지 마세요
   - US Stocks → 시그널로 추출하지 마세요
   - 코스피 → 시그널로 추출하지 마세요
   - 구체적 종목이 언급되지 않은 시장 전반 의견은 제외

5. 티커가 있는 종목은 "한글명 (티커)" 형식으로 작성:
   - 엔비디아 (NVDA)
   - 비트마인 (BMNR)
   - 캔톤네트워크 (CC)
   - 단, 비트코인/이더리움/XRP처럼 널리 알려진 건 티커 생략 가능

6. "시장 전체" 같은 포괄적 대상은 종목이 아닙니다:
   - Crypto Market, Cryptocurrency, US Stocks, 코스피 등은 시그널로 추출하지 마세요
   - 구체적 종목이 언급되지 않은 시장 전반 의견은 제외
"""

CONTEXT_RULES = """
맥락 판단 규칙 (매우 중요):

1. 비교/빗대기용 종목은 시그널이 아닙니다:
   - 화자가 종목A를 설명하기 위해 종목B,C의 실적/성과를 비교 대상으로 언급한 경우,
     비교 대상(B,C)은 시그널로 추출하지 마세요.
   - 예: "팔란티어 실적이 좋죠, 삼성전자도 축하드리고, SK하이닉스도 대단하죠. 
     근데 코인 중에서 이런 실적을 보여주는 건 캔톤밖에 없어요"
     → 팔란티어/삼성전자/SK하이닉스는 빗대기용 → 시그널 아님
     → 캔톤만 시그널 (BUY 또는 POSITIVE)

2. 단순 사실 전달은 시그널이 아닙니다 (엄격 기준):
   - "팔란티어 매출이 70% 증가했습니다" → 사실 전달일 뿐 → ❌ 시그널 아님
   - "팔란티어 매출 70% 증가, 지금 안 사면 후회합니다" → 의견 포함 → BUY ✅
   - 화자가 해당 종목에 대해 "사라/팔아라/좋다/위험하다/전망이 밝다/조심해야 한다" 등 직접적 의견을 밝혀야 시그널
   - 단순 수치/팩트 나열은 아무리 긍정적이어도 시그널로 추출하지 마세요

3. 축하/감탄 vs 추천 구분:
   - "삼성전자 투자하신 분들 축하드립니다" → 축하일 뿐, 매수 추천 아님
   - "삼성전자 지금이라도 사세요" → BUY 시그널

4. 화자의 주요 논점(main point)에 해당하는 종목만 추출:
   - 영상의 핵심 주제 종목 = 시그널 추출 대상
   - 곁다리로 스쳐 지나가는 종목 = 제외
"""

CORE_PRINCIPLES = """
핵심 원칙 (모든 판단의 기준):
1. 의견이 없으면 시그널도 없다 — 억지 추출 금지
2. 맥락이 왕이다 — 단어 매칭이 아니라 문맥으로 판단
3. 확신 없으면 보수적으로 — 애매하면 한 단계 낮춰 처리
4. 풍자/반어는 반대로 — 톤과 전후 맥락 필수 확인
5. 화자 본인 의견만 — 타인 인용, 뉴스 전달 제외
"""

SARCASM_RULES = """
반어법/풍자 감지 규칙:
- "네네 사세요 사세요~", "다 사세요 뭐~" 등 비꼬는 톤 + 앞뒤에 부정적 맥락 → 실제 의미 반대로 판단
- "대단하시네요 진짜" + 부정적 맥락 → 풍자로 처리
- 판단 기준: 해당 발언 전후 2~3문장의 맥락을 반드시 확인
- 확신이 없으면 NEUTRAL 처리하고 context에 "풍자 가능성" 명시
"""

COMPOSITE_SIGNAL_RULES = """
복합 시그널 처리 규칙:
- 같은 종목에 대해 방향이 같으면 → 가장 강한 시그널 1개
- 같은 종목에 대해 방향이 다르면 → 둘 다 출력
  예: "장기적으론 BUY인데 단기적으론 빠질 수 있다" 
  → BUY (timeframe: LONG) + CONCERN (timeframe: SHORT) 둘 다 출력
- 자산이 다르면 당연히 별도 출력
  예: "비트는 사고 알트는 팔아라" → 각각 출력
"""

INTENSITY_RULES = """
시그널 강도 보정 규칙:
- 같은 방향 발언이 3회 이상 반복 → confidence 한 단계 상향
- "근데", "다만", "물론 ~이긴 하지만" 뒤에 나온 시그널 → hedged: true
- "~일 수도 있다", "~같긴 한데" → confidence 한 단계 하향
- "확실하다", "장담한다", "틀리면 은퇴한다" → confidence: HIGH 확정
"""

EXTRA_EXTRACTION_RULES = """
추가 추출 규칙:
- 광고/협찬 표시된 종목: 시그널 추출하되 context에 "스폰서 콘텐츠" 명시
- 과거 시제 발언 구분: "그때 샀어야 했다" → 현재 시그널 아님, 제외
- 가정법 구분: "만약 내가 지금 돈이 있었다면 샀을 거다" → conditional: true
- 타인 의견 인용: "워렌 버핏이 사라고 했다" → 화자 본인 의견 아니면 제외 (단, 화자가 동의를 표하면 시그널로 처리)
- 썸네일/제목 vs 본문 괴리: 자막 내용 기준으로만 판단 (제목 무시)
"""

NEUTRAL_RULES = """
NEUTRAL 판단 강화:
- 의견 없이 양쪽 시나리오 병렬 나열 → NEUTRAL
- "올라갈 수도 내려갈 수도" → NEUTRAL
- 교육/설명 목적 콘텐츠 (차트 읽는 법, 용어 설명) → 시그널 없음으로 처리
- 시그널 0개인 영상도 있을 수 있음 → 억지로 추출하지 말 것
"""

SYSTEM_PROMPT = f"""당신은 유튜브 투자 채널의 자막을 분석하여 투자 시그널을 추출하는 전문가입니다.

★ 분석 순서 (가장 중요 — 반드시 이 순서대로):
1. 먼저 영상 전체 내용을 요약하세요 (주요 주제, 화자의 전체적인 시각, 핵심 논점)
2. 요약을 바탕으로 각 발언의 문맥을 이해한 뒤 시그널을 추출하세요
3. 이렇게 하면 풍자/역설/맥락 의존적 발언을 더 정확하게 판단할 수 있습니다

{CORE_PRINCIPLES}

{SIGNAL_TYPES}

{ASSET_NAME_RULES}

{CONTEXT_RULES}

{SARCASM_RULES}

{COMPOSITE_SIGNAL_RULES}

{INTENSITY_RULES}

{EXTRA_EXTRACTION_RULES}

{NEUTRAL_RULES}

다음 JSON 형식으로 출력하세요:
{{
  "video_summary": "영상 전체 내용 요약 (한국어, 2-4문장)",
  "signals": [
    {{
      "asset": "종목명 (한글명 (티커) 형식)",
      "signal_type": "위 8개 타입 중 하나 (대문자)",
      "content": "화자의 핵심 발언 (원문 인용, 한국어)",
      "confidence": "HIGH/MEDIUM/LOW",
      "timeframe": "SHORT/MID/LONG (단기: 1주 이내, 중기: 1주~3개월, 장기: 3개월+)",
      "conditional": false,
      "skin_in_game": false,
      "hedged": false,
      "context": "발언의 맥락 설명 (한국어)",
      "timestamp": "자막의 타임스탬프 [M:SS] 형식"
    }}
  ]
}}

필드 설명:
- timeframe: SHORT(단기 트레이딩, 1주 이내), MID(중기 스윙, 1주~3개월), LONG(장기 투자, 3개월+)
- conditional: 조건부 시그널인 경우 true ("떨어지면 사라", "만약 ~하면")
- skin_in_game: 화자가 본인도 해당 포지션을 갖고 있는 경우 true ("저도 샀습니다", "저는 홀딩 중")
- hedged: 시그널을 말하면서 동시에 리스크/반대 가능성을 언급한 경우 true ("사세요, 근데 리스크는 있어요")

규칙:
1. 화자가 특정 종목/코인/자산에 대해 명확한 의견을 표현한 경우만 추출
2. 단순 정보 전달이나 뉴스 읽기는 제외 (NEUTRAL은 의미있는 분석이 있을 때만)
3. 가격 목표 언급 시 매수/매도 맥락에 따라 적절한 시그널 타입 부여
4. 같은 종목 + 같은 방향 → 가장 강한 시그널 1개만. 같은 종목 + 다른 방향 → 둘 다 출력
5. 시그널이 없으면 빈 배열 반환: {{"signals": []}}
6. 반드시 valid JSON만 출력하세요. 다른 텍스트 없이 JSON만.

타임스탬프 규칙 (매우 중요):
- timestamp는 반드시 해당 발언이 실제로 시작되는 자막 라인의 타임스탬프를 사용하세요
- content에 인용한 문장이 등장하는 자막 라인의 [M:SS] 값을 정확히 기입하세요
- [0:00]~[0:10] 범위는 보통 인트로이므로, 실제 발언 위치가 맞는지 재확인하세요
- 자막에서 해당 문장을 찾아 그 줄의 타임스탬프를 그대로 쓰세요"""


def extract_signals_from_subtitle(client, video_id, subtitle, title, channel):
    """단일 자막에서 시그널 추출"""
    user_msg = f"유튜버: {channel}\n영상 제목: {title}\n영상 ID: {video_id}\n\n=== 자막 ===\n{subtitle}"
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}]
    )
    
    text = response.content[0].text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    
    return json.loads(text)


def main():
    subtitle_dir = os.path.dirname(os.path.abspath(__file__))
    client = anthropic.Anthropic()
    
    # Load video metadata
    videos_meta = {}
    videos_path = os.path.join(subtitle_dir, "_all_videos.json")
    if os.path.exists(videos_path):
        with open(videos_path, 'r', encoding='utf-8') as f:
            for v in json.load(f):
                vid = v.get('video_id') or v.get('id', '')
                videos_meta[vid] = v
    
    # Get subtitle files
    txt_files = sorted(glob.glob(os.path.join(subtitle_dir, "*.txt")))
    txt_files = [f for f in txt_files if not os.path.basename(f).startswith('_')]
    
    # Load progress if exists
    progress_path = os.path.join(subtitle_dir, "_extract_8types_progress.json")
    all_signals = []
    done_ids = set()
    if os.path.exists(progress_path):
        with open(progress_path, 'r', encoding='utf-8') as f:
            progress = json.load(f)
            all_signals = progress.get("signals", [])
            done_ids = set(progress.get("done_ids", []))
        print(f"Resuming: {len(done_ids)} already done, {len(all_signals)} signals so far")
    
    print(f"Processing {len(txt_files)} subtitle files...")
    
    for i, txt_path in enumerate(txt_files):
        video_id = os.path.splitext(os.path.basename(txt_path))[0]
        
        if video_id in done_ids:
            continue
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            subtitle = f.read()
        
        if len(subtitle.strip()) < 50:
            done_ids.add(video_id)
            continue
        
        meta = videos_meta.get(video_id, {})
        title = meta.get('title', video_id)
        channel = meta.get('channel', '코린이 아빠')
        
        try:
            result = extract_signals_from_subtitle(client, video_id, subtitle, title, channel)
            signals = result.get("signals", [])
            for sig in signals:
                sig["video_id"] = video_id
                sig["channel"] = channel
                sig["title"] = title
            all_signals.extend(signals)
            done_ids.add(video_id)
            print(f"  [{len(done_ids)}/{len(txt_files)}] {video_id}: {len(signals)} signals ({title[:40]})")
            
            # Save progress every 5 videos
            if len(done_ids) % 5 == 0:
                with open(progress_path, 'w', encoding='utf-8') as f:
                    json.dump({"signals": all_signals, "done_ids": list(done_ids)}, f, ensure_ascii=False, indent=2)
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ERROR {video_id}: {e}")
            time.sleep(2)
            continue
    
    # Save final results
    output_path = os.path.join(subtitle_dir, "_all_signals_8types.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_signals, f, ensure_ascii=False, indent=2)
    
    # Save progress
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump({"signals": all_signals, "done_ids": list(done_ids)}, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal signals: {len(all_signals)}")
    from collections import Counter
    types = Counter(s.get('signal_type', '?') for s in all_signals)
    print(f"Types: {dict(types)}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
