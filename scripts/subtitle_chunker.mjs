// subtitle_chunker.mjs
// 긴 자막을 chunking하여 V11 프롬프트로 분석 후 병합하는 모듈

import fs from 'fs/promises';
import path from 'path';

const ANTHROPIC_API_KEY = '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';
const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';
const REQUEST_DELAY_MS = 3000; // 3초 딜레이
const RETRY_DELAY_MS = 60000; // 429 에러 시 60초 대기

const CHUNK_SIZE = 7000;
const OVERLAP_SIZE = 500;

// 시그널 타입 강도 (높을수록 강함)
const SIGNAL_STRENGTH = {
  '매도': 5,
  '부정': 4, 
  '중립': 3,
  '긍정': 2,
  '매수': 1
};

/**
 * 문장 경계에서 자막을 chunking
 */
export function chunkSubtitle(subtitle, chunkSize = CHUNK_SIZE, overlap = OVERLAP_SIZE) {
  if (!subtitle || subtitle.length <= chunkSize) {
    return [subtitle];
  }

  const chunks = [];
  let start = 0;
  
  while (start < subtitle.length) {
    let end = start + chunkSize;
    
    if (end >= subtitle.length) {
      // 마지막 chunk
      chunks.push(subtitle.slice(start));
      break;
    }
    
    // 문장 경계 찾기 (마침표, 물음표, 느낌표)
    const searchStart = end - 200; // 뒤에서 200자 내에서 문장 경계 찾기
    let sentenceEnd = -1;
    
    for (let i = end; i >= Math.max(searchStart, start); i--) {
      if ('.?!'.includes(subtitle[i]) && subtitle[i + 1] === ' ') {
        sentenceEnd = i + 1;
        break;
      }
    }
    
    if (sentenceEnd === -1) {
      // 문장 경계 못 찾으면 그냥 자르기
      sentenceEnd = end;
    }
    
    chunks.push(subtitle.slice(start, sentenceEnd));
    start = sentenceEnd - overlap; // overlap 적용
    
    if (start < 0) start = 0;
  }
  
  return chunks.filter(chunk => chunk.trim().length > 0);
}

/**
 * V11 프롬프트 로드
 */
async function loadV11Prompt() {
  try {
    const promptPath = 'C:\\Users\\Mario\\work\\invest-sns\\prompts\\pipeline_v11.md';
    return await fs.readFile(promptPath, 'utf-8');
  } catch (error) {
    throw new Error(`V11 프롬프트 로드 실패: ${error.message}`);
  }
}

/**
 * 딜레이 함수
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Anthropic API 호출
 */
