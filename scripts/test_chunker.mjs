// test_chunker.mjs
// subtitle_chunker 테스트 스크립트

import { createClient } from '@supabase/supabase-js';
import { processSubtitleChunks, processSubtitleTruncated } from './subtitle_chunker.mjs';
import fs from 'fs/promises';
import path from 'path';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

/**
 * 50K+ 자막을 가진 영상 5개 가져오기
 */
async function fetchLongSubtitleVideos() {
  console.log('Supabase에서 긴 자막 영상 검색 중...');
  
  const { data, error } = await supabase
    .from('youtube_videos') 
    .select('video_id, title, subtitle_text')
    .not('subtitle_text', 'is', null)
    .gte('char_length(subtitle_text)', 50000)
    .order('char_length(subtitle_text)', { ascending: false })
    .limit(5);
    
  if (error) {
    throw new Error(`Supabase 에러: ${error.message}`);
  }
  
  console.log(`${data.length}개 영상 발견`);
  return data;
}

/**
 * 테스트 실행 및 결과 비교
 */
async function runTest() {
  const startTime = Date.now();
  console.log('=== Chunk→Merge 테스트 시작 ===');
  
  try {
    // 1. 테스트 데이터 가져오기
    const videos = await fetchLongSubtitleVideos();
    
    if (videos.length === 0) {
      console.log('테스트할 영상이 없습니다.');
      return;
    }
    
    const results = [];
    let totalCost = 0;
    
    // 2. 각 영상 테스트
    for (let i = 0; i < videos.length; i++) {
      const video = videos[i];
      console.log(`\n\n[${ i + 1}/${videos.length}] ${video.title}`);
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
      
      // 다음 영상 전 잠시 대기
      if (i < videos.length - 1) {
        console.log('\n다음 영상 처리까지 5초 대기...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
    
    // 3. 전체 결과 분석
    const summary = analyzeTotalResults(results, totalCost);
    
    // 4. 보고서 생성
    await generateReport(results, summary, Date.now() - startTime);
    
    console.log(`\n\n=== 테스트 완료 ===`);
    console.log(`총 비용: $${totalCost.toFixed(4)}`);
    console.log(`실행 시간: ${Math.floor((Date.now() - startTime) / 1000)}초`);
    
  } catch (error) {
    console.error('테스트 실행 에러:', error.message);
  }
}

/**
 * 전체 결과 분석
 */
function analyzeTotalResults(results, totalCost) {
  const validResults = results.filter(r => !r.error);
  
  const totalChunkSignals = validResults.reduce((sum, r) => sum + (r.comparison?.chunkSignals || 0), 0);
  const totalTruncatedSignals = validResults.reduce((sum, r) => sum + (r.comparison?.truncatedSignals || 0), 0);
  const totalSignalDiff = totalChunkSignals - totalTruncatedSignals;
  
  const avgCostRatio = validResults.length > 0 
    ? validResults.reduce((sum, r) => sum + parseFloat(r.comparison?.costRatio || 0), 0) / validResults.length
    : 0;
    
  const improvedVideos = validResults.filter(r => (r.comparison?.signalDifference || 0) > 0).length;
  
  return {
    totalVideos: results.length,
    validResults: validResults.length,
    totalChunkSignals,
    totalTruncatedSignals,
    totalSignalDiff,
    avgCostRatio: avgCostRatio.toFixed(2),
    improvedVideos,
    improvementRate: validResults.length > 0 ? (improvedVideos / validResults.length * 100).toFixed(1) : 0,
    totalCost: totalCost.toFixed(4)
  };
}

/**
 * 마크다운 보고서 생성
 */
async function generateReport(results, summary, executionTime) {
  const reportPath = 'C:\\Users\\Mario\\work\\data\\research\\chunk_merge_test.md';
  
  let report = `# Chunk→Merge 방식 테스트 결과

## 테스트 개요
- **실행일**: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Bangkok' })}
- **테스트 영상**: ${summary.totalVideos}개 (유효: ${summary.validResults}개)
- **실행 시간**: ${Math.floor(executionTime / 1000)}초
- **총 비용**: $${summary.totalCost}

## 전체 요약
- **총 시그널 수** (청킹): ${summary.totalChunkSignals}개
- **총 시그널 수** (트렁케이션): ${summary.totalTruncatedSignals}개
- **시그널 증가**: ${summary.totalSignalDiff > 0 ? '+' : ''}${summary.totalSignalDiff}개
- **개선된 영상**: ${summary.improvedVideos}/${summary.validResults}개 (${summary.improvementRate}%)
- **평균 비용 증가**: ${summary.avgCostRatio}배

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
    
    report += `
#### Chunking 결과
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

#### 발견된 시그널
`;

    // 청킹 방식 시그널 표시
    if (chunk.mergedSignals.length > 0) {
      report += '**청킹 방식:**\n';
      chunk.mergedSignals.forEach(signal => {
        report += `- ${signal.stock} (${signal.ticker || 'N/A'}): **${signal.signal_type}** (conf: ${signal.confidence})\n`;
        report += `  - "${signal.key_quote}"\n`;
      });
      report += '\n';
    }
    
    // 트렁케이션 방식 시그널 표시
    if (truncated.signals.length > 0) {
      report += '**트렁케이션 방식:**\n';
      truncated.signals.forEach(signal => {
        report += `- ${signal.stock} (${signal.ticker || 'N/A'}): **${signal.signal_type}** (conf: ${signal.confidence})\n`;
        report += `  - "${signal.key_quote}"\n`;
      });
    }
    
    report += '\n---\n\n';
  }

  report += `## 결론

${summary.totalSignalDiff > 0 ? 
  `✅ **청킹 방식이 ${summary.totalSignalDiff}개 시그널을 추가로 발견**했습니다.` :
  summary.totalSignalDiff === 0 ?
  `⚖️ 두 방식의 시그널 발견 수가 동일합니다.` :
  `❌ 청킹 방식이 ${Math.abs(summary.totalSignalDiff)}개 시그널을 적게 발견했습니다.`
}

- ${summary.improvedVideos}/${summary.validResults}개 영상에서 청킹 방식이 더 많은 시그널을 발견
- 평균 비용 증가: ${summary.avgCostRatio}배
- 긴 영상에서 시그널 누락 방지 효과 ${summary.improvedVideos > 0 ? '확인' : '미확인'}

**권장사항**: ${summary.totalSignalDiff > 0 ? 
  '청킹 방식 도입을 통해 긴 영상에서 시그널 누락을 방지할 수 있습니다.' :
  '추가 테스트를 통해 청킹 방식의 효과를 재검증이 필요합니다.'
}
`;

  await fs.writeFile(reportPath, report, 'utf-8');
  console.log(`\n보고서 생성됨: ${reportPath}`);
}

// 테스트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  runTest().catch(console.error);
}

export { runTest, fetchLongSubtitleVideos };