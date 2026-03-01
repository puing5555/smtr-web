const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: './invest-sns/.env.local' });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function analyzeSignals() {
  try {
    // 1단계: 전체 시그널 조회 (speakers, influencer_videos 조인)
    const { data: signals, error } = await supabase
      .from('influencer_signals')
      .select(`
        id,
        stock,
        ticker,
        signal,
        confidence,
        key_quote,
        reasoning,
        mention_type,
        market,
        speaker_id,
        video_id,
        speakers(name),
        influencer_videos(title, subtitle_text, published_at, created_at)
      `)
      .order('id', { ascending: true });

    if (error) {
      console.error('Error fetching signals:', error);
      return;
    }

    console.log(`총 시그널 수: ${signals.length}`);
    console.log('\n=== 시그널 타입 분포 ===');
    const signalTypes = {};
    signals.forEach(s => {
      signalTypes[s.signal] = (signalTypes[s.signal] || 0) + 1;
    });
    console.log(signalTypes);

    console.log('\n=== 첫 10개 시그널 상세 정보 ===');
    signals.slice(0, 10).forEach(signal => {
      console.log(`\nID: ${signal.id}`);
      console.log(`종목: ${signal.stock} (${signal.ticker})`);
      console.log(`시그널: ${signal.signal} (신뢰도: ${signal.confidence})`);
      console.log(`화자: ${signal.speakers?.name}`);
      console.log(`영상: ${signal.influencer_videos?.title}`);
      console.log(`업로드: ${signal.influencer_videos?.published_at || signal.influencer_videos?.created_at}`);
      console.log(`핵심 발언: ${signal.key_quote}`);
      console.log(`추론: ${signal.reasoning}`);
      console.log('---');
    });

    // JSON으로 저장해서 상세 분석
    const fs = require('fs');
    fs.writeFileSync('signals_data.json', JSON.stringify(signals, null, 2));
    console.log('\n시그널 데이터를 signals_data.json에 저장했습니다.');

  } catch (err) {
    console.error('Error:', err);
  }
}

analyzeSignals();