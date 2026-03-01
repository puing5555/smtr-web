const { Client } = require('pg');

// Supabase 연결 정보
const client = new Client({
  connectionString: 'postgresql://postgres.arypzhotxflimroprmdk:invest$sns2024@arypzhotxflimroprmdk.supabase.co:5432/postgres',
  ssl: {
    rejectUnauthorized: false
  }
});

async function analyzeSignals() {
  try {
    await client.connect();
    console.log('✅ Supabase 연결 성공');

    // 1. signals 테이블 구조 확인
    console.log('\n📋 signals 테이블 구조:');
    const tableInfo = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default 
      FROM information_schema.columns 
      WHERE table_name = 'signals' 
      ORDER BY ordinal_position
    `);
    console.table(tableInfo.rows);

    // 2. 전체 시그널 수 확인
    const totalCount = await client.query('SELECT COUNT(*) FROM signals');
    console.log(`\n📊 전체 시그널 수: ${totalCount.rows[0].count}개`);

    // 3. 품질 이슈 분석 시작
    console.log('\n🔍 품질 이슈 분석:');
    
    // 3.1 화자 오류 (speaker가 채널 호스트인데 게스트가 말한 경우 체크를 위해 videos와 조인)
    console.log('\n1. 화자 오류 분석:');
    const speakerIssues = await client.query(`
      SELECT s.speaker, v.channel_id, COUNT(*) as count
      FROM signals s
      JOIN videos v ON s.video_id = v.id
      GROUP BY s.speaker, v.channel_id
      ORDER BY count DESC
    `);
    
    console.log('화자별 채널 분포:');
    console.table(speakerIssues.rows.slice(0, 20));

    // 3.2 시그널 유형 분석
    console.log('\n2. 시그널 유형 분석:');
    const signalTypes = await client.query(`
      SELECT signal_type, COUNT(*) as count
      FROM signals 
      GROUP BY signal_type 
      ORDER BY count DESC
    `);
    
    console.log('시그널 타입별 분포:');
    console.table(signalTypes.rows);
    
    // 유효하지 않은 시그널 타입 체크
    const invalidSignalTypes = await client.query(`
      SELECT * FROM signals 
      WHERE signal_type NOT IN ('STRONG_BUY', 'BUY', 'POSITIVE', 'HOLD', 'NEUTRAL', 'CONCERN', 'SELL', 'STRONG_SELL')
      LIMIT 10
    `);
    console.log(`잘못된 시그널 타입: ${invalidSignalTypes.rows.length}개`);
    if (invalidSignalTypes.rows.length > 0) {
      console.table(invalidSignalTypes.rows);
    }

    // 3.3 key_quote 부정확 문제
    console.log('\n3. key_quote 품질 분석:');
    const emptyQuotes = await client.query(`
      SELECT COUNT(*) as count FROM signals 
      WHERE key_quote IS NULL OR key_quote = '' OR LENGTH(key_quote) < 10
    `);
    console.log(`key_quote 부정확 (비어있거나 10자 미만): ${emptyQuotes.rows[0].count}개`);
    
    const shortQuotes = await client.query(`
      SELECT speaker, ticker, key_quote, LENGTH(key_quote) as length
      FROM signals 
      WHERE key_quote IS NOT NULL AND LENGTH(key_quote) < 10
      LIMIT 10
    `);
    console.log('짧은 key_quote 예시:');
    console.table(shortQuotes.rows);

    // 3.4 타임스탬프 이상
    console.log('\n4. 타임스탬프 이상:');
    const timestampIssues = await client.query(`
      SELECT COUNT(*) as count FROM signals 
      WHERE timestamp IS NULL OR timestamp = '00:00' OR timestamp = '0:00'
    `);
    console.log(`타임스탬프 이상 (null 또는 0초): ${timestampIssues.rows[0].count}개`);
    
    const badTimestamps = await client.query(`
      SELECT speaker, ticker, timestamp
      FROM signals 
      WHERE timestamp IS NULL OR timestamp = '00:00' OR timestamp = '0:00'
      LIMIT 10
    `);
    console.log('타임스탬프 이상 예시:');
    console.table(badTimestamps.rows);

    // 3.5 중복 시그널 체크
    console.log('\n5. 중복 시그널 분석:');
    const duplicates = await client.query(`
      SELECT video_id, ticker, signal_type, COUNT(*) as count
      FROM signals 
      GROUP BY video_id, ticker, signal_type
      HAVING COUNT(*) > 1
      ORDER BY count DESC
    `);
    console.log(`중복 시그널 (같은 영상+종목+시그널타입): ${duplicates.rows.length}개 그룹`);
    if (duplicates.rows.length > 0) {
      console.table(duplicates.rows.slice(0, 10));
    }

    // 3.6 ticker 이상
    console.log('\n6. ticker 품질 분석:');
    const tickerIssues = await client.query(`
      SELECT ticker, COUNT(*) as count FROM signals 
      WHERE ticker IS NULL OR ticker = '' OR ticker = '없음' OR ticker = 'N/A' OR ticker = '-'
      GROUP BY ticker
      ORDER BY count DESC
    `);
    console.log(`ticker 이상: ${tickerIssues.rows.length}개 타입`);
    console.table(tickerIssues.rows);

    // 4. mention_type 분포 (V9에서 추가된 규칙 효과 분석)
    console.log('\n📈 mention_type 분포 (V9 규칙 효과 분석):');
    const mentionTypes = await client.query(`
      SELECT mention_type, COUNT(*) as count
      FROM signals 
      GROUP BY mention_type 
      ORDER BY count DESC
    `);
    console.table(mentionTypes.rows);

    // 5. confidence 분포
    console.log('\n📊 confidence 분포:');
    const confidenceLevels = await client.query(`
      SELECT confidence, COUNT(*) as count
      FROM signals 
      GROUP BY confidence 
      ORDER BY 
        CASE confidence 
          WHEN 'very_high' THEN 1
          WHEN 'high' THEN 2  
          WHEN 'medium' THEN 3
          WHEN 'low' THEN 4
          WHEN 'very_low' THEN 5
          ELSE 6
        END
    `);
    console.table(confidenceLevels.rows);

    // 6. 최신 시그널 몇 개 예시
    console.log('\n📄 최신 시그널 예시 (5개):');
    const recentSignals = await client.query(`
      SELECT s.speaker, s.ticker, s.signal_type, s.mention_type, s.confidence, s.key_quote, v.title, s.created_at
      FROM signals s
      JOIN videos v ON s.video_id = v.id
      ORDER BY s.created_at DESC
      LIMIT 5
    `);
    console.table(recentSignals.rows);

  } catch (error) {
    console.error('❌ 에러:', error);
  } finally {
    await client.end();
  }
}

analyzeSignals();