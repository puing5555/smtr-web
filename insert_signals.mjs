const BASE = "https://arypzhotxflimroprmdk.supabase.co/rest/v1";
const KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A";
const headers = {
  "apikey": KEY,
  "Authorization": `Bearer ${KEY}`,
  "Content-Type": "application/json",
  "Prefer": "return=representation"
};

const videoMap = {
  "R6w3T3eUVIs": "2f1794a4-01f6-4ece-a5f7-01882e107aa9",
  "-US4r1E1kOQ": "9236a7e9-8a4b-4291-b6ef-19cc83991e5e",
  "XFHD_1M3Mxg": "900806f6-434f-4913-82c7-2b69a80284d0",
  "ldT75QwBB6g": "bee43acd-68d6-4247-98bd-1c1365c8815d",
  "x0TKvrIdIwI": "c7bf5e71-50d1-4ffa-94a7-e3bce9ec49a5",
  "irK0YCnox78": "e9012cde-ddbc-4819-8745-ef93fff6327f",
  "qYAiv0Kljas": "235ea3ae-5b54-4f6b-9a12-0f57da76d919",
  "I4Tt3tevuTU": "d210f06a-ff68-458f-8d8c-d34724d63458",
  "8-hYd-8eojE": "d66104b7-0b88-463e-b2a9-34b6797404da",
  "hxpOT8n_ICw": "c2952626-8842-4561-b297-468f6733d8f7",
  "awXkJ9hK-a0": "baadbc77-38fd-46bf-8270-6c780c19cb0e",
  "82TEaq8GIfc": "4fbee999-8f87-451e-85cc-54f31e17bf26",
  "7AaksU-R3dg": "1fa51ee5-980e-45e8-bd3f-1f90b501c35d",
  "A7qHwvcGh9A": "6961f2b0-beea-4845-a094-c7572a7ca792",
  "Vy2jrX-uCbY": "59a6b272-7eeb-4719-af66-2242066a7e33",
  "TjKVuAGhC1M": "951857cf-e963-4639-b256-2a8095c3c5fa",
  "PGQW7nyoRRI": "da2b8045-ad74-49de-8c1e-d1c8e441f11c"
};

const speakerMap = {
  "\uBC30\uC7AC\uC6D0": "7fef30a4-a248-44d6-99b9-02bda6f47eb2",
  "\uACE0\uC5F0\uC218": "3508abce-70e0-4eaa-a0d4-686b61071dd9",
  "\uAE40\uC7A5\uB144": "03baa455-178d-4a82-bf47-6a12ccc2b694",
  "\uAE40\uB3D9\uD6C8": "5783838f-af5f-4e74-bcbf-bbc20141b199",
  "\uBC15\uC9C0\uD6C8": "e59ed6f5-7a8d-4111-af1c-502ad3344e79",
  "\uBC15\uBCD1\uCC3D": "2720d0ee-b7e2-4006-80df-90bc9de07797",
  "\uAE40\uC7A5\uC5F4": "8234cd75-1d0d-458c-b01c-62080c7d91e3",
  "\uBC15\uBA85\uC131": "5d03d08f-abb4-453b-bf86-40e57a0ddfdb",
  "\uC7A5\uC6B0\uC9C4": "aa25b0e6-aadf-4bae-a2fa-afc0a067e315",
  "\uC774\uAC74\uD76C": "731fe32d-f47a-432f-9899-305915138983",
  "\uCF54\uB9B0\uC774 \uC544\uBE60": "2e9a8a44-3eb8-4009-8318-5e8d23a62840"
};

