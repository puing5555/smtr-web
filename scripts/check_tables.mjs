// check_tables.mjs
// Supabase 테이블 구조 확인

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

console.log('=== Supabase 테이블 확인 ===');

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// 여러 가능한 테이블명 시도
const possibleTables = [
  'youtube_videos',
  'videos', 
  'youtube_video',
  'video',
  'ytb_videos',
  'channels',
  'transcripts'
];

for (const tableName of possibleTables) {
  try {
    console.log(`\n테스트 중: ${tableName}`);
    const { data, error } = await supabase
      .from(tableName)
      .select('*')
      .limit(1);
      
    if (error) {
      console.log(`❌ ${tableName}: ${error.message}`);
    } else {
      console.log(`✅ ${tableName}: 성공! (${data?.length || 0}개 행)`);
      if (data && data.length > 0) {
        console.log('컬럼:', Object.keys(data[0]).join(', '));
      }
    }
  } catch (err) {
    console.log(`❌ ${tableName}: ${err.message}`);
  }
}