async function callAnthropicAPI(prompt, subtitle, videoTitle, chunkIndex, totalChunks, retryCount = 0) {
  const chunkHeader = totalChunks > 1 
    ? `\n\n[영상 제목: ${videoTitle}]\n[Chunk ${chunkIndex + 1}/${totalChunks}]\n\n`
    : `\n\n[영상 제목: ${videoTitle}]\n\n`;

  const fullPrompt = prompt + chunkHeader + subtitle;

  const requestBody = {
    model: "claude-3-haiku-20240307",
    max_tokens: 4000,
    messages: [
      {
        role: "user",
        content: fullPrompt
      }
    ]
  };

  try {
    const response = await fetch(ANTHROPIC_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(requestBody)
    });

    if (response.status === 429) {
      if (retryCount < 3) {
        console.log(`Rate limit hit. 대기중... (${retryCount + 1}/3)`);
        await delay(RETRY_DELAY_MS);
        return await callAnthropicAPI(prompt, subtitle, videoTitle, chunkIndex, totalChunks, retryCount + 1);
      } else {
        throw new Error('Rate limit exceeded after 3 retries');
      }
    }

    if (!response.ok) {
      throw new Error(`API 에러: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.content && result.content[0] && result.content[0].text) {
      return result.content[0].text;
    } else {
      throw new Error('Invalid API response format');
    }
  } catch (error) {
    if (retryCount < 3) {
      console.log(`API 에러, 재시도... (${retryCount + 1}/3): ${error.message}`);
      await delay(5000);
      return await callAnthropicAPI(prompt, subtitle, videoTitle, chunkIndex, totalChunks, retryCount + 1);
    } else {
      throw error;
    }
  }
}

/**
 * JSON 파싱 (마크다운 코드 블록 처리 + 개선된 파싱)
 */
function parseJSON(text) {
  try {
    // 1. 마크다운 코드 블록 추출
    let cleanText = text;
    const jsonMatch = text.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
    if (jsonMatch) {
      cleanText = jsonMatch[1];
    } else {
      // 2. 첫 번째 { 부터 마지막 } 까지 추출
      const startIdx = text.indexOf('{');
      const lastIdx = text.lastIndexOf('}');
      if (startIdx !== -1 && lastIdx !== -1 && lastIdx > startIdx) {
        cleanText = text.substring(startIdx, lastIdx + 1);
      }
    }
    
    return JSON.parse(cleanText);
  } catch (error) {
    console.log(`JSON 파싱 실패한 텍스트: ${text.substring(0, 200)}...`);
    // 빈 signals 배열 반환
    return { signals: [] };
  }
}

/**
 * 시그널 병합 (1영상 1종목 1시그널 규칙)
 */
export function mergeSignals(allSignals) {
  if (!allSignals || allSignals.length === 0) {
    return [];
  }

  // 종목별로 그룹핑
  const stockGroups = {};
  
  for (const signal of allSignals) {
    if (!signal.stock) continue;
    
    const key = signal.stock.toLowerCase().trim();
    if (!stockGroups[key]) {
      stockGroups[key] = [];
    }
    stockGroups[key].push(signal);
  }
  
  // 각 종목별로 최적의 시그널 선택
  const mergedSignals = [];
  
  for (const [stock, signals] of Object.entries(stockGroups)) {
    if (signals.length === 1) {
      mergedSignals.push(signals[0]);
      continue;
    }
    
    // 1. 가장 강한 시그널 타입 찾기
    const strongestType = signals.reduce((strongest, signal) => {
      const currentStrength = SIGNAL_STRENGTH[signal.signal_type] || 10;
      const strongestStrength = SIGNAL_STRENGTH[strongest.signal_type] || 10;
      return currentStrength < strongestStrength ? signal : strongest;
    });
    
    // 2. 같은 타입 중 가장 높은 confidence 찾기
    const sameTypeSignals = signals.filter(s => s.signal_type === strongestType.signal_type);
    const bestSignal = sameTypeSignals.reduce((best, signal) => {
      return (signal.confidence || 0) > (best.confidence || 0) ? signal : best;
    });
    
    mergedSignals.push(bestSignal);
  }
  
  return mergedSignals;
}

/**
 * 메인 처리 함수: chunking → 분석 → 병합
 */
export async function processSubtitleChunks(subtitle, videoTitle, options = {}) {
  const { 
    chunkSize = CHUNK_SIZE,
    overlap = OVERLAP_SIZE,
    verbose = false 
  } = options;

  console.log(`\n=== ${videoTitle} 처리 시작 ===`);
  console.log(`자막 길이: ${subtitle.length}자`);

  // 1. V11 프롬프트 로드
  const prompt = await loadV11Prompt();
  
  // 2. 자막 chunking
  const chunks = chunkSubtitle(subtitle, chunkSize, overlap);
  console.log(`Chunks 생성됨: ${chunks.length}개`);
  
  if (chunks.length === 1) {
    console.log('단일 chunk - 일반 처리');
  }

  // 3. 각 chunk 분석
  const allSignals = [];
  let totalCost = 0;
  
  for (let i = 0; i < chunks.length; i++) {
    if (verbose) {
      console.log(`\nChunk ${i + 1}/${chunks.length} 처리 중... (${chunks[i].length}자)`);
    }
    
    try {
      const response = await callAnthropicAPI(prompt, chunks[i], videoTitle, i, chunks.length);
      const parsed = parseJSON(response);
      
      if (parsed.signals && Array.isArray(parsed.signals)) {
        allSignals.push(...parsed.signals);
        if (verbose) {
          console.log(`  → ${parsed.signals.length}개 시그널 추출`);
        }
      }
      
      // 비용 계산 (대략적)
      const inputTokens = Math.ceil((prompt.length + chunks[i].length) / 4);
      const outputTokens = Math.ceil(response.length / 4);
      const cost = (inputTokens * 0.003 + outputTokens * 0.015) / 1000;
      totalCost += cost;
      
    } catch (error) {
      console.error(`Chunk ${i + 1} 처리 에러:`, error.message);
    }
    
    // 레이트 리밋 방지 딜레이 (마지막 chunk 제외)
    if (i < chunks.length - 1) {
      await delay(REQUEST_DELAY_MS);
    }
  }
  
  // 4. 시그널 병합
  const mergedSignals = mergeSignals(allSignals);
  
  console.log(`\n처리 완료:`);
  console.log(`  - 전체 시그널: ${allSignals.length}개`);
  console.log(`  - 병합 후: ${mergedSignals.length}개`);
  console.log(`  - 예상 비용: $${totalCost.toFixed(4)}`);
  
  return {
    chunks: chunks.length,
    totalSignals: allSignals.length,
    mergedSignals,
    estimatedCost: totalCost,
    allSignalsRaw: allSignals // 디버깅용
  };
}

/**
 * 기존 truncation 방식 처리 (비교용)
 */
export async function processSubtitleTruncated(subtitle, videoTitle, truncateAt = 8000) {
  console.log(`\n=== ${videoTitle} (Truncated) 처리 시작 ===`);
  
  const truncatedSubtitle = subtitle.length > truncateAt 
    ? subtitle.substring(0, truncateAt) 
    : subtitle;
    
  console.log(`자막 길이: ${subtitle.length}자 → ${truncatedSubtitle.length}자`);
  
  const prompt = await loadV11Prompt();
  
  try {
    const response = await callAnthropicAPI(prompt, truncatedSubtitle, videoTitle, 0, 1);
    const parsed = parseJSON(response);
    
    const inputTokens = Math.ceil((prompt.length + truncatedSubtitle.length) / 4);
    const outputTokens = Math.ceil(response.length / 4);
    const cost = (inputTokens * 0.003 + outputTokens * 0.015) / 1000;
    
    console.log(`처리 완료: ${parsed.signals?.length || 0}개 시그널, 비용: $${cost.toFixed(4)}`);
    
    return {
      signals: parsed.signals || [],
      estimatedCost: cost,
      truncatedLength: truncatedSubtitle.length,
      originalLength: subtitle.length
    };
  } catch (error) {
    console.error('Truncated 처리 에러:', error.message);
    return { signals: [], estimatedCost: 0, error: error.message };
  }
}

export default {
  processSubtitleChunks,
  processSubtitleTruncated,
  chunkSubtitle,
  mergeSignals
};