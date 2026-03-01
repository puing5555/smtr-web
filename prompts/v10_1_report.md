# V10.1 프롬프트 개선 - 라운드 1 분석 보고서

## 기본 정보
- 분석 일시: 2026-03-01 15:22:12
- 총 시그널 수: 99
- 발견된 이슈 수: 144

## 이슈 분류별 현황

### 1. key_quote 품질 이슈 (113건)
- [042cf439-e42f-4822-b9fd-6efaac70b854] no_investment_reasoning: key_quote에 투자근거 없음: "GPU를 생산하는 회사는 TSM입니다. 여기에 20%"
- [050ddf63-9f8a-487b-ae70-5d7f30ae1b6f] stock_not_mentioned_in_quote: key_quote에 종목명(현대차) 미포함: "자동차 회사가 로봇 회사로 바뀌면서 멀티플이 바뀌는 어마어마한 그런게 있다"
- [050ddf63-9f8a-487b-ae70-5d7f30ae1b6f] no_investment_reasoning: key_quote에 투자근거 없음: "자동차 회사가 로봇 회사로 바뀌면서 멀티플이 바뀌는 어마어마한 그런게 있다"
- [072420e3-2ae3-4942-84f8-2c38a6e835f4] no_investment_reasoning: key_quote에 투자근거 없음: "저는 엔비디아라는 회사는 모바일 혁명의 애플처럼 주식 궤도를 그릴 거라고 생각해요"
- [0b1207d3-8144-4e27-b5b6-adad57709e27] stock_not_mentioned_in_quote: key_quote에 종목명(HM파마) 미포함: "제가 창업한 회사가 하나 있거든요. H 파마예요"
- [0d83bde0-d91c-45da-af79-0a360db6c6ad] stock_not_mentioned_in_quote: key_quote에 종목명(NH투자증권) 미포함: "배당이랑 실적 성장 둘 다 가져갈 수 있다, DPS는 전년 대비 20% 성장"
- [0f3c3f27-ddb4-4dec-a16d-7f28163db5f1] key_quote_too_short: key_quote가 20자 미만 (현재 16자): "삼성도 좋아요. 삼성전자 좋아"
- [0f3c3f27-ddb4-4dec-a16d-7f28163db5f1] no_investment_reasoning: key_quote에 투자근거 없음: "삼성도 좋아요. 삼성전자 좋아"
- [11e95a7f-a408-4a9a-9072-f1b238db28e5] stock_not_mentioned_in_quote: key_quote에 종목명(주성엔지니어링) 미포함: "기술 옵션이 가장 풍부한 종목, 눌림목 오게 되면 매수하는 전략도 나쁘지 않다"
- [11e95a7f-a408-4a9a-9072-f1b238db28e5] no_investment_reasoning: key_quote에 투자근거 없음: "기술 옵션이 가장 풍부한 종목, 눌림목 오게 되면 매수하는 전략도 나쁘지 않다"
- [163d4529-4871-4f34-ac74-271407952cd6] stock_not_mentioned_in_quote: key_quote에 종목명(SK하이닉스) 미포함: "지금이라도 사야 돼. 저는 뭐 사야 된다고 생각하지만. 추가적으로 담아가시는 전략이 낫지 않을까"
- [163d4529-4871-4f34-ac74-271407952cd6] no_investment_reasoning: key_quote에 투자근거 없음: "지금이라도 사야 돼. 저는 뭐 사야 된다고 생각하지만. 추가적으로 담아가시는 전략이 낫지 않을까"
- [1c3a1827-db67-458f-955b-11bb7b554575] stock_not_mentioned_in_quote: key_quote에 종목명(하이브) 미포함: "홀딩 의견 강력하게 말씀드리고 싶고... 어닝이 확인되면 충분히 다시 점핑할 가능성"
- [1c3a1827-db67-458f-955b-11bb7b554575] no_investment_reasoning: key_quote에 투자근거 없음: "홀딩 의견 강력하게 말씀드리고 싶고... 어닝이 확인되면 충분히 다시 점핑할 가능성"
- [1cda9f77-c6cf-43b6-83be-6542e9930f58] stock_not_mentioned_in_quote: key_quote에 종목명(SK하이닉스) 미포함: "여전히 주인공이다라는 생각을 하고 있습니다"
- [1cda9f77-c6cf-43b6-83be-6542e9930f58] no_investment_reasoning: key_quote에 투자근거 없음: "여전히 주인공이다라는 생각을 하고 있습니다"
- [20fe5054-8bda-4b78-8285-bd5270fb57f7] stock_not_mentioned_in_quote: key_quote에 종목명(HD현대일렉트릭) 미포함: "AI 인프라의 핵심 파트너가 돼 버렸다. 아주 강력한 모트"
- [20fe5054-8bda-4b78-8285-bd5270fb57f7] no_investment_reasoning: key_quote에 투자근거 없음: "AI 인프라의 핵심 파트너가 돼 버렸다. 아주 강력한 모트"
- [21f03a71-d3a6-437a-aafb-1ef0f8b224f6] no_investment_reasoning: key_quote에 투자근거 없음: "원익 IPS 테스 유진테크 뭐 두산 테스나 뭐 하나 마이크론 뭐 이런 회사들도 여전히 업사이드가 있다고 보고 있습니다"
- [2244a98d-2de6-40a7-bd0a-8f0104126e5e] no_investment_reasoning: key_quote에 투자근거 없음: "HD현대일렉트릭이나 효성중공업이 AI 인프라의 핵심 파트너가 돼 버렸다"
- [2bb7d896-a03c-4413-ac3e-9717c59b9090] no_investment_reasoning: key_quote에 투자근거 없음: "대한민국 장비주에서 한미반도체나 원익IPS 같은 이런 종목군들 매수하시게 된다라면 어렵지 않을 것 같고요"
- [2d5d8a4b-a6e1-425a-98f5-8767a142193e] stock_not_mentioned_in_quote: key_quote에 종목명(로봇 섹터) 미포함: "로봇 관련 주식이 올라가는 건 너무 좋은데 조금 빠르지 않나 싶은 생각이. 한 2,3년은 걸려야"
- [2d5d8a4b-a6e1-425a-98f5-8767a142193e] no_investment_reasoning: key_quote에 투자근거 없음: "로봇 관련 주식이 올라가는 건 너무 좋은데 조금 빠르지 않나 싶은 생각이. 한 2,3년은 걸려야"
- [33078122-93ea-4001-83bd-58ee6dc8e4df] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "리레이팅 된 거 없다. 이익 전망 따라간 거. 밸류에이션 상으로 부담되지는 않는다"
- [332a5809-ad05-4697-89f2-1a8e2f6cb359] stock_not_mentioned_in_quote: key_quote에 종목명(SMR/원전) 미포함: "단언컨대 SMR은 올해 가장 강력한 섹터가 될 것입니다"
- [332a5809-ad05-4697-89f2-1a8e2f6cb359] no_investment_reasoning: key_quote에 투자근거 없음: "단언컨대 SMR은 올해 가장 강력한 섹터가 될 것입니다"
- [3f5e9c95-9ec0-41c9-a700-683e9257d5f8] stock_not_mentioned_in_quote: key_quote에 종목명(현대차) 미포함: "삼성증권 85만원, 65만원, 60만원, 80만원. 격차가 되게 커요"
- [3fe9c19f-d7da-42f6-a677-be82ea350afd] stock_not_mentioned_in_quote: key_quote에 종목명(코스피) 미포함: "이 전투의 결론이 무조건 위로가야 됩니다. 지금 무조건 위로 가야 되는 상황이지 않나 생각이 되고"
- [3fe9c19f-d7da-42f6-a677-be82ea350afd] no_investment_reasoning: key_quote에 투자근거 없음: "이 전투의 결론이 무조건 위로가야 됩니다. 지금 무조건 위로 가야 되는 상황이지 않나 생각이 되고"
- [414a3173-afac-46b8-af46-48615d2293e6] no_investment_reasoning: key_quote에 투자근거 없음: "SK하이닉스하고 삼성원자 같은 경우에는 여러분들 포트폴리오에 당연히 있으셔야 된다"
- [418512f8-30ff-438a-9f56-f5a151536b09] no_investment_reasoning: key_quote에 투자근거 없음: "삼성전자 밸류업 공시가 주총 직후 나오지 않겠냐. 최소한 배당이 전년보다 10% 이상 증가되겠구나 생각할 수 있다"
- [41daad11-7b68-4815-b380-eef73f8555c0] no_investment_reasoning: key_quote에 투자근거 없음: "지금 피지컬 AI를 사실 최 전선에서 드라이브를 걸고 있는 회사는 테슬라고요"
- [493f2bf6-d84d-43c6-898e-7ec2e68ed1a3] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "여전히 너무 저렴한 거 같습니다. 이익 전망치가 개선되고 있다"
- [58b2432f-071a-4208-a1d8-90f3f0222517] stock_not_mentioned_in_quote: key_quote에 종목명(삼성증권) 미포함: "DPS가 전년 대비 30% 이상 증가할 것으로 예상, 배당 수익률 4% 후반"
- [5a8d8634-625b-4e6a-b93b-47380dbe329c] no_investment_reasoning: key_quote에 투자근거 없음: "현대차 지금이라도 사야 돼요라고 물어보면 저는 예스. 의미 있는 거래량을 터트렸다는 거는 한 2, 3일이 쉬더라도 다시 고점을 뚫겠다"
- [5ae58cc4-830b-4abe-8d2e-c0dc7d3fe76d] no_investment_reasoning: key_quote에 투자근거 없음: "원익 IPS 테스 유진테크 뭐 두산 테스나 뭐 하나 마이크론 뭐 이런 회사들도 여전히 업사이드가 있다고 보고 있습니다"
- [6ab0f37a-1bac-4010-988a-f14db3e2b1e8] stock_not_mentioned_in_quote: key_quote에 종목명(키움증권) 미포함: "키움 증권 같은 경우에도 전년 대비 순익이 20% 성장할 것으로 예상"
- [71ff56f8-deb9-49c1-9c18-bc4fd717d666] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "삼성은 계속 올라갑니다 SK는 계속 떨어지고 그러면서 제가 보기에는 그때 되면 역전할 것 같아요"
- [71ff56f8-deb9-49c1-9c18-bc4fd717d666] no_investment_reasoning: key_quote에 투자근거 없음: "삼성은 계속 올라갑니다 SK는 계속 떨어지고 그러면서 제가 보기에는 그때 되면 역전할 것 같아요"
- [720aef52-2d6a-45f1-b8bd-b888a96813ae] stock_not_mentioned_in_quote: key_quote에 종목명(소프트웨어 섹터) 미포함: "장기적으로 다시 소프트웨어가 예전에 그런 영광을 누릴 수 있다고 배팅을 하는 거는 조금 자제를 해야 되지 않나"
- [720aef52-2d6a-45f1-b8bd-b888a96813ae] no_investment_reasoning: key_quote에 투자근거 없음: "장기적으로 다시 소프트웨어가 예전에 그런 영광을 누릴 수 있다고 배팅을 하는 거는 조금 자제를 해야 되지 않나"
- [75042710-e161-4b46-bb9e-ae97f1e0d98a] no_investment_reasoning: key_quote에 투자근거 없음: "마이크론하고 샌디스크 비슷하 11배... 미국 평균보다 반이잖아요"
- [78b3f927-0ecb-49a7-93df-2dea1ea4d630] stock_not_mentioned_in_quote: key_quote에 종목명(테크 기업) 미포함: "디지털 시대의 투자 전략은 제조업이 아닌 테크배 해야 된다는 얘기입니다"
- [7a6e30a3-db8d-42a4-8b62-33b554469e95] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "둘 다 사는게 좋습니다. 지금은 메모리 3사가 굉장히 제일 높은 확률로 업사이드가 남아 있다"
- [7a6e30a3-db8d-42a4-8b62-33b554469e95] no_investment_reasoning: key_quote에 투자근거 없음: "둘 다 사는게 좋습니다. 지금은 메모리 3사가 굉장히 제일 높은 확률로 업사이드가 남아 있다"
- [7ed86fea-e0bb-4604-b0c1-3ba7788966c1] no_investment_reasoning: key_quote에 투자근거 없음: "우선순은 메모리... 하이닉 삼성전자, 샌디스크, 마이크론 넷 중에 하나는 갖고 있어야지"
- [82fe1aa4-e24e-475c-b368-aab1c2a194ca] no_investment_reasoning: key_quote에 투자근거 없음: "GPU는 반드시 HBM이야 작동이 됩니다. SK하이닉스에 20%"
- [83d4e654-d9db-4e5a-9a69-ac85b0ce0699] no_investment_reasoning: key_quote에 투자근거 없음: "하이닉스랑 마이크론이랑 삼성전자 비중 거의 30% 정도로 된 ETF를 사세요"
- [85e74359-3b1f-4694-b9f5-09b8d303659d] stock_not_mentioned_in_quote: key_quote에 종목명(원익IPS) 미포함: "눌림목 오게 되면 매수하는 전략도 나쁘지 않다"
- [85e74359-3b1f-4694-b9f5-09b8d303659d] no_investment_reasoning: key_quote에 투자근거 없음: "눌림목 오게 되면 매수하는 전략도 나쁘지 않다"
- [86996087-c16e-4dfd-9f7a-9be7501ef024] stock_not_mentioned_in_quote: key_quote에 종목명(삼성SDI) 미포함: "삼성 SDI가 탁 어제 15%가 올랐는데요 라인 한 3일 동안의 움직임을 라인이 바로 전고체 배터리 관련주들의 라인이고요"
- [86996087-c16e-4dfd-9f7a-9be7501ef024] no_investment_reasoning: key_quote에 투자근거 없음: "삼성 SDI가 탁 어제 15%가 올랐는데요 라인 한 3일 동안의 움직임을 라인이 바로 전고체 배터리 관련주들의 라인이고요"
- [87f3fa04-503b-4cb5-9000-ee39bd0ce907] no_investment_reasoning: key_quote에 투자근거 없음: "반도체 빅테크 그리고 나스닥은 시간이 흐르면 결국은 올라갈 수밖에 없다고 생각합니다. 왜냐면 이게 세상의 흐름을 끌고 가는 그 핵에 놓여 있는 거거든요"
- [889cc0ca-b605-46af-8ec6-65360b496d5d] stock_not_mentioned_in_quote: key_quote에 종목명(엔비디아) 미포함: "이 정도는 잘 나올 것으로 예상한 그거에 부합했다는 겁니다. 나쁜게 아니에요. 2, 3% 오르는게 정상"
- [8e42adce-5630-4b8a-9e38-1137df6b4173] stock_not_mentioned_in_quote: key_quote에 종목명(아모레퍼시픽) 미포함: "API가 야 너무 많이 올랐어. 두 달 정도 조정받다가 새롭게 요번 주에 역사 주신 거를 돌파했거든요"
- [8e42adce-5630-4b8a-9e38-1137df6b4173] no_investment_reasoning: key_quote에 투자근거 없음: "API가 야 너무 많이 올랐어. 두 달 정도 조정받다가 새롭게 요번 주에 역사 주신 거를 돌파했거든요"
- [90524688-c8f2-4640-9614-61f79ec3ce58] stock_not_mentioned_in_quote: key_quote에 종목명(HCM파마) 미포함: "제가 창업한 회사가 하나 있거든요. H파마예요. 글로벌 미생물 신약 기업이 될 수 있는 데이터들을 갖고 있어요"
- [90524688-c8f2-4640-9614-61f79ec3ce58] no_investment_reasoning: key_quote에 투자근거 없음: "제가 창업한 회사가 하나 있거든요. H파마예요. 글로벌 미생물 신약 기업이 될 수 있는 데이터들을 갖고 있어요"
- [90831b68-b73e-4f53-b215-ffca476fc46e] stock_not_mentioned_in_quote: key_quote에 종목명(원익IPS) 미포함: "원익 IPS 테스 유진테크 뭐 두산 테스나 뭐 하나 마이크론 뭐 이런 회사들도 여전히 업사이드가 있다고 보고 있습니다"
- [90831b68-b73e-4f53-b215-ffca476fc46e] no_investment_reasoning: key_quote에 투자근거 없음: "원익 IPS 테스 유진테크 뭐 두산 테스나 뭐 하나 마이크론 뭐 이런 회사들도 여전히 업사이드가 있다고 보고 있습니다"
- [997ba1c8-40cc-4255-a8f5-7a8ccd001b5e] stock_not_mentioned_in_quote: key_quote에 종목명(효성중공업) 미포함: "올해도 계속 한다... 효중이 대장으로 치고 나갈 가능성이 매우 크다"
- [997ba1c8-40cc-4255-a8f5-7a8ccd001b5e] no_investment_reasoning: key_quote에 투자근거 없음: "올해도 계속 한다... 효중이 대장으로 치고 나갈 가능성이 매우 크다"
- [999ac2a9-60b3-42e6-8b24-f3ef97a36eb1] stock_not_mentioned_in_quote: key_quote에 종목명(HD현대일렉트릭) 미포함: "HD 현대력도 모멘텀에 뭐가 있냐면 올해 드디어 유럽의 수주를 선점"
- [999ac2a9-60b3-42e6-8b24-f3ef97a36eb1] no_investment_reasoning: key_quote에 투자근거 없음: "HD 현대력도 모멘텀에 뭐가 있냐면 올해 드디어 유럽의 수주를 선점"
- [9aeda838-cd78-49c4-afe0-779fe6924305] stock_not_mentioned_in_quote: key_quote에 종목명(바이오 AI 기업) 미포함: "결국에이 바이오 쪽은 뭐 AI 인공지능과 엮겨 가지고 잘 될 거라고"
- [9aeda838-cd78-49c4-afe0-779fe6924305] no_investment_reasoning: key_quote에 투자근거 없음: "결국에이 바이오 쪽은 뭐 AI 인공지능과 엮겨 가지고 잘 될 거라고"
- [9c83cb42-6d31-4a9a-9b1c-5a85c125b84d] key_quote_too_short: key_quote가 20자 미만 (현재 12자): "둘 다 사는게 좋습니다"
- [9c83cb42-6d31-4a9a-9b1c-5a85c125b84d] stock_not_mentioned_in_quote: key_quote에 종목명(SK하이닉스) 미포함: "둘 다 사는게 좋습니다"
- [9c83cb42-6d31-4a9a-9b1c-5a85c125b84d] no_investment_reasoning: key_quote에 투자근거 없음: "둘 다 사는게 좋습니다"
- [9d79c0a4-7e2a-4852-b303-b24f05a980fd] stock_not_mentioned_in_quote: key_quote에 종목명(현대차그룹주) 미포함: "올해는 저는 피지컬 AI 해라고 보고 있기 때문에 로봇과 자율주쟁이 두 가지 축이 가장 크다고 보고요. 어 그 두 가지 축에서 현대차 그룹주가 일순이"
- [a9338662-af28-46b7-ac82-84e475646007] stock_not_mentioned_in_quote: key_quote에 종목명(엔비디아) 미포함: "주가는 70% 이상 반영을 하고서 움직였을 가능성이 있다. 새로운게 나와야 된다. 실적이 아니라 새로운 모멘텀을 기다리는 부분"
- [b5ab47f3-aa0c-4584-8a87-41a53aacb0be] stock_not_mentioned_in_quote: key_quote에 종목명(NC소프트) 미포함: "홀딩하셔도 되겠다. YoY 2142% 성장 예상... 바닥에서 야금야금 올라가는 이유가 설명"
- [b97347cb-f51c-4180-9717-e11ebc8cccef] stock_not_mentioned_in_quote: key_quote에 종목명(현대건설) 미포함: "SMR은 올해 가장 강력한 섹터가 될 것입니다"
- [b97347cb-f51c-4180-9717-e11ebc8cccef] no_investment_reasoning: key_quote에 투자근거 없음: "SMR은 올해 가장 강력한 섹터가 될 것입니다"
- [bac042bc-8a78-4397-ab71-ba1755fc3d79] stock_not_mentioned_in_quote: key_quote에 종목명(조선) 미포함: "아직 식지 않은 기대감. 단순 하청이 아닌 안보 파트너로 격상"
- [bb6deb68-005b-489c-9302-1ac7cd050453] stock_not_mentioned_in_quote: key_quote에 종목명(한국금융지주) 미포함: "한국 금융 지주랑 키움 증권을 추천드리고 있는데요... 지난해도 연간 2조원 순익 달성"
- [be863b24-d232-45ff-a6ec-7d5d79e77cfe] stock_not_mentioned_in_quote: key_quote에 종목명(비트코인) 미포함: "저는 막 급락이라고 보진 않고 5년 동안 오른 게 훨씬 많죠. 그걸 좀 일단은 되돌린 게 아닌가"
- [bf5c5e09-5518-466d-bf4d-4655a92e4548] key_quote_too_short: key_quote가 20자 미만 (현재 19자): "마이크로온도 사시는 것도 괜찮습니다"
- [bf5c5e09-5518-466d-bf4d-4655a92e4548] stock_not_mentioned_in_quote: key_quote에 종목명(마이크론) 미포함: "마이크로온도 사시는 것도 괜찮습니다"
- [bf5c5e09-5518-466d-bf4d-4655a92e4548] no_investment_reasoning: key_quote에 투자근거 없음: "마이크로온도 사시는 것도 괜찮습니다"
- [c250cb34-04cb-4174-9843-8c069f731271] no_investment_reasoning: key_quote에 투자근거 없음: "SK하이닉스는 156만 원으로 상향을 하죠"
- [c5d155e7-b7da-4127-90a5-02e4cd45c8f7] stock_not_mentioned_in_quote: key_quote에 종목명(SK하이닉스) 미포함: "삼성은 계속 올라갑니다 SK는 계속 떨어지고"
- [c5d155e7-b7da-4127-90a5-02e4cd45c8f7] no_investment_reasoning: key_quote에 투자근거 없음: "삼성은 계속 올라갑니다 SK는 계속 떨어지고"
- [c5ddfab8-d29f-428c-aaab-568aff7db603] stock_not_mentioned_in_quote: key_quote에 종목명(SK하이닉스) 미포함: "하나증권 112만원, 유안타 106만6천원, 유진투자 99만원, 한투 96만원. 영업이익 전망 모두 110조 이상"
- [c6df1cd3-246d-40b7-850b-cb0a8d624a65] stock_not_mentioned_in_quote: key_quote에 종목명(아이덴) 미포함: "5달러에서 한 78달러까지 갔다가... 몇 년은 제가 보유를 하거든요"
- [c84d8705-85ea-4cb7-b91a-d9fb54db86ac] stock_not_mentioned_in_quote: key_quote에 종목명(구글(알파벳)) 미포함: "구글이 빅테크 안에서는 해치펀드들이 선호하는 종목으로 뽑히고 있다"
- [c9d04f21-5570-4d15-b01f-0d8d06412b7b] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "20만 원은 전 출발점이 아닐까라고 말씀을 드리고 싶습니다"
- [c9d04f21-5570-4d15-b01f-0d8d06412b7b] no_investment_reasoning: key_quote에 투자근거 없음: "20만 원은 전 출발점이 아닐까라고 말씀을 드리고 싶습니다"
- [d1363829-ca81-472e-9813-630140a95799] no_investment_reasoning: key_quote에 투자근거 없음: "국내에서도 원익IPS 테스 유진테크 두산테스나 하나마이크론 이런 회사들도 여전히 업사이드가 있다고 보고 있습니다"
- [d155bb53-c292-48f0-818a-1f25f5b43fe9] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "KB증권 20만원, 키움증권 20만원, 미래에셋 18만7천원. 영업이익 전망 최고 170조"
- [dc359487-49ef-42ce-ba2c-297b1587e743] stock_not_mentioned_in_quote: key_quote에 종목명(CGV) 미포함: "정부의 구독형 영화패스 제도와 프랑스 성공사례를 통해 영화관 산업 회복 가능성"
- [dc359487-49ef-42ce-ba2c-297b1587e743] no_investment_reasoning: key_quote에 투자근거 없음: "정부의 구독형 영화패스 제도와 프랑스 성공사례를 통해 영화관 산업 회복 가능성"
- [dd2bbc57-c6ed-4168-b84a-305e0b832e7f] stock_not_mentioned_in_quote: key_quote에 종목명(2차전지 관련 기업) 미포함: "저는 약간 조심스러워요. 그니까 단기적으로 수를 뭐 받는다고 얘기 하는데예. 그게 언제 무너질지 모른다는 거예요"
- [dd2bbc57-c6ed-4168-b84a-305e0b832e7f] no_investment_reasoning: key_quote에 투자근거 없음: "저는 약간 조심스러워요. 그니까 단기적으로 수를 뭐 받는다고 얘기 하는데예. 그게 언제 무너질지 모른다는 거예요"
- [dfa9fdbc-5485-4a48-a007-14dab596ab31] stock_not_mentioned_in_quote: key_quote에 종목명(엔비디아) 미포함: "갖고 계신 분면 그냥 갖고 계시면 되고요. 안 갖고 계신 분이라면 2%면 들어가도 괜찮을 것 같아"
- [dfa9fdbc-5485-4a48-a007-14dab596ab31] no_investment_reasoning: key_quote에 투자근거 없음: "갖고 계신 분면 그냥 갖고 계시면 되고요. 안 갖고 계신 분이라면 2%면 들어가도 괜찮을 것 같아"
- [e1d58ec7-3ca7-4db9-9a77-d63cf1c06e89] stock_not_mentioned_in_quote: key_quote에 종목명(SOXX) 미포함: "SOSX라고 하는 ETF가 있으니까 반도체 ETF거든요. 이런 ETF 쪽에 30% 정도 투자하게 되면 어렵지 않게 수익을 낼 수 있지 않을까"
- [e33133c1-cd42-4a51-975e-f092c50f3f46] no_investment_reasoning: key_quote에 투자근거 없음: "반도체 빅테크 그리고 나스닥은 시간이 흐르면 결국은 올라갈 수밖에 없다고 생각합니다. 왜냐면 이게 세상의 흐름을 끌고 가는 그 핵에 놓여 있는 거거든요"
- [e82826f9-e9c9-49c5-8529-57df230d3016] stock_not_mentioned_in_quote: key_quote에 종목명(SK하이닉스) 미포함: "지금은 메모리 3사가 굉장히 제일 높은 확률로 업사이드가 남아 있다라고 봐야 되고요"
- [e82826f9-e9c9-49c5-8529-57df230d3016] no_investment_reasoning: key_quote에 투자근거 없음: "지금은 메모리 3사가 굉장히 제일 높은 확률로 업사이드가 남아 있다라고 봐야 되고요"
- [ec80bdec-b73c-4d5f-905f-3fada26fd361] no_investment_reasoning: key_quote에 투자근거 없음: "마이크론도 사시는 것도 괜찮습니다. 미국에 상장돼 있다라는 프리미엄을 무시 못 하거든요"
- [f13c9ca0-d899-4bb3-9c61-849503831329] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "비중이 없는 분은 지금이라도 물리더라도 들어가야 된다... 바라보지만 말고 일단 포지션을 넣고 거기서 대응을 해야 된다"
- [f13c9ca0-d899-4bb3-9c61-849503831329] no_investment_reasoning: key_quote에 투자근거 없음: "비중이 없는 분은 지금이라도 물리더라도 들어가야 된다... 바라보지만 말고 일단 포지션을 넣고 거기서 대응을 해야 된다"
- [f3ecfcd0-fc26-4606-989f-9c4fab5b2f3b] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "영업이익 43조에서 201조. 이익이 다섯배 늘어난 회사는 본 적이 없어요"
- [f614c684-8fc0-4c7d-a121-8073bee99b09] no_investment_reasoning: key_quote에 투자근거 없음: "SMR 1등 기업은 현대건설. 놓치지 마시고 분할로라도 공략해 보시면 좋을 것 같습니다"
- [f6d397de-1c5d-47f3-bf75-02abc2f3e8f4] stock_not_mentioned_in_quote: key_quote에 종목명(AI 인프라 섹터) 미포함: "AI 인프라 업체들은 계속해서 이런 경쟁 속에서 수혜가 이어질 수밖에 없다. GPU라든가 메모리라든가 전력"
- [fc445820-5853-4152-bca2-db6eacb10003] no_investment_reasoning: key_quote에 투자근거 없음: "하이닉스 멀티플 다섯배. 이게 말이 돼? 글로벌 3위 진입 가능성"
- [fd197edb-e670-46c0-ac68-1626c26e129e] no_investment_reasoning: key_quote에 투자근거 없음: "소재단은 꼭 하나 정도는 들고 가셨으면 좋겠습니다. 솔브레인 27년부터 본격화"
- [fd931214-1927-4c30-be65-fa6430d3f1bb] no_investment_reasoning: key_quote에 투자근거 없음: "생산을 하기 위해서는 장비가 필요한데 가장 핵심이 레이저입니다. ASML입니다"
- [ff39bd30-09b5-40cc-b8d2-413ff2b32138] no_investment_reasoning: key_quote에 투자근거 없음: "생산을 하기 위해서는 장비가 필요한데 그 장비 중에 가장 핵심이 레이저입니다. 이거 ASML입니다"
- [ffa1dc33-167c-4ea8-9691-5f8aa1bf1f4c] key_quote_too_short: key_quote가 20자 미만 (현재 12자): "둘 다 사는게 좋습니다"
- [ffa1dc33-167c-4ea8-9691-5f8aa1bf1f4c] stock_not_mentioned_in_quote: key_quote에 종목명(삼성전자) 미포함: "둘 다 사는게 좋습니다"
- [ffa1dc33-167c-4ea8-9691-5f8aa1bf1f4c] no_investment_reasoning: key_quote에 투자근거 없음: "둘 다 사는게 좋습니다"

