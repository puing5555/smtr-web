#!/usr/bin/env node

import fs from 'fs';
import path from 'path';

// 환경 설정
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const ANTHROPIC_KEY = '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';
const MODEL = 'claude-sonnet-4-20250514';

// 파일 경로
const PROGRESS_FILE = 'C:/Users/Mario/work/data/research/v11_progress_100.json';
const PROMPT_FILE = 'C:/Users/Mario/work/invest-sns/prompts/pipeline_v11.md';
const FINAL_RESULTS_FILE = 'C:/Users/Mario/work/data/research/v11_complete_results.json';
const LOG_FILE = 'C:/Users/Mario/work/data/research/v11_finish_log.txt';

// 통계
let totalCost = 0;
let processedCount = 0;
let dbUpdateCount = 0;

function log(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}`;
    console.log(logEntry);
    fs.appendFileSync(LOG_FILE, logEntry + '\n');
}

// 딜레이 함수
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// API 호출 함수
async function callAnthropic(prompt, inputTokens = 0) {
    try {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_KEY,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: MODEL,
                max_tokens: 4000,
                messages: [{
                    role: 'user',
                    content: prompt
                }]
            })
        });

        if (response.status === 429) {
            log('  Rate limit hit. Waiting 60s...');
            await sleep(60000);
            return callAnthropic(prompt, inputTokens);
        }

        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        const outputTokens = result.usage?.output_tokens || 0;
        const cost = (inputTokens * 0.003 + outputTokens * 0.015) / 1000;
        totalCost += cost;

        log(`  Tokens: ${inputTokens} in / ${outputTokens} out | Cost: $${cost.toFixed(4)}`);

        return result.content[0].text;
    } catch (error) {
        log(`  API error: ${error.message}`);
        await sleep(5000);
        throw error;
    }
}

// Supabase API 호출
async function supabaseApi(endpoint, method = 'GET', body = null) {
    const url = `${SUPABASE_URL}/rest/v1${endpoint}`;
    const options = {
        method,
        headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
        throw new Error(`Supabase error: ${response.status} ${response.statusText}`);
    }

    if (method === 'GET') {
        return response.json();
    }
    return response;
}

// V11 분석 수행
async function analyzeWithV11(transcript, videoSignals) {
    const v11Prompt = fs.readFileSync(PROMPT_FILE, 'utf8');
    
    const prompt = `${v11Prompt}

## 분석 대상 자막
${transcript}

## 기존 시그널 (참고용)
${videoSignals.map(s => `- ${s.stock}: ${s.signal}`).join('\n')}

