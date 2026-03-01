[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1"
$KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
$headers = @{
    "apikey" = $KEY
    "Authorization" = "Bearer $KEY"
    "Content-Type" = "application/json; charset=utf-8"
    "Prefer" = "return=representation"
}

# Video ID mapping (youtube_id -> DB UUID)
$videoMap = @{
    "R6w3T3eUVIs" = "2f1794a4-01f6-4ece-a5f7-01882e107aa9"
    "-US4r1E1kOQ" = "9236a7e9-8a4b-4291-b6ef-19cc83991e5e"
    "XFHD_1M3Mxg" = "900806f6-434f-4913-82c7-2b69a80284d0"
    "ldT75QwBB6g" = "bee43acd-68d6-4247-98bd-1c1365c8815d"
    "x0TKvrIdIwI" = "c7bf5e71-50d1-4ffa-94a7-e3bce9ec49a5"
    "irK0YCnox78" = "e9012cde-ddbc-4819-8745-ef93fff6327f"
    "qYAiv0Kljas" = "235ea3ae-5b54-4f6b-9a12-0f57da76d919"
    "I4Tt3tevuTU" = "d210f06a-ff68-458f-8d8c-d34724d63458"
    "8-hYd-8eojE" = "d66104b7-0b88-463e-b2a9-34b6797404da"
    "hxpOT8n_ICw" = "c2952626-8842-4561-b297-468f6733d8f7"
    "awXkJ9hK-a0" = "baadbc77-38fd-46bf-8270-6c780c19cb0e"
    "82TEaq8GIfc" = "4fbee999-8f87-451e-85cc-54f31e17bf26"
    "7AaksU-R3dg" = "1fa51ee5-980e-45e8-bd3f-1f90b501c35d"
    "A7qHwvcGh9A" = "6961f2b0-beea-4845-a094-c7572a7ca792"
    "Vy2jrX-uCbY" = "59a6b272-7eeb-4719-af66-2242066a7e33"
    "TjKVuAGhC1M" = "951857cf-e963-4639-b256-2a8095c3c5fa"
    "PGQW7nyoRRI" = "da2b8045-ad74-49de-8c1e-d1c8e441f11c"
}

# Speaker ID mapping
$speakerMap = @{
    "배재원" = "7fef30a4-a248-44d6-99b9-02bda6f47eb2"
    "고연수" = "3508abce-70e0-4eaa-a0d4-686b61071dd9"
    "김장년" = "03baa455-178d-4a82-bf47-6a12ccc2b694"
    "김동훈" = "5783838f-af5f-4e74-bcbf-bbc20141b199"
    "박지훈" = "e59ed6f5-7a8d-4111-af1c-502ad3344e79"
    "박병창" = "2720d0ee-b7e2-4006-80df-90bc9de07797"
    "김장열" = "8234cd75-1d0d-458c-b01c-62080c7d91e3"
    "박명성" = "5d03d08f-abb4-453b-bf86-40e57a0ddfdb"
    "장우진" = "aa25b0e6-aadf-4bae-a2fa-afc0a067e315"
    "이건희" = "731fe32d-f47a-432f-9899-305915138983"
    "코린이 아빠" = "2e9a8a44-3eb8-4009-8318-5e8d23a62840"
    "달란트투자" = "4c58cef4-0c79-4db1-8b8a-6a8b5ce1be10"
}

$signals = @()
$count = 0

function Add-Signal($vid, $speaker, $stock, $ticker, $market, $signal, $mentionType, $confidence, $ts, $quote, $reasoning) {
    $script:signals += @{
        video_id = $videoMap[$vid]
        speaker_id = $speakerMap[$speaker]
        stock = $stock
        ticker = $ticker
        market = $market
        signal = $signal
        mention_type = $mentionType
        confidence = $confidence
        timestamp = $ts
        key_quote = $quote
        reasoning = $reasoning
        pipeline_version = "V9.1"
        review_status = "pending"
    }
}

# === Video 1: sampro_R6w3T3eUVIs - 배재원 ===
Add-Signal "R6w3T3eUVIs" "배재원" "삼성전자" "005930" "KR" "BUY" "결론" "high" "07:00" "비중이 없는 분은 지금이라도 물리더라도 들어가야 된다" "영업이익 추정치 계속 상향 중, 목표주가 30만원 이상 나오는 상황에서 매수하지 않는 이유가 없다고 강조. 10%라도 들어가라고 권유."
Add-Signal "R6w3T3eUVIs" "배재원" "SK하이닉스" "000660" "KR" "BUY" "결론" "high" "08:46" "하이닉스 30만원일 때도 비싸다고 했는데 지금 시점에서 30만원이면 당연히 사겠죠" "메모리 수요 강세, HBM 비용 상승은 공급 부족 의미. 영업이익 추정치 상향 지속."
Add-Signal "R6w3T3eUVIs" "배재원" "코스피" "" "SECTOR" "BUY" "결론" "high" "06:14" "상반기에 7000포인트 역사적 순간도 볼 수 있지 않을까" "코스피 영업이익 600조대 상향, 리레이팅 가능성. 이익으로 설명되는 수준에서 리레이팅까지 기대."

# === Video 2: sampro_-US4r1E1kOQ - 김장년 ===
Add-Signal "-US4r1E1kOQ" "김장년" "엔비디아" "NVDA" "US" "BUY" "결론" "medium" "04:37" "포지션 없는 분이면 200달러 전으로 들어갈 만한 수준, 30% 정도 넣어놓고" "실적 인라인, 가이던스 5-7% 상회. PER 23배로 월마트보다 싸다. 추론형 AI 인플렉션 포인트 도래."
Add-Signal "-US4r1E1kOQ" "김장년" "삼성전자" "005930" "KR" "STRONG_BUY" "결론" "high" "09:50" "삼성전자 하이닉스 1분기 실적 나오기 전에 애널리스트 전망 한번 더 올라갈 수 있다" "엔비디아 추론형 시장 확대로 디램 가격 상승 불가피. 노무라 240조, 맥쿼리 300조 영업이익 전망. 멀티플 확대 여지."
Add-Signal "-US4r1E1kOQ" "김장년" "SK하이닉스" "000660" "KR" "STRONG_BUY" "결론" "high" "09:50" "엔비디아가 가는 속도보다 메모리가 덜 가지 않을 것 같다" "추론형 AI 확대로 키밸류캐시용 일반 디램 수요 폭발. HBM 말고 디램 가격 상승도 가늠 불가."

# === Video 3: sampro_XFHD_1M3Mxg - 김동훈 ===
Add-Signal "XFHD_1M3Mxg" "김동훈" "신세계" "004170" "KR" "BUY" "결론" "high" "01:00" "신세계 주식을 가장 좋게 보고 있다" "인바운드 외국인 관광객 증가, 원화약세 수혜. 일본 이세탄 사례(4년 7배). PER 12.6배로 과거 고점 16.7배 대비 여력. 외국인 지분 20% 순매수 지속."
Add-Signal "XFHD_1M3Mxg" "김동훈" "삼성전자" "005930" "KR" "BUY" "전망" "medium" "18:02" "엔비디아 지금도 너무 싸지 않나요? PER 20배" "시티은행 목표주가 34만원 상향. 영업이익 상향 소식 지속되는 한 고점으로 보기 어렵다."

# === Video 4: sampro_ldT75QwBB6g - 박지훈 ===
Add-Signal "ldT75QwBB6g" "박지훈" "효성중공업" "298040" "KR" "BUY" "결론" "high" "16:43" "이 세 개의 종목은 올해도 계속 한다. 실체가 있는 거니까" "전력인프라 수주 실체 있는 실적. 시총 대비 매출단이 4분기에 HD현대일렉과 맞닿을 것. 대장주 가능성."
Add-Signal "ldT75QwBB6g" "박지훈" "HD현대일렉트릭" "267260" "KR" "BUY" "결론" "high" "19:03" "HD현대도 팔아야 되는 건 아닙니다. 유럽 수주 모멘텀" "올해 유럽 수주 개시로 새로운 모멘텀. 시총 38조로 전력3사 중 최대."
Add-Signal "ldT75QwBB6g" "박지훈" "LS일렉트릭" "010120" "KR" "HOLD" "전망" "medium" "18:11" "LS일렉이 고밸류인 거예요. 현재 상황을 보면" "시총 23조인데 매출단 효성중공업의 반도 안됨. 상대적 고밸류 지적."
Add-Signal "ldT75QwBB6g" "박지훈" "삼성전기" "009150" "KR" "BUY" "결론" "high" "25:56" "2026년에 대박주를 삼성전기로 선택했습니다" "피지컬AI 핵심, MLCC+휴머노이드 부품. 핸드셋 전환기 원년. 로봇 눈(OLED) 소재단 수혜."
Add-Signal "ldT75QwBB6g" "박지훈" "솔브레인" "357780" "KR" "BUY" "결론" "medium" "28:23" "소부장 소재단은 꼭 하나 정도는 들고 가셨으면" "외국인 펀드매니저 9:1로 소재 관심. 미국 진출, 유리기판, 블랙PDL 모멘텀."
Add-Signal "ldT75QwBB6g" "박지훈" "LG화학" "051910" "KR" "BUY" "결론" "high" "36:28" "LG화학 강력 추천드리는 바입니다" "팰리서 캐피탈 행동주의 펀드 활동. PBR 0.8배, 외국인 35%+. 3월 주총 시즌 모멘텀."
Add-Signal "ldT75QwBB6g" "박지훈" "NC소프트" "036570" "KR" "HOLD" "결론" "medium" "32:31" "NC소프트 바닥에서 야금야금 올라가는 이유 설명. 홀딩하셔도 되겠다" "어닝모멘텀 3년만에 회복, 가이던스 3600억(YoY 2142%). 목표주가 40만원대."
Add-Signal "ldT75QwBB6g" "박지훈" "하이브" "352820" "KR" "HOLD" "결론" "medium" "33:42" "온고잉 고잉 한번 믿어보자. 홀딩 의견 강력하게 말씀드리고 싶고" "BTS 복귀 모멘텀. 차이나 플레이 약화됐으나 어닝 확인시 재점핑 가능."

# === Video 5: sampro_x0TKvrIdIwI - 박병창 ===
Add-Signal "x0TKvrIdIwI" "박병창" "삼성전자" "005930" "KR" "POSITIVE" "전망" "high" "04:04" "3월 19일 벨류업 관련 프로그램 발표가 있을 것이다" "메타+AMD 공급계약 수혜, 넥스트 거래에서 10% 추가 상승. 밸류업 공시 기대감. 다만 포모 현상 경계 필요."
Add-Signal "x0TKvrIdIwI" "박병창" "SK하이닉스" "000660" "KR" "POSITIVE" "전망" "high" "06:31" "SK하이닉스 시총 725조, 올해 영업이익 160조면 멀티플 5배도 안돼" "엔비디아 912억달러 미지급 구매 발표로 SK하이닉스 수혜. 내년 이익 더 늘어 3배도 안됨."
Add-Signal "x0TKvrIdIwI" "박병창" "전력/에너지 섹터" "" "SECTOR" "BUY" "결론" "high" "40:38" "AI가 끝나도 끝까지 AI의 수혜를 보면서 끝까지 갈 때가 전력 에너지" "트럼프 빅테크 자체 전력 확보 서명 정책. 원전/SMR 수혜 지속. 최후까지 수혜 섹터."

# === Video 6: sampro_irK0YCnox78 - 김장열 ===
Add-Signal "irK0YCnox78" "김장열" "삼성전자" "005930" "KR" "BUY" "전망" "high" "02:16" "삼성전자 오늘 7% 올랐는데 배당 관련 밸류업 공시 영향" "3/19 밸류업 공시 예정. 배당성향 30%에서 상향 가능성. 조세특례법 시행령 수혜."
Add-Signal "irK0YCnox78" "김장열" "엔비디아" "NVDA" "US" "POSITIVE" "전망" "medium" "05:44" "실적 3-6% 상회, 가이던스 중간포인트 7% 상회. 나쁜게 아니다" "GPM 75% 유지, EPS 6% 상회. 추론형 시장 확대가 메모리 가격 상승 정당화."

# === Video 7: sampro_qYAiv0Kljas - 이건희/김장열 ===
Add-Signal "qYAiv0Kljas" "이건희" "현대차" "005380" "KR" "BUY" "결론" "high" "14:00" "현대차 지금이라도 사야 돼요라고 물어보면 예스라고 말씀드릴 수 있어요" "의미있는 거래량 터지면 2-3일 쉬더라도 고점 재돌파. AI데이터센터 12조 투자, 로봇 모멘텀."
Add-Signal "qYAiv0Kljas" "이건희" "대한항공" "003490" "KR" "BUY" "결론" "medium" "12:28" "대한항공 9% 이상 올랐습니다. 박스권 뚫고 나갔다" "반도체 호황→항공화물 수혜. 방산/우주항공 사업 프리미엄. 주봉 박스권 돌파."
Add-Signal "qYAiv0Kljas" "김장열" "코스피" "" "SECTOR" "BUY" "전망" "high" "09:25" "8천까지 부른 사람이 있으면 잡더라도 6500은 가겠죠" "상승속도 빠르나 기간조정 가능. 그래도 추세 꺾이지 않았으므로 주도주 편입 권유."
Add-Signal "qYAiv0Kljas" "이건희" "현대건설" "000720" "KR" "POSITIVE" "전망" "medium" "08:40" "현대건설이 더 갈 수 있을까? 그랬는데 더 가네요" "건설+원전 테마 지속. 코스피 상승 수혜 섹터 중 하나."

# === Video 8: sampro_I4Tt3tevuTU - 박명성 ===
Add-Signal "I4Tt3tevuTU" "박명성" "삼성전자" "005930" "KR" "BUY" "전망" "high" "04:12" "삼성전자 7.2% 올라가고 있고 하이닉스 7.7% 올라갑니다" "코스피 6300 돌파. 삼성전자+하이닉스 7%대 동반 상승. 역사적 장세에 참여해야."
Add-Signal "I4Tt3tevuTU" "박명성" "SK하이닉스" "000660" "KR" "BUY" "전망" "high" "04:12" "시총 상위 1위부터 10위까지 반도체 투톱 달려가고" "20만전자, 100만닉스 안착 구간. 역사적 상승장 지속."

# === Video 9: sampro_8-hYd-8eojE - 장우진 ===
Add-Signal "8-hYd-8eojE" "장우진" "코스피" "" "SECTOR" "CONCERN" "결론" "medium" "02:08" "너무 급하게 달렸기 때문에 쉼표가 필요한게 아닌가. 현금 20-30% 챙겨두라" "36거래일 중 29일 상승. 상승장 이견 없으나 속도 과열. 기간조정 가능성 경계."
Add-Signal "8-hYd-8eojE" "장우진" "방산주" "" "SECTOR" "CONCERN" "전망" "medium" "05:07" "이란 전쟁 시 유가 120불 시나리오. 아시아 타격" "이란 공격시 호르무즈 해협 봉쇄→유가 급등→한국 인플레이션 부담. 단기 충격 가능."

# === Video 10: sampro_hxpOT8n_ICw - 고연수 ===
Add-Signal "hxpOT8n_ICw" "고연수" "증권 섹터" "" "SECTOR" "BUY" "결론" "high" "06:27" "증권주는 거의 다 편하게 가져가도 된다. 무조건 지금보다 수익률이 더 나을 수 있다" "연초대비 93% 상승이나 실적 성장 뒷받침. 거래대금 27조→65조. 브로커리지 40%+ 성장 기대."
Add-Signal "hxpOT8n_ICw" "고연수" "NH투자증권" "005940" "KR" "BUY" "결론" "high" "06:49" "주주환원 매력도 제일 높은 증권사는 NH투자증권" "배당성향 40%+, DPS 전년대비 20% 성장 전망. 배당+실적 성장 동시."
Add-Signal "hxpOT8n_ICw" "고연수" "삼성증권" "016360" "KR" "BUY" "결론" "high" "07:09" "삼성증권 DPS 전년대비 30% 이상 증가할 것으로 예상" "보수적 배당성향 유지해도 DPS 30%+ 성장. 주주환원 매력."
Add-Signal "hxpOT8n_ICw" "고연수" "미래에셋증권" "006800" "KR" "BUY" "결론" "high" "07:00" "대형증권사 위주로 봐야. 이익 성장 기대할 수 있는 곳" "순익 1조 클럽. 대형증권사 실적+주주환원 확대. 6354억 배당+자사주 소각."

# === Korini videos - Canton/Crypto ===
Add-Signal "awXkJ9hK-a0" "코린이 아빠" "캔톤네트워크" "CC" "CRYPTO" "BUY" "결론" "high" "07:44" "켄톤은 절대 달러 패권에 도전하지 않습니다. 허가받은 소각용 코인" "허가형 블록체인: KYC 필수, 거래 프라이버시 보호, 규제당국 열람 가능, 알고리즘 안전장치. 미국 정부가 신뢰할 수 있는 유일한 구조."

Add-Signal "82TEaq8GIfc" "코린이 아빠" "캔톤네트워크" "CC" "CRYPTO" "STRONG_BUY" "결론" "high" "09:03" "삼성은 2020년 이미 알아보고 디지털SS에 투자. 시장을 근본적으로 변화시킨다" "업비트 노드 참여=상장 임박. 바이낸스 현물 상장 준비중. 밸리데이터 675개로 확대. 연매출 5억달러+ 대비 시총 50억달러 미만=저평가."

Add-Signal "7AaksU-R3dg" "코린이 아빠" "XRP" "XRP" "CRYPTO" "SELL" "결론" "high" "03:17" "월드리버티파이낸셜이 USD1으로 국경간 송금 환전 다 가져가겠다 선언. XRP 네러티브 잠식" "트럼프 일가 USD1 스테이블코인이 XRP의 브릿지통화 역할을 직접 대체. 멀티체인 전략으로 50억달러+ 규모. XRP 핵심 가치 제안 위협."

Add-Signal "7AaksU-R3dg" "코린이 아빠" "알트코인 전반" "" "CRYPTO" "STRONG_SELL" "결론" "high" "05:48" "2026 알트코인 대멸종. 점점 더 현실화되고 있습니다" "비탈릭 80% 매도. 대부분 코인 떡락 중. 프라이버시 무시한 퍼블릭 체인 한계 노출."

Add-Signal "A7qHwvcGh9A" "코린이 아빠" "캔톤네트워크" "CC" "CRYPTO" "STRONG_BUY" "결론" "high" "09:15" "오직 실적으로 말하는 코인은 하나뿐인 캔톤. 밸류에이션 6-7배밖에 안된다" "일 300만달러 소각=연 10억달러 매출. 시총 대비 6-7배 밸류에이션. 액티브어드레스 50% 증가. 실적 증명하는 유일한 알트코인."

Add-Signal "Vy2jrX-uCbY" "코린이 아빠" "캔톤네트워크" "CC" "CRYPTO" "BUY" "결론" "high" "03:42" "AI 거품이 붕괴해도 캔톤이 살아남는 이유" "AI와 크립토 연결. AI 거품 붕괴 시 네러티브 코인 전멸하나 실사용 인프라인 캔톤은 생존. RWA 토큰화 인프라로서의 가치."

Add-Signal "TjKVuAGhC1M" "코린이 아빠" "캔톤네트워크" "CC" "CRYPTO" "POSITIVE" "전망" "medium" "03:15" "코인 거래소의 스테이블코인 이자 지급이 은행 예금을 위협" "클래리티 법안 무기한 연기=규제 불확실성 지속. 코인베이스 등 거래소의 예대마진 비즈니스 모델 설명. 캔톤은 규제 친화적 구조로 수혜."

Add-Signal "PGQW7nyoRRI" "코린이 아빠" "캔톤네트워크" "CC" "CRYPTO" "STRONG_BUY" "결론" "high" "06:46" "이미 대형기관 도매거래 확대 중. 리테일 시장 2차 로켓 추진 준비중. 올해 내 될 것" "한화증권 크리소스 MOU=캔톤 리테일 진입. 삼성월렛 통합 구상 완료. 비트겟 주식선물 거래 시작=RWA 시대. 기관전용 아닌 리테일 확장 중."

Write-Host "Total signals prepared: $($signals.Count)"

# Insert signals
$inserted = 0
$failed = 0
foreach ($s in $signals) {
    try {
        $body = $s | ConvertTo-Json -Depth 5
        $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
        $r = Invoke-RestMethod -Uri "$BASE/influencer_signals" -Method Post -Headers $headers -Body $bodyBytes
        $inserted++
        Write-Host "OK: $($s.stock) - $($s.signal)"
    } catch {
        $failed++
        Write-Host "FAIL: $($s.stock) - $($_.Exception.Message)"
    }
}

Write-Host "`n=== RESULTS ==="
Write-Host "Inserted: $inserted"
Write-Host "Failed: $failed"
Write-Host "Total prepared: $($signals.Count)"
