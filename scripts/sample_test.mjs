// sample_test.mjs
// 샘플 데이터로 청킹 기능 테스트

import { processSubtitleChunks, processSubtitleTruncated } from './subtitle_chunker.mjs';
import fs from 'fs/promises';

console.log('=== 샘플 데이터로 청킹 테스트 ===');

// 긴 샘플 자막 생성 (50K+ 자)
function generateLongSubtitle() {
  const baseTexts = [
    "안녕하세요. 오늘은 삼성전자에 대해 분석해보겠습니다. 삼성전자는 현재 반도체 사이클 회복으로 매우 좋은 모습을 보이고 있습니다. 실적이 크게 개선되고 있어서 지금이 매수 타이밍이라고 봅니다.",
    "다음으로는 SK하이닉스를 살펴보겠습니다. SK하이닉스도 메모리 반도체 업황 개선으로 전망이 밝습니다. HBM 수요 증가로 실적 성장이 기대되는 종목입니다. 관심 가져보시기 바랍니다.",
    "LG에너지솔루션에 대해서도 말씀드리겠습니다. 전기차 시장 성장으로 배터리 수요가 급증하고 있습니다. 북미 공장 가동률 상승으로 수익성이 개선되고 있어서 긍정적으로 평가합니다.",
    "카카오는 좀 조심스럽게 봐야 할 것 같습니다. 규제 이슈와 성장 둔화 우려가 있어서 단기적으로는 부정적입니다. 추가 하락 위험도 있으니 주의하시기 바랍니다.",
    "네이버의 경우는 AI 관련 사업이 주목받고 있습니다. 하지만 경쟁이 치열해서 수익성 개선까지는 시간이 걸릴 것으로 보입니다. 중립적으로 지켜봐야 할 종목입니다.",
    "현대차는 전기차 전환이 가속화되면서 새로운 성장 동력을 확보하고 있습니다. 제네시스 브랜드도 성공적으로 자리잡고 있어서 장기적으로 긍정적입니다.",
    "포스코홀딩스는 철강 업황 회복으로 실적이 개선되고 있습니다. 2차전지 소재 사업도 본격화되면서 새로운 수익원이 생기고 있습니다. 매수 추천드립니다.",
    "셀트리온은 바이오시밀러 시장에서 독보적인 지위를 유지하고 있습니다. 신약 개발도 순조롭게 진행되고 있어서 중장기 성장이 기대됩니다.",
    "한국전력은 전력요금 정상화와 원전 재가동으로 실적 개선이 예상됩니다. 하지만 여전히 부채 부담이 크므로 리스크 관리가 중요합니다.",
    "KB금융그룹은 금리 상승으로 순이자마진이 개선되고 있습니다. 부동산 PF 리스크는 있지만 충당금을 충분히 쌓아둔 상태라서 큰 문제는 없을 것 같습니다."
  ];
  
  let longText = "";
  
  // 약 60K자 생성
  while (longText.length < 60000) {
    for (const text of baseTexts) {
      longText += text + " ";
      if (longText.length >= 60000) break;
    }
  }
  
  return longText;
}

// 샘플 영상 데이터
const sampleVideos = [
  {
    video_id: "sample001", 
    title: "[종목분석] 2024년 하반기 대장주 전망 - 삼성전자, SK하이닉스 중심으로",
    subtitle_text: generateLongSubtitle()
  },
  {
    video_id: "sample002",
    title: "배터리, 자동차 관련주 총정리 - LG에너지솔루션, 현대차 분석",
    subtitle_text: generateLongSubtitle().substring(0, 45000)
  }
];

