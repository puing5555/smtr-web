import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 환경 설정
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_API_KEY = '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';
const MODEL = 'claude-sonnet-4-20250514';
const TELEGRAM_GROUP_ID = '-1003764256213';
const JAY_DM_ID = '6578282080';

// Supabase 클라이언트 초기화
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// V11 프롬프트 읽기
const V11_PROMPT_PATH = 'C:\\Users\\Mario\\work\\invest-sns\\prompts\\pipeline_v11.md';
const v11Prompt = fs.readFileSync(V11_PROMPT_PATH, 'utf-8');

// 글로벌 상태
let totalCost = 0;
let processedCount = 0;
let results = [];

// 시그널 매핑
const signalTypeMap = {
  'STRONG_BUY': '매수',
  'BUY': '긍정', 
  'HOLD': '중립',
  'SELL': '부정',
  'STRONG_SELL': '매도',
  'CAUTION': '부정',
  'NEGATIVE': '부정',
  'POSITIVE': '긍정',
  'NEUTRAL': '중립',
  '매수': '매수',
  '긍정': '긍정',
  '중립': '중립', 
  '부정': '부정',
  '매도': '매도'
};

// 딜레이 함수
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Anthropic API 호출
async function callAnthropicAPI(content, retries = 3) {
  const truncatedContent = content.length > 8000 ? content.substring(0, 8000) + '...' : content;
  
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: 4000,
          system: v11Prompt,
          messages: [
            {
              role: 'user', 
              content: `다음 영상 자막을 분석해서 투자 시그널을 추출해주세요:\n\n${truncatedContent}`
            }
          ]
        })
      });

      if (response.status === 429) {
        console.log(`Rate limit hit, waiting 60 seconds... (attempt ${i + 1}/${retries})`);
        await delay(60000);
        continue;
      }

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // 비용 계산 (대략적)
      const inputTokens = Math.ceil(truncatedContent.length / 4);
      const outputTokens = Math.ceil(data.content[0].text.length / 4);
      const cost = (inputTokens * 0.003 + outputTokens * 0.015) / 1000; // USD per 1K tokens 추정
      totalCost += cost;

      return {
        content: data.content[0].text,
        cost: cost
      };

    } catch (error) {
      console.error(`API call attempt ${i + 1} failed:`, error.message);
      if (i === retries - 1) throw error;
      await delay(5000);
    }
  }
}

// 시그널 파싱
function parseSignals(responseText) {
  try {
    // JSON 부분 추출
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) return [];
    
    const parsed = JSON.parse(jsonMatch[0]);
    return parsed.signals || [];
  } catch (error) {
    console.error('Failed to parse signals:', error.message);
    return [];
  }
}

// 시그널 정규화
function normalizeSignalType(signalType) {
  return signalTypeMap[signalType] || signalType;
}

// 텔레그램 보고 (로그만 저장, 실제 전송은 메인 에이전트가 수행)
async function sendTelegramReport(chatId, message) {
  console.log(`📱 [TO ${chatId}] ${message}`);
  // 메시지를 별도 배열에 저장해서 나중에 일괄 처리
  if (!global.telegramMessages) {
    global.telegramMessages = [];
  }
  global.telegramMessages.push({ chatId, message, timestamp: new Date().toISOString() });
}

