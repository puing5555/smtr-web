const fs = require('fs');
const path = require('path');

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const headers = {
  'apikey': KEY,
  'Authorization': `Bearer ${KEY}`,
  'Content-Type': 'application/json',
  'Prefer': 'return=minimal'
};

// New summaries for videos with placeholder summaries
const summaries = {
  'R6w3T3eUVIs': '배제원 PV가 엔비디아 실적 발표 이후 반도체 및 코스피 전망을 분석했다. 엔비디아 실적이 양호하게 발표되면서 AI 거품론에 따른 반도체 조정 우려가 해소되었고, 빅테크들의 케펙스 지출 지속과 AI 에이전트 매출 기대감이 긍정적이라고 평가. 코스피 6,000포인트 돌파가 현재 이익 수준만으로도 설명 가능하며 추가 상승세가 이어질 것이라는 전망을 제시했다.',
  
  'XFHD_1M3Mxg': 'NH투자증권 김동훈 대리가 인바운드 관광 증가와 원화 약세를 바탕으로 백화점 업종, 특히 신세계 주식을 분석했다. 중일 외교 갈등으로 중국인 일본 관광이 61% 감소하면서 한국이 반사이익을 받고 있으며, 외국인 관광객이 코로나 이전 수준을 회복한 상황. 신세계를 최선호주로 제시하며 인바운드 확대에 따른 백화점 실적 개선을 전망했다.',
  
  'x0TKvrIdIwI': '박병창 이사가 코스피 6,300 돌파 상황에서 반도체와 비반도체 섹터를 분석했다. 삼성전자가 메타·AMD 공급계약 기대감으로 7.1% 상승하고 SK하이닉스가 오후 급등하며 7.9% 오른 장세를 해설. 삼성전자는 분량 여력이 있어 AMD MI460 수주에 유리하며, 코스피의 주봉 차트가 거의 쉼 없이 상승하는 강한 추세를 보이고 있다고 분석했다.',
  
  'I4Tt3tevuTU': '삼프로TV 클로징벨에서 박명석 앵커와 SK증권 이재규 차장이 코스피 6,300 돌파 시황을 분석했다. 코스피가 장중 6,313까지 상승하며 사상 최고치를 경신했고, 코스닥도 2% 넘게 상승. 2026년이 역사책에 남을 해가 될 것이라며, 매일 고가를 경신하는 전례 없는 상승장 속에서 투자 전략을 논의했다.',
  
  '8-hYd-8eojE': '장우진 작가가 현대차 그룹을 중심으로 시장 분석을 했다. 올해 36거래일 중 하락일이 7일뿐인 강한 상승장을 확인하며, 과거 코스피 4천대에서 7천 전망을 제시했던 것을 회고. 급등 이후 단기 조정 가능성을 언급하며 현금 20~30% 보유를 권고했으나, 상승장 자체에 대한 이견은 없다고 강조했다.',
  
  '-US4r1E1kOQ': '유니스토리자산운용 김장년 본부장이 엔비디아 실적 발표 직후 반도체·메모리 전망을 분석했다. 엔비디아 매출이 예상 대비 3~5% 상회했으나 서프라이즈 폭이 크지 않아 애프터마켓에서 2.25% 상승에 그쳤고, 가이던스는 중간값 기준 5~9% 상회. 컨퍼런스콜 내용과 데이터센터 매출 등 세부 지표를 확인해야 한다는 신중한 입장을 제시했다.',
  
  'ldT75QwBB6g': '삼프로TV 아침맨에서 박지훈 부장이 효성중공업 외 5종목을 분석했다. 코스피 6천 시대에 현대차 8%, 기아 12% 급등하며 반도체 외 자동차 섹터도 존재감을 드러낸 장세 해설. 너무 많이 오른 종목의 추격 매수보다 로테이션에 탑승할 종목 선별이 중요하다며, K증시의 체질 개선이 본격화되고 있다고 평가했다.',
  
  'irK0YCnox78': '김장열 본부장이 삼성전자의 배당 정책 변화 가능성을 분석했다. 삼성전자가 3월 18일 주총 직후 밸류업 공시를 할 것이라는 기사가 나왔고, 배당소득 분리과세 시행령 개정으로 배당 성향 25% 이상·전년 대비 10% 증가 시 세제 혜택이 가능해졌다. 삼성전자가 이에 해당하려면 배당을 최소 10% 이상 증가시킬 것으로 예상되며, 이것이 당일 7% 상승의 한 요인이라고 분석했다.',
  
  'qYAiv0Kljas': '삼프로TV 클로징벨에서 김장열 본부장과 이건희 대표가 코스피 6,000 돌파 시황을 분석했다. 코스피가 6,093선을 기록하며 사상 최초로 6천선을 넘어선 역사적 순간을 실시간으로 전했고, 현대차·현대건설·SK하이닉스 등 주요 종목의 동향을 논의했다.',
  
  'hxpOT8n_ICw': '고연수 연구원이 증권 섹터의 투자 매력을 분석했다. 증권 업종이 연초 대비 93% 상승하며 반도체를 뛰어넘는 수익률을 기록했고, 코스피 연간 영업이익이 588조원(전년 대비 95% 증가)에 달하는 상황에서도 PER 10배·PBR 1.7배로 중국보다 저평가되어 있다고 분석. 증시 우상향 시 브로커리지·투자평가이익 모두 성장 가능하여 증권주가 차기 주도주가 될 수 있다고 전망했다.',
  
  '_MrBnIb0jOk': '달란트투자에서 현재 AI 투자가 닷컴버블과 근본적으로 다르다고 주장했다. AI가 100배~1000배 개선을 가져오는 상황에서 미국 관세 10~20% 증가는 의미가 없으며, 1차 15배 점핑이 올해 상반기에 나올 것이라고 전망. 최전단에 있는 4개 핵심 기업을 기억해야 한다고 강조했다.',
  
  'kFa9RxL4HnA': '달란트투자에서 반도체 3사(삼성전자·SK하이닉스·마이크론)의 주도권 변화를 분석했다. HBM 수요가 구하지 못할 정도로 폭증하면서 판매자 우위 시장이 형성되었고, SK하이닉스는 12나노 공정으로 엔비디아에 유리한 위치를 확보. 삼성전자는 계속 상승하고 SK하이닉스는 조정 후 역전할 가능성이 있다는 전망을 제시했다.',
  
  'B5owNUs_DFw': '이효석아카데미 8주차 쇼미더연수에서 미국 증시 현황과 AI 투자 트렌드 변화를 분석했다. S&P500은 9월 이후 10% 박스권에 갇혀 있으며, 소프트웨어 종목들이 크게 하락한 반면 반도체장비·구리·건설기계 등 중후장대 산업이 상위 섹터로 부상. 13F 공시에서 버크셔의 포트폴리오 변화, EWY(한국 ETF) 매수세를 확인했고, 중국 AI 모델(QWen3.5, 딥시크2.0 등)의 API 가격이 6개월 만에 급락하며 AI 인프라 투자와 실제 AI 활용 사이의 격차가 좁혀지고 있다고 분석했다.'
};