async function runSampleTest() {
  console.log('샘플 테스트 시작...\n');
  
  const results = [];
  let totalCost = 0;
  
  for (let i = 0; i < sampleVideos.length; i++) {
    const video = sampleVideos[i];
    console.log(`\n[${ i + 1}/${sampleVideos.length}] ${video.title}`);
    console.log(`자막 길이: ${video.subtitle_text.length.toLocaleString()}자`);
    
    const testResult = {
      videoId: video.video_id,
      title: video.title,
      subtitleLength: video.subtitle_text.length,
      chunkResult: null,
      truncatedResult: null,
      comparison: {}
    };
    
    try {
      // Chunking 방식 테스트
      console.log('\n--- Chunking 방식 테스트 ---');
      const chunkResult = await processSubtitleChunks(
        video.subtitle_text, 
        video.title,
        { verbose: true }
      );
      testResult.chunkResult = chunkResult;
      totalCost += chunkResult.estimatedCost;
      
      // Truncation 방식 테스트  
      console.log('\n--- Truncation 방식 테스트 ---');
      const truncatedResult = await processSubtitleTruncated(
        video.subtitle_text,
        video.title
      );
      testResult.truncatedResult = truncatedResult;
      totalCost += truncatedResult.estimatedCost;
      
      // 비교 분석
      testResult.comparison = {
        chunkSignals: chunkResult.mergedSignals.length,
        truncatedSignals: truncatedResult.signals.length,
        signalDifference: chunkResult.mergedSignals.length - truncatedResult.signals.length,
        chunkCost: chunkResult.estimatedCost,
        truncatedCost: truncatedResult.estimatedCost,
        costRatio: (chunkResult.estimatedCost / truncatedResult.estimatedCost).toFixed(2)
      };
      
      console.log('\n=== 비교 결과 ===');
      console.log(`청킹: ${testResult.comparison.chunkSignals}개 시그널`);
      console.log(`트렁케이션: ${testResult.comparison.truncatedSignals}개 시그널`);
      console.log(`시그널 차이: ${testResult.comparison.signalDifference > 0 ? '+' : ''}${testResult.comparison.signalDifference}`);
      console.log(`비용 비율: ${testResult.comparison.costRatio}배`);
      
    } catch (error) {
      console.error(`영상 ${i + 1} 처리 에러:`, error.message);
      testResult.error = error.message;
    }
    
    results.push(testResult);
    
    // 다음 영상 전 대기
    if (i < sampleVideos.length - 1) {
      console.log('\n다음 영상 처리까지 5초 대기...');
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
  
  // 결과 보고서 생성
  await generateSampleReport(results, totalCost);
  
  console.log(`\n\n=== 샘플 테스트 완료 ===`);
  console.log(`총 비용: $${totalCost.toFixed(4)}`);
}

async function generateSampleReport(results, totalCost) {
  const reportPath = 'C:\\Users\\Mario\\work\\data\\research\\chunk_merge_test.md';
  
  let report = `# Chunk→Merge 방식 테스트 결과 (샘플 데이터)

## 테스트 개요
- **실행일**: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Bangkok' })}
- **테스트 영상**: ${results.length}개 (샘플 데이터)
- **총 비용**: $${totalCost.toFixed(4)}

## 전체 요약
`;

  const validResults = results.filter(r => !r.error);
  const totalChunkSignals = validResults.reduce((sum, r) => sum + (r.comparison?.chunkSignals || 0), 0);
  const totalTruncatedSignals = validResults.reduce((sum, r) => sum + (r.comparison?.truncatedSignals || 0), 0);
  const totalSignalDiff = totalChunkSignals - totalTruncatedSignals;

  report += `- **총 시그널 수** (청킹): ${totalChunkSignals}개
- **총 시그널 수** (트렁케이션): ${totalTruncatedSignals}개
- **시그널 증가**: ${totalSignalDiff > 0 ? '+' : ''}${totalSignalDiff}개

## 영상별 상세 결과

`;

  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    
    report += `### ${i + 1}. ${result.title}
- **Video ID**: ${result.videoId}
- **자막 길이**: ${result.subtitleLength.toLocaleString()}자

`;

    if (result.error) {
      report += `- **에러**: ${result.error}\n\n`;
      continue;
    }
    
    const chunk = result.chunkResult;
    const truncated = result.truncatedResult;
    const comp = result.comparison;
    
    report += `#### Chunking 결과
- **Chunks**: ${chunk.chunks}개
- **전체 시그널**: ${chunk.totalSignals}개
- **병합 후**: ${chunk.mergedSignals.length}개
- **비용**: $${chunk.estimatedCost.toFixed(4)}

#### Truncation 결과
- **시그널**: ${truncated.signals.length}개
- **잘린 길이**: ${truncated.truncatedLength.toLocaleString()}자
- **비용**: $${truncated.estimatedCost.toFixed(4)}

#### 비교
- **시그널 차이**: ${comp.signalDifference > 0 ? '+' : ''}${comp.signalDifference}개
- **비용 증가**: ${comp.costRatio}배
- **개선 여부**: ${comp.signalDifference > 0 ? '✅ 개선' : comp.signalDifference === 0 ? '⚖️ 동일' : '❌ 감소'}

---

`;
  }

  report += `## 결론

${totalSignalDiff > 0 ? 
    `✅ **청킹 방식이 ${totalSignalDiff}개 시그널을 추가로 발견**했습니다.` :
    totalSignalDiff === 0 ?
    `⚖️ 두 방식의 시그널 발견 수가 동일합니다.` :
    `❌ 청킹 방식이 ${Math.abs(totalSignalDiff)}개 시그널을 적게 발견했습니다.`
}

샘플 데이터 테스트를 통해 청킹 방식의 기본 동작을 확인했습니다.
실제 데이터를 사용한 추가 테스트가 필요합니다.
`;

  await fs.writeFile(reportPath, report, 'utf-8');
  console.log(`\n보고서 생성됨: ${reportPath}`);
}

// 테스트 실행
runSampleTest().catch(console.error);