// 메인 실행 함수
async function main() {
  console.log('🚀 V11 재분류 시작...');
  
  try {
    // 1. 모든 기존 시그널 가져오기
    console.log('📊 기존 시그널 조회 중...');
    const { data: existingSignals, error: signalError } = await supabase
      .from('influencer_signals')
      .select('*')
      .not('key_quote', 'is', null)
      .neq('key_quote', '')
      .order('created_at', { ascending: false });

    if (signalError) throw new Error(`Signal fetch error: ${signalError.message}`);
    
    console.log(`✅ 총 ${existingSignals.length}개 기존 시그널 발견`);

    // 2. video_id별로 그룹화하여 영상 목록 생성
    console.log('📊 영상별 시그널 그룹화 중...');
    const videoGroups = {};
    
    existingSignals.forEach(signal => {
      if (!videoGroups[signal.video_id]) {
        videoGroups[signal.video_id] = {
          video_id: signal.video_id,
          signals: [],
          combined_quotes: '',
          title_hint: ''
        };
      }
      videoGroups[signal.video_id].signals.push({
        ...signal,
        signal_type: normalizeSignalType(signal.signal)
      });
      // 자막 텍스트 재구성을 위해 key_quote들을 결합
      if (signal.key_quote) {
        videoGroups[signal.video_id].combined_quotes += signal.key_quote + ' ';
      }
    });

    const videos = Object.values(videoGroups);
    
    // 텍스트가 충분한 영상만 선택 (최소 200자 이상)
    const videosWithContent = videos.filter(v => v.combined_quotes.length >= 200);
    
    console.log(`✅ 분석 가능한 영상: ${videosWithContent.length}개 (전체 ${videos.length}개 중)`);

    // 3. 각 영상 분석 (충분한 텍스트가 있는 영상만)
    console.log('🔍 V11 분석 시작...');
    
    // 처리할 영상 수 제한 (비용 관리를 위해 - 테스트용으로 50개만)
    const videosToProcess = videosWithContent.slice(0, 50); // 테스트: 50개
    console.log(`📝 처리 예정 영상: ${videosToProcess.length}개 (테스트 버전)`);
    
    for (let i = 0; i < videosToProcess.length; i++) {
      const video = videosToProcess[i];
      const videoTitle = video.combined_quotes.substring(0, 100) + '...';
      console.log(`\n[${i + 1}/${videosToProcess.length}] 분석 중: ${videoTitle}`);
      
      try {
        // 재구성된 자막 텍스트로 V11 분석
        const apiResult = await callAnthropicAPI(video.combined_quotes);
        const newSignals = parseSignals(apiResult.content);
        
        // 시그널 정규화
        const normalizedNewSignals = newSignals.map(signal => ({
          ...signal,
          signal_type: normalizeSignalType(signal.signal_type)
        }));

        // 기존 시그널과 비교
        const oldSignals = video.signals;
        
        // 결과 저장
        results.push({
          video_id: video.video_id,
          title: videoTitle,
          old_signals: oldSignals,
          new_signals: normalizedNewSignals,
          old_signal_count: oldSignals.length,
          new_signal_count: normalizedNewSignals.length,
          api_cost: apiResult.cost,
          content_length: video.combined_quotes.length
        });

        processedCount++;

        // 25개마다 중간 보고 (테스트용)
        if (processedCount % 25 === 0) {
          const progress = `📊 중간 보고 (${processedCount}/${videos.length})\n`;
          const costInfo = `💰 누적 비용: $${totalCost.toFixed(4)}\n`;
          const avgCost = `📈 평균 비용/영상: $${(totalCost / processedCount).toFixed(4)}`;
          
          await sendTelegramReport(TELEGRAM_GROUP_ID, progress + costInfo + avgCost);
        }

        // 레이트 리밋 방지 (테스트용 단축)
        await delay(1000);
        
        // 10개마다 추가 휴식
        if (processedCount % 10 === 0) {
          console.log('😴 10개 처리 완료, 3초 휴식...');
          await delay(3000);
        }

      } catch (error) {
        console.error(`❌ 영상 ${video.video_id} 분석 실패:`, error.message);
        results.push({
          video_id: video.video_id,
          title: videoTitle,
          error: error.message,
          old_signals: video.signals,
          new_signals: [],
          old_signal_count: video.signals.length,
          new_signal_count: 0,
          api_cost: 0,
          content_length: video.combined_quotes.length
        });
      }
    }

    // 4. 결과 분석 및 리포트 생성
    await generateReports();
    
  } catch (error) {
    console.error('❌ 전체 프로세스 실패:', error.message);
  }
}