위 자막을 V11 파이프라인으로 분석하여 JSON 형식으로 시그널을 추출해주세요.`;

    const inputTokens = prompt.length / 4; // 대략 추정
    const response = await callAnthropic(prompt, inputTokens);
    
    try {
        // JSON 추출
        const jsonMatch = response.match(/```json\n(.*?)\n```/s) || response.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            throw new Error('No JSON found in response');
        }
        
        const result = JSON.parse(jsonMatch[1] || jsonMatch[0]);
        return result.signals || [];
    } catch (error) {
        log(`  JSON parsing error: ${error.message}`);
        return [];
    }
}

async function main() {
    try {
        log('=== V11 DB UPDATE + 나머지 처리 시작 ===');
        
        // 1. 기존 진행 상황 로드
        log('Loading existing progress...');
        const progressData = JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf8'));
        const processedVideoIds = new Set(progressData.map(item => item.video_id));
        log(`Existing processed videos: ${processedVideoIds.size}`);
        
        // 2. DB에서 전체 시그널 가져오기
        log('Fetching all signals from DB...');
        const allSignals = await supabaseApi('/influencer_signals?select=id,video_id,stock,signal,key_quote&limit=1000');
        log(`Total signals in DB: ${allSignals.length}`);
        
        // 3. video_id별로 그룹핑 및 key_quote 200자+ 필터링
        const videoGroups = {};
        for (const signal of allSignals) {
            if (!videoGroups[signal.video_id]) {
                videoGroups[signal.video_id] = [];
            }
            videoGroups[signal.video_id].push(signal);
        }
        
        const videosToProcess = [];
        for (const [videoId, signals] of Object.entries(videoGroups)) {
            if (processedVideoIds.has(videoId)) continue;
            
            const keyQuote = signals[0].key_quote || '';
            if (keyQuote.length >= 200) {
                videosToProcess.push({
                    video_id: videoId,
                    signals,
                    key_quote: keyQuote
                });
            }
        }
        
        log(`Videos to process: ${videosToProcess.length}`);
        log(`Videos with 200+ chars total: ${Object.values(videoGroups).filter(signals => signals[0].key_quote?.length >= 200).length}`);
        
        // 4. 나머지 영상들 V11 재분석
        const newResults = [];
        let saveCounter = 0;
        
        for (let i = 0; i < videosToProcess.length; i++) {
            const video = videosToProcess[i];
            log(`[${i+1}/${videosToProcess.length}] Processing video ${video.video_id.substring(0,8)}... (${video.signals.length} signals, ${video.key_quote.length} chars)`);
            
            try {
                const newSignals = await analyzeWithV11(video.key_quote, video.signals);
                
                const result = {
                    video_id: video.video_id,
                    old_signals: video.signals.map(s => ({
                        id: s.id,
                        stock: s.stock,
                        signal: s.signal
                    })),
                    new_signals: newSignals,
                    processed_at: new Date().toISOString()
                };
                
                newResults.push(result);
                processedCount++;
                
                log(`  Results: ${video.signals.length} old signals → ${newSignals.length} new signals`);
                
                // 10개마다 중간 저장
                if ((i + 1) % 10 === 0) {
                    const tempFile = `C:/Users/Mario/work/data/research/v11_temp_${i+1}.json`;
                    fs.writeFileSync(tempFile, JSON.stringify(newResults, null, 2));
                    log(`  Saved progress: ${newResults.length} results`);
                }
                
                // 딜레이 적용
                if ((i + 1) % 20 === 0) {
                    log('  20개 처리 완료. 5초 휴식...');
                    await sleep(5000);
                } else {
                    await sleep(3000);
                }
                
            } catch (error) {
                log(`  Error processing video ${video.video_id}: ${error.message}`);
                await sleep(5000);
            }
        }
        
        // 5. 전체 결과 합산 (기존 100개 + 새로 처리한 것들)
        const allResults = [...progressData, ...newResults];
        fs.writeFileSync(FINAL_RESULTS_FILE, JSON.stringify(allResults, null, 2));
        log(`Final results saved: ${allResults.length} total processed videos`);
        
        // 6. DB UPDATE 수행
        log('\n=== DB UPDATE 시작 ===');
        for (const result of allResults) {
            for (const oldSignal of result.old_signals) {
                // 매칭되는 new signal 찾기
                const matchingNew = result.new_signals.find(newSig => {
                    // 종목명 정규화하여 비교
                    const oldStock = oldSignal.stock.replace(/[\s\-()]/g, '').toLowerCase();
                    const newStock = newSig.stock.replace(/[\s\-()]/g, '').toLowerCase();
                    
                    return oldStock === newStock || 
                           oldStock.includes(newStock) || 
                           newStock.includes(oldStock);
                });
                
                if (matchingNew) {
                    try {
                        await supabaseApi(`/influencer_signals?id=eq.${oldSignal.id}`, 'PATCH', {
                            signal: matchingNew.signal_type,
                            pipeline_version: 'V11'
                        });
                        
                        dbUpdateCount++;
                        if (dbUpdateCount % 50 === 0) {
                            log(`  DB Updated: ${dbUpdateCount} records`);
                            await sleep(1000);
                        }
                        
                    } catch (error) {
                        log(`  DB update error for ${oldSignal.id}: ${error.message}`);
                    }
                }
            }
        }
        
        // 7. 최종 통계 확인
        log('\n=== 최종 확인 ===');
        const finalSignals = await supabaseApi('/influencer_signals?select=signal&limit=1000');
        const signalCounts = {};
        
        for (const sig of finalSignals) {
            signalCounts[sig.signal] = (signalCounts[sig.signal] || 0) + 1;
        }
        
        log('Final signal distribution:');
        Object.entries(signalCounts).sort((a,b) => b[1] - a[1]).forEach(([signal, count]) => {
            log(`  ${signal}: ${count}개`);
        });
        
        log('\n=== 완료 ===');
        log(`처리 완료: 전체 ${allResults.length}개 영상`);
        log(`새로 처리: ${newResults.length}개 영상`);
        log(`DB 업데이트: ${dbUpdateCount}건`);
        log(`총 비용: $${totalCost.toFixed(2)}`);
        
        // 최종 보고서 작성
        const report = `📊 V11 재분류 + DB UPDATE 최종 완료

전체 처리: ${allResults.length}개 영상
- 기존: ${progressData.length}개
- 신규: ${newResults.length}개

DB UPDATE: ${dbUpdateCount}건 업데이트
총 비용: $${totalCost.toFixed(2)}

최종 시그널 분포:
${Object.entries(signalCounts).sort((a,b) => b[1] - a[1]).map(([signal, count]) => 
    `│ ${signal.padEnd(4)} │ ${count.toString().padStart(3)} │`
).join('\n')}

✅ 작업 완료`;

        fs.writeFileSync('C:/Users/Mario/work/data/research/v11_final_report.txt', report);
        console.log('\n' + report);
        
    } catch (error) {
        log(`Fatal error: ${error.message}`);
        console.error(error);
        process.exit(1);
    }
}

// 메인 실행
main().catch(console.error);