const signals = [
  // Video 1: R6w3T3eUVIs - 배재원
  {vid:"R6w3T3eUVIs",sp:"배재원",stock:"삼성전자",ticker:"005930",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"07:00",quote:"비중이 없는 분은 지금이라도 물리더라도 들어가야 된다",reason:"영업이익 추정치 계속 상향, 목표주가 30만원 이상. 10%라도 포지션 진입 권유."},
  {vid:"R6w3T3eUVIs",sp:"배재원",stock:"SK하이닉스",ticker:"000660",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"08:46",quote:"하이닉스 30만원이면 당연히 사겠죠",reason:"메모리 수요 강세, HBM 비용 상승=공급부족. 영업이익 추정치 상향 지속."},
  {vid:"R6w3T3eUVIs",sp:"배재원",stock:"코스피",ticker:"",market:"SECTOR",signal:"BUY",mt:"결론",conf:"high",ts:"06:14",quote:"상반기에 7000포인트 역사적 순간도 볼 수 있지 않을까",reason:"코스피 영업이익 600조대 상향, 리레이팅 가능성. MSCI코리아ETF 자금유입 가속."},

  // Video 2: -US4r1E1kOQ - 김장년
  {vid:"-US4r1E1kOQ",sp:"김장년",stock:"엔비디아",ticker:"NVDA",market:"US",signal:"BUY",mt:"결론",conf:"medium",ts:"04:37",quote:"포지션 없는 분 200달러 전으로 30% 정도 넣어놓고",reason:"실적 인라인, 가이던스 5-7% 상회. PER 23배 저평가. 추론형 AI 인플렉션 포인트."},
  {vid:"-US4r1E1kOQ",sp:"김장년",stock:"삼성전자",ticker:"005930",market:"KR",signal:"STRONG_BUY",mt:"결론",conf:"high",ts:"09:50",quote:"삼성전자 하이닉스 1분기 실적 전에 애널리스트 전망 한번 더 올라갈 수 있다",reason:"엔비디아 추론형 시장 확대→디램 가격 상승 불가피. 노무라 240조, 맥쿼리 300조 전망."},
  {vid:"-US4r1E1kOQ",sp:"김장년",stock:"SK하이닉스",ticker:"000660",market:"KR",signal:"STRONG_BUY",mt:"결론",conf:"high",ts:"09:50",quote:"엔비디아 가는 속도보다 메모리가 덜 가지 않을 것 같다",reason:"추론형 AI로 키밸류캐시용 디램 수요 폭발. HBM+일반디램 모두 수혜."},

  // Video 3: XFHD_1M3Mxg - 김동훈
  {vid:"XFHD_1M3Mxg",sp:"김동훈",stock:"신세계",ticker:"004170",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"01:00",quote:"신세계 주식을 가장 좋게 보고 있다",reason:"인바운드 관광객 증가+원화약세. 이세탄 사례(4년7배). PER12.6→과거고점16.7 여력. 외국인20% 순매수."},
  {vid:"XFHD_1M3Mxg",sp:"김동훈",stock:"삼성전자",ticker:"005930",market:"KR",signal:"BUY",mt:"전망",conf:"medium",ts:"18:02",quote:"삼성전자 지금 PER 20배도 안돼서 싸다",reason:"시티 목표주가 34만원 상향. 영업이익 상향 지속 중."},

  // Video 4: ldT75QwBB6g - 박지훈
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"효성중공업",ticker:"298040",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"16:43",quote:"이 세 개 종목 올해도 계속. 효중이 대장으로 치고 나갈 가능성 매우 크다",reason:"전력인프라 실체 있는 실적. 4분기 HD현대일렉과 매출단 맞닿을 전망. 시총 26조."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"HD현대일렉트릭",ticker:"267260",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"19:03",quote:"HD현대도 팔면 안됨. 유럽 수주 모멘텀",reason:"올해 유럽 수주 개시. 미국+유럽 투트랙. 시총38조 전력3사 최대."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"LS일렉트릭",ticker:"010120",market:"KR",signal:"HOLD",mt:"전망",conf:"medium",ts:"18:11",quote:"LS일렉이 고밸류. 매출단 효성중공업 반도 안됨",reason:"시총23조인데 매출 규모 대비 상대적 고밸류. 전력 3사 중 우선순위 낮음."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"삼성전기",ticker:"009150",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"25:56",quote:"2026년 대박주를 삼성전기로 선택했습니다",reason:"피지컬AI 핵심. MLCC+휴머노이드OLED부품. 핸드셋전환기 원년."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"솔브레인",ticker:"357780",market:"KR",signal:"BUY",mt:"결론",conf:"medium",ts:"28:23",quote:"소부장 소재단은 꼭 하나 정도 들고 가셨으면",reason:"외국인 펀드매니저 9:1로 소재 관심. 미국진출+유리기판+블랙PDL 모멘텀."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"LG화학",ticker:"051910",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"36:28",quote:"LG화학 강력 추천. 행동주의 펀드 활동으로 주총 시즌 모멘텀",reason:"팰리서캐피탈 행동주의. PBR0.8배, 외국인35%+. 3월 주총시즌 촉매."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"NC소프트",ticker:"036570",market:"KR",signal:"HOLD",mt:"결론",conf:"medium",ts:"32:31",quote:"NC소프트 홀딩하셔도 되겠다. 목표주가 40만원대",reason:"3년만에 어닝 회복. 가이던스 3600억(YoY 2142%). 박스권 탈출 시도중."},
  {vid:"ldT75QwBB6g",sp:"박지훈",stock:"하이브",ticker:"352820",market:"KR",signal:"HOLD",mt:"결론",conf:"medium",ts:"33:42",quote:"홀딩 의견 강력하게 말씀드리고 싶고",reason:"BTS 복귀 모멘텀. 차이나플레이 약화됐으나 어닝 확인시 재점핑 가능."},

  // Video 5: x0TKvrIdIwI - 박병창
  {vid:"x0TKvrIdIwI",sp:"박병창",stock:"삼성전자",ticker:"005930",market:"KR",signal:"POSITIVE",mt:"전망",conf:"high",ts:"04:04",quote:"3월19일 밸류업 관련 발표 예정. 포모현상은 있으나",reason:"메타+AMD 공급계약, 밸류업 공시 기대. 다만 포모현상 경계. 넥스트에서 추가 상승."},
  {vid:"x0TKvrIdIwI",sp:"박병창",stock:"SK하이닉스",ticker:"000660",market:"KR",signal:"POSITIVE",mt:"전망",conf:"high",ts:"06:31",quote:"시총725조, 영업이익160조면 멀티플5배도 안돼. 내년이면 3배도 안됨",reason:"엔비디아 912억달러 미지급구매. 절대 밸류에이션 저평가."},
  {vid:"x0TKvrIdIwI",sp:"박병창",stock:"전력/에너지",ticker:"",market:"SECTOR",signal:"BUY",mt:"결론",conf:"high",ts:"40:38",quote:"AI 끝나도 끝까지 수혜 보면서 갈 때가 전력에너지",reason:"트럼프 빅테크 자체전력 확보 서명. 원전/SMR 호재 지속."},

  // Video 6: irK0YCnox78 - 김장열
  {vid:"irK0YCnox78",sp:"김장열",stock:"삼성전자",ticker:"005930",market:"KR",signal:"BUY",mt:"전망",conf:"high",ts:"02:16",quote:"삼성전자 오늘 7% 올랐는데 배당 밸류업 공시 영향",reason:"3/19 밸류업 공시 예정. 배당 10%이상 상향 가능. 넥스트에서 10% 추가상승."},
  {vid:"irK0YCnox78",sp:"김장열",stock:"엔비디아",ticker:"NVDA",market:"US",signal:"POSITIVE",mt:"전망",conf:"medium",ts:"05:44",quote:"실적 3-6% 상회, 가이던스 7% 상회. 나쁜게 아니다",reason:"GPM 75% 유지, EPS 6% 상회. 추론형 확대→메모리 수혜 정당화."},

  // Video 7: qYAiv0Kljas - 이건희/김장열
  {vid:"qYAiv0Kljas",sp:"이건희",stock:"현대차",ticker:"005380",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"14:00",quote:"현대차 지금이라도 사야돼요? 예스",reason:"거래량 터지면 2-3일쉬고 고점재돌파. AI데이터센터12조투자+로봇모멘텀."},
  {vid:"qYAiv0Kljas",sp:"이건희",stock:"대한항공",ticker:"003490",market:"KR",signal:"BUY",mt:"결론",conf:"medium",ts:"12:28",quote:"대한항공 9%이상 상승. 박스권 뚫고 나갔다",reason:"반도체호황→항공화물 수혜. 방산/우주항공 프리미엄. 주봉 박스권 돌파."},
  {vid:"qYAiv0Kljas",sp:"김장열",stock:"코스피",ticker:"",market:"SECTOR",signal:"BUY",mt:"전망",conf:"high",ts:"09:25",quote:"8천 부른 사람도 있으면 잡아도 6500은 가겠죠",reason:"상승속도 빠르나 추세 미꺾임. 주도주 편입 권유."},
  {vid:"qYAiv0Kljas",sp:"이건희",stock:"현대건설",ticker:"000720",market:"KR",signal:"POSITIVE",mt:"전망",conf:"medium",ts:"08:40",quote:"현대건설 더 갈 수 있을까? 더 가네요",reason:"건설+원전 테마 지속. 코스피 상승 수혜 섹터."},

  // Video 8: I4Tt3tevuTU - 박명성
  {vid:"I4Tt3tevuTU",sp:"박명성",stock:"삼성전자",ticker:"005930",market:"KR",signal:"BUY",mt:"전망",conf:"high",ts:"04:12",quote:"삼성전자 7.2%, 하이닉스 7.7% 올라간다",reason:"코스피 6300돌파. 역사적 장세 참여 필요."},
  {vid:"I4Tt3tevuTU",sp:"박명성",stock:"SK하이닉스",ticker:"000660",market:"KR",signal:"BUY",mt:"전망",conf:"high",ts:"04:12",quote:"시총 상위 1-10위 반도체 투톱 달려간다",reason:"20만전자 100만닉스 안착. 역사적 상승장 지속."},

  // Video 9: 8-hYd-8eojE - 장우진
  {vid:"8-hYd-8eojE",sp:"장우진",stock:"코스피",ticker:"",market:"SECTOR",signal:"CONCERN",mt:"결론",conf:"medium",ts:"02:08",quote:"너무 급하게 달려서 쉼표 필요. 현금 20-30% 챙겨두라",reason:"36거래일중 29일 상승. 상승장 이견없으나 속도과열 경계."},

  // Video 10: hxpOT8n_ICw - 고연수
  {vid:"hxpOT8n_ICw",sp:"고연수",stock:"증권섹터",ticker:"",market:"SECTOR",signal:"BUY",mt:"결론",conf:"high",ts:"06:27",quote:"증권주 거의 다 편하게 가져가도 된다. 무조건 수익률 더 나을 것",reason:"연초대비 93%상승이나 실적뒷받침. 거래대금 27→65조. 브로커리지40%+ 성장."},
  {vid:"hxpOT8n_ICw",sp:"고연수",stock:"NH투자증권",ticker:"005940",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"06:49",quote:"주주환원 매력도 제일 높은 증권사 NH투자증권",reason:"배당성향40%+, DPS 전년대비20% 성장. 배당+실적 동시."},
  {vid:"hxpOT8n_ICw",sp:"고연수",stock:"삼성증권",ticker:"016360",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"07:09",quote:"삼성증권 DPS 전년대비 30%이상 증가 예상",reason:"보수적 배당성향 유지해도 DPS30%+ 성장."},
  {vid:"hxpOT8n_ICw",sp:"고연수",stock:"미래에셋증권",ticker:"006800",market:"KR",signal:"BUY",mt:"결론",conf:"high",ts:"07:00",quote:"대형증권사 위주로. 이익성장 기대",reason:"순익1조 클럽. 6354억 배당+자사주소각 발표."},

  // Korini - Crypto
  {vid:"awXkJ9hK-a0",sp:"코린이 아빠",stock:"캔톤네트워크",ticker:"CC",market:"CRYPTO",signal:"BUY",mt:"결론",conf:"high",ts:"07:44",quote:"켄톤은 달러 패권에 도전하지 않는다. 허가받은 소각용 코인",reason:"허가형 블록체인: KYC필수, 프라이버시보호, 규제당국열람가능. 미국정부 신뢰 구조."},
  {vid:"82TEaq8GIfc",sp:"코린이 아빠",stock:"캔톤네트워크",ticker:"CC",market:"CRYPTO",signal:"STRONG_BUY",mt:"결론",conf:"high",ts:"09:03",quote:"삼성은 2020년 이미 투자. 시장을 근본적으로 변화시킨다",reason:"업비트노드참여=상장임박. 밸리데이터675개 확대. 연매출5억$+ vs 시총50억$ 미만."},
  {vid:"7AaksU-R3dg",sp:"코린이 아빠",stock:"XRP",ticker:"XRP",market:"CRYPTO",signal:"SELL",mt:"결론",conf:"high",ts:"03:17",quote:"월드리버티파이낸셜이 USD1으로 국경간 송금환전 다 가져가겠다 선언",reason:"트럼프일가 USD1이 XRP 브릿지통화 역할 직접대체. 50억$+ 규모."},
  {vid:"7AaksU-R3dg",sp:"코린이 아빠",stock:"알트코인전반",ticker:"",market:"CRYPTO",signal:"STRONG_SELL",mt:"결론",conf:"high",ts:"05:48",quote:"2026 알트코인 대멸종. 점점 더 현실화",reason:"비탈릭80% 매도. 대부분 코인 떡락. 프라이버시 무시한 퍼블릭체인 한계."},
  {vid:"A7qHwvcGh9A",sp:"코린이 아빠",stock:"캔톤네트워크",ticker:"CC",market:"CRYPTO",signal:"STRONG_BUY",mt:"결론",conf:"high",ts:"09:15",quote:"오직 실적으로 말하는 코인은 하나뿐인 캔톤. 밸류에이션 6-7배",reason:"일300만$ 소각=연10억$ 매출. 시총대비 6-7배. 실적증명 유일한 알트코인."},
  {vid:"Vy2jrX-uCbY",sp:"코린이 아빠",stock:"캔톤네트워크",ticker:"CC",market:"CRYPTO",signal:"BUY",mt:"결론",conf:"high",ts:"03:42",quote:"AI 거품 붕괴해도 캔톤 살아남는 이유",reason:"실사용 인프라→AI거품과 무관. RWA 토큰화 인프라 가치."},
  {vid:"TjKVuAGhC1M",sp:"코린이 아빠",stock:"캔톤네트워크",ticker:"CC",market:"CRYPTO",signal:"POSITIVE",mt:"전망",conf:"medium",ts:"03:15",quote:"클래리티법안 무기한 연기. 규제 불확실성 지속",reason:"코인거래소 예대마진 비즈니스 설명. 캔톤은 규제친화적 구조로 수혜 가능."},
  {vid:"PGQW7nyoRRI",sp:"코린이 아빠",stock:"캔톤네트워크",ticker:"CC",market:"CRYPTO",signal:"STRONG_BUY",mt:"결론",conf:"high",ts:"06:46",quote:"대형기관 도매거래 확대중. 리테일 2차로켓 준비중. 올해내 될것",reason:"한화증권MOU=리테일진입. 삼성월렛통합 구상완료. 기관전용 아닌 리테일 확장."},
];