// 리포트 생성
async function generateReports() {
  console.log('📝 리포트 생성 중...');
  
  // 데이터 디렉토리 생성
  const dataDir = 'C:\\Users\\Mario\\work\\data\\research';
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  // 상세 데이터 JSON 저장
  const dataPath = path.join(dataDir, 'v11_reclassify_data.json');
  fs.writeFileSync(dataPath, JSON.stringify(results, null, 2), 'utf-8');

  // 분석 메트릭 계산
  const metrics = calculateMetrics();
  
  // 리포트 마크다운 생성
  const reportPath = path.join(dataDir, 'v11_reclassify_report.md');
  const report = generateMarkdownReport(metrics);
  fs.writeFileSync(reportPath, report, 'utf-8');

  // 최종 보고
  const finalReport = generateTelegramReport(metrics);
  await sendTelegramReport(TELEGRAM_GROUP_ID, finalReport);
  await sendTelegramReport(JAY_DM_ID, finalReport);
  
  // 텔레그램 메시지 목록을 파일로 저장
  if (global.telegramMessages) {
    const messagesPath = path.join(dataDir, 'telegram_messages.json');
    fs.writeFileSync(messagesPath, JSON.stringify(global.telegramMessages, null, 2), 'utf-8');
    console.log(`📱 텔레그램 메시지 ${global.telegramMessages.length}개 저장: ${messagesPath}`);
  }
  
  console.log('✅ 모든 작업 완료!');
}

// 메트릭 계산
function calculateMetrics() {
  const oldDistribution = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  const newDistribution = { '매수': 0, '긍정': 0, '중립': 0, '부정': 0, '매도': 0 };
  
  let buyToPositiveCount = 0;
  let newSignalCount = 0;
  let removedSignalCount = 0;
  let totalOldSignals = 0;
  let totalNewSignals = 0;
  
  results.forEach(result => {
    // 기존 시그널 분포
    result.old_signals.forEach(signal => {
      if (oldDistribution[signal.signal_type] !== undefined) {
        oldDistribution[signal.signal_type]++;
        totalOldSignals++;
      }
    });
    
    // 새 시그널 분포  
    result.new_signals.forEach(signal => {
      if (newDistribution[signal.signal_type] !== undefined) {
        newDistribution[signal.signal_type]++;
        totalNewSignals++;
      }
    });
    
    // 매수→긍정 재분류 카운트
    const oldBuyStocks = result.old_signals
      .filter(s => s.signal_type === '매수')
      .map(s => s.stock);
    const newPositiveStocks = result.new_signals
      .filter(s => s.signal_type === '긍정')
      .map(s => s.stock);
    
    buyToPositiveCount += oldBuyStocks.filter(stock => 
      newPositiveStocks.includes(stock)
    ).length;
  });

  return {
    totalVideos: results.length,
    processedVideos: results.filter(r => !r.error).length,
    errorVideos: results.filter(r => r.error).length,
    totalCost: totalCost,
    oldDistribution,
    newDistribution,
    totalOldSignals,
    totalNewSignals,
    buyToPositiveCount,
    oldNegativeRatio: (oldDistribution['부정'] / totalOldSignals * 100).toFixed(1),
    newNegativeRatio: (newDistribution['부정'] / totalNewSignals * 100).toFixed(1)
  };
}