### 2. 시그널 분류 이슈 (9건)
- [146207b1-702e-44a5-8d7f-026bf6181cbb] forecast_classified_as_signal: 전망성 발언을 시그널로 분류: "엔터조에서 대장은 하이브인데 저는 근데 하이브는 조금 좋게 말씀드리고 싶은 이유가 뭐냐면 역사 신고가 근처예요. 근데 이제 근처인데 어 BTS가 너무 기대되기 때문입니다"
- [55bf5a77-ff14-4c2b-9da8-a15c7a94ea74] forecast_classified_as_signal: 전망성 발언을 시그널로 분류: "모건 스탠리 2027년 삼성전자 영업이익 전세계 1등. 340조원. 2027 포워드 PE 네배밖에 안 돼. 삼성전자는 계속 가도 전혀 이상하지 않은"
- [6ab0f37a-1bac-4010-988a-f14db3e2b1e8] forecast_classified_as_signal: 전망성 발언을 시그널로 분류: "키움 증권 같은 경우에도 전년 대비 순익이 20% 성장할 것으로 예상"
- [7ed86fea-e0bb-4604-b0c1-3ba7788966c1] forecast_classified_as_signal: 전망성 발언을 시그널로 분류: "우선순은 메모리... 하이닉 삼성전자, 샌디스크, 마이크론 넷 중에 하나는 갖고 있어야지"
- [997ba1c8-40cc-4255-a8f5-7a8ccd001b5e] forecast_classified_as_signal: 전망성 발언을 시그널로 분류: "올해도 계속 한다... 효중이 대장으로 치고 나갈 가능성이 매우 크다"
- [b5ab47f3-aa0c-4584-8a87-41a53aacb0be] education_classified_as_signal: 교육성 내용을 시그널로 분류: "홀딩하셔도 되겠다. YoY 2142% 성장 예상... 바닥에서 야금야금 올라가는 이유가 설명"
- [c5d155e7-b7da-4127-90a5-02e4cd45c8f7] education_classified_as_signal: 교육성 내용을 시그널로 분류: "삼성은 계속 올라갑니다 SK는 계속 떨어지고"
- [e82826f9-e9c9-49c5-8529-57df230d3016] forecast_classified_as_signal: 전망성 발언을 시그널로 분류: "지금은 메모리 3사가 굉장히 제일 높은 확률로 업사이드가 남아 있다라고 봐야 되고요"
- [f13c9ca0-d899-4bb3-9c61-849503831329] education_classified_as_signal: 교육성 내용을 시그널로 분류: "비중이 없는 분은 지금이라도 물리더라도 들어가야 된다... 바라보지만 말고 일단 포지션을 넣고 거기서 대응을 해야 된다"