async function insertSignal(s) {
  const body = {
    video_id: videoMap[s.vid],
    speaker_id: speakerMap[s.sp],
    stock: s.stock,
    ticker: s.ticker,
    market: s.market,
    signal: s.signal,
    mention_type: s.mt,
    confidence: s.conf,
    timestamp: s.ts,
    key_quote: s.quote,
    reasoning: s.reason,
    pipeline_version: "V9.1",
    review_status: "pending"
  };
  const r = await fetch(`${BASE}/influencer_signals`, {method:"POST", headers, body: JSON.stringify(body)});
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return await r.json();
}

async function main() {
  console.log(`Total signals to insert: ${signals.length}`);
  let ok=0, fail=0;
  for (const s of signals) {
    try {
      await insertSignal(s);
      ok++;
      console.log(`OK: ${s.stock} - ${s.signal}`);
    } catch(e) {
      fail++;
      console.log(`FAIL: ${s.stock} - ${e.message}`);
    }
  }
  console.log(`\n=== RESULTS ===`);
  console.log(`Inserted: ${ok}`);
  console.log(`Failed: ${fail}`);
  
  // Now count total signals in DB
  const r = await fetch(`${BASE}/influencer_signals?select=id&pipeline_version=eq.V9.1`, {headers:{"apikey":KEY,"Authorization":`Bearer ${KEY}`}});
  const data = await r.json();
  console.log(`Total V9.1 signals in DB: ${data.length}`);
  
  const r2 = await fetch(`${BASE}/influencer_signals?select=id`, {headers:{"apikey":KEY,"Authorization":`Bearer ${KEY}`}});
  const data2 = await r2.json();
  console.log(`Total all signals in DB: ${data2.length}`);
}

main().catch(console.error);