// 마크다운 리포트 생성
function generateMarkdownReport(metrics) {
  const timestamp = new Date().toLocaleString('ko-KR');
  
  return `# V11 재분류 결과 리포트

## 실행 정보
- 실행 시간: ${timestamp}
- 총 처리 영상: ${metrics.processedVideos}/${metrics.totalVideos}개
- 오류 영상: ${metrics.errorVideos}개
- 총 비용: $${metrics.totalCost.toFixed(4)}
- 평균 비용/영상: $${(metrics.totalCost / metrics.processedVideos).toFixed(4)}

## 시그널 분포 비교

| 시그널 타입 | 기존 (V10) | V11 | 변화 |
|------------|-----------|-----|------|
| 매수       | ${metrics.oldDistribution['매수']} | ${metrics.newDistribution['매수']} | ${metrics.newDistribution['매수'] - metrics.oldDistribution['매수'] > 0 ? '+' : ''}${metrics.newDistribution['매수'] - metrics.oldDistribution['매수']} |
| 긍정       | ${metrics.oldDistribution['긍정']} | ${metrics.newDistribution['긍정']} | ${metrics.newDistribution['긍정'] - metrics.oldDistribution['긍정'] > 0 ? '+' : ''}${metrics.newDistribution['긍정'] - metrics.oldDistribution['긍정']} |
| 중립       | ${metrics.oldDistribution['중립']} | ${metrics.newDistribution['중립']} | ${metrics.newDistribution['중립'] - metrics.oldDistribution['중립'] > 0 ? '+' : ''}${metrics.newDistribution['중립'] - metrics.oldDistribution['중립']} |
| 부정       | ${metrics.oldDistribution['부정']} | ${metrics.newDistribution['부정']} | ${metrics.newDistribution['부정'] - metrics.oldDistribution['부정'] > 0 ? '+' : ''}${metrics.newDistribution['부정'] - metrics.oldDistribution['부정']} |
| 매도       | ${metrics.oldDistribution['매도']} | ${metrics.newDistribution['매도']} | ${metrics.newDistribution['매도'] - metrics.oldDistribution['매도'] > 0 ? '+' : ''}${metrics.newDistribution['매도'] - metrics.oldDistribution['매도']} |
| **총합**   | **${metrics.totalOldSignals}** | **${metrics.totalNewSignals}** | **${metrics.totalNewSignals - metrics.totalOldSignals > 0 ? '+' : ''}${metrics.totalNewSignals - metrics.totalOldSignals}** |

## 핵심 메트릭

### 🔵 매수→긍정 재분류
- **${metrics.buyToPositiveCount}건** 매수 시그널이 긍정으로 재분류됨

### 🟠 부정 비율 변화
- 기존: ${metrics.oldNegativeRatio}% (${metrics.oldDistribution['부정']}/${metrics.totalOldSignals})
- V11: ${metrics.newNegativeRatio}% (${metrics.newDistribution['부정']}/${metrics.totalNewSignals})
- 변화: ${(parseFloat(metrics.newNegativeRatio) - parseFloat(metrics.oldNegativeRatio)).toFixed(1)}%p

## 데이터 파일
- 상세 데이터: \`v11_reclassify_data.json\`
- 이 리포트: \`v11_reclassify_report.md\`

---
*Generated by V11 재분류 스크립트*
`;
}

// 텔레그램 리포트 생성
function generateTelegramReport(metrics) {
  return `🎯 **V11 재분류 완료**

📊 **처리 현황**
• 영상: ${metrics.processedVideos}/${metrics.totalVideos}개 완료
• 오류: ${metrics.errorVideos}개
• 총 비용: $${metrics.totalCost.toFixed(4)}

📈 **시그널 분포 변화**
• 매수: ${metrics.oldDistribution['매수']} → ${metrics.newDistribution['매수']} (${metrics.newDistribution['매수'] - metrics.oldDistribution['매수'] > 0 ? '+' : ''}${metrics.newDistribution['매수'] - metrics.oldDistribution['매수']})
• 긍정: ${metrics.oldDistribution['긍정']} → ${metrics.newDistribution['긍정']} (${metrics.newDistribution['긍정'] - metrics.oldDistribution['긍정'] > 0 ? '+' : ''}${metrics.newDistribution['긍정'] - metrics.oldDistribution['긍정']})
• 중립: ${metrics.oldDistribution['중립']} → ${metrics.newDistribution['중립']} (${metrics.newDistribution['중립'] - metrics.oldDistribution['중립'] > 0 ? '+' : ''}${metrics.newDistribution['중립'] - metrics.oldDistribution['중립']})
• 부정: ${metrics.oldDistribution['부정']} → ${metrics.newDistribution['부정']} (${metrics.newDistribution['부정'] - metrics.oldDistribution['부정'] > 0 ? '+' : ''}${metrics.newDistribution['부정'] - metrics.oldDistribution['부정']})
• 매도: ${metrics.oldDistribution['매도']} → ${metrics.newDistribution['매도']} (${metrics.newDistribution['매도'] - metrics.oldDistribution['매도'] > 0 ? '+' : ''}${metrics.newDistribution['매도'] - metrics.oldDistribution['매도']})

🔵 **핵심 지표**
• 매수→긍정 재분류: **${metrics.buyToPositiveCount}건**
• 부정 비율: ${metrics.oldNegativeRatio}% → ${metrics.newNegativeRatio}% (${(parseFloat(metrics.newNegativeRatio) - parseFloat(metrics.oldNegativeRatio)).toFixed(1)}%p)

📁 결과 파일: \`data/research/v11_reclassify_*\``;
}

// 실행
main().catch(console.error);