### 3. 화자 귀속 이슈 (0건)

### 4. 중복 시그널 (20건)
- [0f3c3f27-ddb4-4dec-a16d-7f28163db5f1] duplicate_signal: 중복 시그널 (영상=1a47ae36-c840-4831-9ece-ec88ba5fc7ec, 종목=삼성전자, 화자=이효석)
- [764703cc-157e-46fe-b265-f2253a1d66ba] duplicate_signal: 중복 시그널 (영상=1a47ae36-c840-4831-9ece-ec88ba5fc7ec, 종목=삼성전자, 화자=이효석)
- [163d4529-4871-4f34-ac74-271407952cd6] duplicate_signal: 중복 시그널 (영상=1a47ae36-c840-4831-9ece-ec88ba5fc7ec, 종목=SK하이닉스, 화자=이효석)
- [1cda9f77-c6cf-43b6-83be-6542e9930f58] duplicate_signal: 중복 시그널 (영상=1a47ae36-c840-4831-9ece-ec88ba5fc7ec, 종목=SK하이닉스, 화자=이효석)
- [22e38f2b-be73-44cb-864d-febe8c81353c] duplicate_signal: 중복 시그널 (영상=d68ab7a3-4772-49fe-86f2-eead4f4d1887, 종목=SK하이닉스, 화자=조진표)
- [c250cb34-04cb-4174-9843-8c069f731271] duplicate_signal: 중복 시그널 (영상=d68ab7a3-4772-49fe-86f2-eead4f4d1887, 종목=SK하이닉스, 화자=조진표)
- [63208f63-4c0a-4625-b6b7-48fd75451f29] duplicate_signal: 중복 시그널 (영상=d68ab7a3-4772-49fe-86f2-eead4f4d1887, 종목=삼성전자, 화자=조진표)
- [7ba0f471-6950-4436-8e8f-2ee5989748ce] duplicate_signal: 중복 시그널 (영상=d68ab7a3-4772-49fe-86f2-eead4f4d1887, 종목=삼성전자, 화자=조진표)
- [7a6e30a3-db8d-42a4-8b62-33b554469e95] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=삼성전자, 화자=이영수)
- [ffa1dc33-167c-4ea8-9691-5f8aa1bf1f4c] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=삼성전자, 화자=이영수)
- [90831b68-b73e-4f53-b215-ffca476fc46e] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=원익IPS, 화자=이영수)
- [d1363829-ca81-472e-9813-630140a95799] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=원익IPS, 화자=이영수)
- [9c83cb42-6d31-4a9a-9b1c-5a85c125b84d] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=SK하이닉스, 화자=이영수)
- [e82826f9-e9c9-49c5-8529-57df230d3016] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=SK하이닉스, 화자=이영수)
- [b97347cb-f51c-4180-9717-e11ebc8cccef] duplicate_signal: 중복 시그널 (영상=93c60878-e2d3-4bc2-bcd2-4d32d0a3bd2c, 종목=현대건설, 화자=달란트투자)
- [f614c684-8fc0-4c7d-a121-8073bee99b09] duplicate_signal: 중복 시그널 (영상=93c60878-e2d3-4bc2-bcd2-4d32d0a3bd2c, 종목=현대건설, 화자=달란트투자)
- [bf5c5e09-5518-466d-bf4d-4655a92e4548] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=마이크론, 화자=이영수)
- [ec80bdec-b73c-4d5f-905f-3fada26fd361] duplicate_signal: 중복 시그널 (영상=cef2c937-db77-4bf6-9173-2e3fd8533334, 종목=마이크론, 화자=이영수)
- [fd931214-1927-4c30-be65-fa6430d3f1bb] duplicate_signal: 중복 시그널 (영상=8bc8b1e0-aea1-4a66-8e7f-4efc9a3f9a34, 종목=ASML, 화자=배재규)
- [ff39bd30-09b5-40cc-b8d2-413ff2b32138] duplicate_signal: 중복 시그널 (영상=8bc8b1e0-aea1-4a66-8e7f-4efc9a3f9a34, 종목=ASML, 화자=배재규)

### 5. confidence 적용 이슈 (2건)
- [2bb7d896-a03c-4413-ac3e-9717c59b9090] conditional_with_high_confidence: 조건부 발언인데 confidence medium: "대한민국 장비주에서 한미반도체나 원익IPS 같은 이런 종목군들 매수하시게 된다라면 어렵지 않을 것 같고요"
- [dfa9fdbc-5485-4a48-a007-14dab596ab31] conditional_with_high_confidence: 조건부 발언인데 confidence high: "갖고 계신 분면 그냥 갖고 계시면 되고요. 안 갖고 계신 분이라면 2%면 들어가도 괜찮을 것 같아"

### 6. 기타 이슈 (0건)

## 패턴 분석
- key_quote 너무 짧음: 4건
- 종목명 미포함: 53건
- 투자근거 없음: 56건