// Music/intro videos - skip summary update
const musicOnly = ['xtl0nnxAYKc', 'rpoGBOJZ2fk', 'B2ARIKugV-k'];

const dir = 'C:/Users/Mario/work/subs';
const files = fs.readdirSync(dir).filter(f => f.endsWith('_fulltext.txt'));

// DB video IDs (from query result)
const dbVideoIds = new Set([
  'Xv-wNA91EPE','R6w3T3eUVIs','XFHD_1M3Mxg','x0TKvrIdIwI','I4Tt3tevuTU',
  '8-hYd-8eojE','XveVkr3JHs4','8Nn3qerCt44','BVRoApF0c8k','CFY_pEYLpaU',
  'f3XyT2v2WVc','lfsT3hO1GqQ','nwuAhWEoAng','vVurVxsXvoM','zh2ucctO00c',
  '4QlLhzLfhzU','_MrBnIb0jOk','xtl0nnxAYKc','rpoGBOJZ2fk','B2ARIKugV-k',
  'kFa9RxL4HnA','tSXkj2Omz34','fDZnPoK5lyc','5mvn3PfKf9Y','bmXgryWXNrw',
  'g19QLu5tZlo','wPKfa2qWh4U','B5owNUs_DFw','ZXuQCpuVCYc','nm5zQxZSkbk',
  'N7xO-UWCM5w','-US4r1E1kOQ','ldT75QwBB6g','irK0YCnox78','qYAiv0Kljas',
  'hxpOT8n_ICw'
]);

async function updateVideo(videoId, data) {
  const url = `${SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.${encodeURIComponent(videoId)}`;
  const res = await fetch(url, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed ${videoId}: ${res.status} ${text}`);
  }
  return true;
}

async function main() {
  let updated = 0;
  let skipped = 0;
  let summaryUpdated = 0;
  let subtitleUpdated = 0;
  
  for (const file of files) {
    const noSuffix = file.replace('_fulltext.txt', '');
    const idx = noSuffix.indexOf('_');
    const videoId = noSuffix.substring(idx + 1);
    
    if (!dbVideoIds.has(videoId)) {
      console.log(`SKIP (not in DB): ${videoId}`);
      skipped++;
      continue;
    }
    
    const text = fs.readFileSync(path.join(dir, file), 'utf8');
    const subtitleText = text.substring(0, 5000);
    
    const data = { subtitle_text: subtitleText };
    
    if (summaries[videoId]) {
      data.video_summary = summaries[videoId];
      summaryUpdated++;
    }
    
    try {
      await updateVideo(videoId, data);
      updated++;
      subtitleUpdated++;
      const tag = summaries[videoId] ? ' +SUMMARY' : '';
      console.log(`OK: ${videoId}${tag}`);
    } catch (e) {
      console.error(e.message);
    }
  }
  
  console.log(`\n=== RESULTS ===`);
  console.log(`Total files: ${files.length}`);
  console.log(`Updated: ${updated}`);
  console.log(`Summaries updated: ${summaryUpdated}`);
  console.log(`Subtitle text updated: ${subtitleUpdated}`);
  console.log(`Skipped (not in DB): ${skipped}`);
}

main();
