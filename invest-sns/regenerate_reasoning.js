import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config({ path: '.env.local' })

// Supabase client setup
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
const anthropicApiKey = process.env.ANTHROPIC_API_KEY

if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error('Supabase 환경변수가 설정되지 않았습니다')
}

if (!anthropicApiKey || anthropicApiKey === 'YOUR_ANTHROPIC_API_KEY_HERE') {
  throw new Error('Anthropic API 키가 설정되지 않았습니다')
}

const supabase = createClient(supabaseUrl, supabaseServiceKey)

// Sleep function for delay
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Anthropic API call
async function callAnthropicAPI(prompt) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': anthropicApiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 200,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    })
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Anthropic API 오류: ${response.status} - ${error}`)
  }

  const data = await response.json()
  return data.content[0].text
}

// Create reasoning prompt
function createPrompt(stock, signal, keyQuote, subtitleText) {
  const signalTypeMap = {
    'STRONG_BUY': '매수',
    'BUY': '매수', 
    'POSITIVE': '긍정',
    'HOLD': '중립',
    'NEUTRAL': '중립',
    'CONCERN': '경계',
    'SELL': '매도',
    'STRONG_SELL': '매도'
  }
  
  const koreanSignal = signalTypeMap[signal] || signal
  const limitedSubtitle = subtitleText ? subtitleText.substring(0, 3000) : ''
  
  if (!subtitleText) {
    return `다음 시그널의 분석 근거(reasoning)를 작성해줘. 최소 80자 이상, 최대 150자.
    
종목명: ${stock}
시그널: ${koreanSignal}
핵심발언: ${keyQuote}

왜 이 시그널 타입으로 분류했는지, 발언자의 핵심 논거가 무엇인지 구체적으로 설명해줘.`
  }

  return `다음 시그널의 분석 근거(reasoning)를 원본 자막을 기반으로 작성해줘. 최소 80자 이상, 최대 150자. 왜 이 시그널 타입으로 분류했는지, 발언자의 핵심 논거가 무엇인지 구체적으로 설명.

종목명: ${stock}
시그널: ${koreanSignal}
핵심발언: ${keyQuote}
자막: ${limitedSubtitle}`
}

async function main() {
  console.log('🔍 reasoning이 null이거나 80자 미만인 시그널 조회 중...')
  
  // 1. Get signals with null or short reasoning
  const { data: signals, error: signalsError } = await supabase
    .from('influencer_signals')
    .select('id, stock, ticker, signal, confidence, key_quote, reasoning, video_id')
    .or('reasoning.is.null,reasoning.eq.')
    
  if (signalsError) {
    console.error('시그널 조회 오류:', signalsError)
    return
  }

  // Filter signals with reasoning less than 80 characters
  const filteredSignals = signals.filter(signal => 
    !signal.reasoning || signal.reasoning.length < 80
  )

  console.log(`📊 전체 시그널: ${signals.length}개`)
  console.log(`🔧 재생성 필요 시그널: ${filteredSignals.length}개`)

  if (filteredSignals.length === 0) {
    console.log('✅ 재생성이 필요한 시그널이 없습니다.')
    return
  }

  let successCount = 0
  let failureCount = 0
  const failedSignals = []

  // Process in batches of 10
  for (let i = 0; i < filteredSignals.length; i += 10) {
    const batch = filteredSignals.slice(i, i + 10)
    console.log(`\n📦 배치 ${Math.floor(i/10) + 1}/${Math.ceil(filteredSignals.length/10)} 처리 중... (${batch.length}개)`)

    for (const signal of batch) {
      try {
        console.log(`  🔄 처리 중: ${signal.stock} (ID: ${signal.id})`)
        
        let subtitleText = null
        
        // 2. Get subtitle text from video
        if (signal.video_id) {
          const { data: video, error: videoError } = await supabase
            .from('influencer_videos')
            .select('subtitle_text')
            .eq('id', signal.video_id)
            .single()
            
          if (videoError) {
            console.log(`    ⚠️  영상 자막 조회 실패 (video_id: ${signal.video_id})`)
          } else {
            subtitleText = video.subtitle_text
          }
        }

        // 3. Create prompt and call Anthropic API
        const prompt = createPrompt(signal.stock, signal.signal, signal.key_quote, subtitleText)
        const newReasoning = await callAnthropicAPI(prompt)

        // 4. Update reasoning in database
        const { error: updateError } = await supabase
          .from('influencer_signals')
          .update({ reasoning: newReasoning })
          .eq('id', signal.id)

        if (updateError) {
          console.log(`    ❌ DB 업데이트 실패: ${updateError.message}`)
          failureCount++
          failedSignals.push({ id: signal.id, stock: signal.stock, error: updateError.message })
        } else {
          console.log(`    ✅ 성공: ${newReasoning.substring(0, 50)}...`)
          successCount++
        }

        // Delay between requests (2 seconds)
        await sleep(2000)
        
      } catch (error) {
        console.log(`    ❌ 오류: ${error.message}`)
        failureCount++
        failedSignals.push({ id: signal.id, stock: signal.stock, error: error.message })
      }
    }
  }

  console.log('\n📈 작업 완료 결과:')
  console.log(`✅ 성공: ${successCount}개`)
  console.log(`❌ 실패: ${failureCount}개`)

  if (failedSignals.length > 0) {
    console.log('\n❌ 실패한 시그널들:')
    failedSignals.forEach(failure => {
      console.log(`  - ID ${failure.id} (${failure.stock}): ${failure.error}`)
    })
  }

  console.log(`\n🎯 총 ${successCount}개 시그널의 reasoning이 재생성되었습니다.`)
}

main().catch(console.error)