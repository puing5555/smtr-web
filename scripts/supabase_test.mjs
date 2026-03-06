// supabase_test.mjs
// Supabase 연결 테스트

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

console.log('=== Supabase 연결 테스트 ===');

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

try {
  console.log('긴 자막 영상 검색 중...');
  
  const { data, error } = await supabase
    .from('youtube_videos') 
    .select('video_id, title, subtitle_text, LENGTH(subtitle_text) as length')
    .not('subtitle_text', 'is', null)
    .order('LENGTH(subtitle_text)', { ascending: false })
    .limit(5);
    
  if (error) {
    console.error('Supabase 에러:', error.message);
  } else {
    console.log(`${data.length}개 영상 발견:`);
    data.forEach((video, index) => {
      console.log(`${index + 1}. ${video.title}`);
      console.log(`   자막 길이: ${video.subtitle_text?.length?.toLocaleString() || 'N/A'}자`);
      console.log(`   Video ID: ${video.video_id}`);
      console.log('---');
    });
  }
} catch (err) {
  console.error('테스트 에러:', err.message);
}