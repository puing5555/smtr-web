// basic_connection.mjs
// Supabase 기본 연결 테스트

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

console.log('=== Supabase 기본 연결 테스트 ===');

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

try {
  // RPC 함수로 현재 시간 가져오기
  const { data, error } = await supabase.rpc('now');
  
  if (error) {
    console.log('RPC 에러:', error.message);
  } else {
    console.log('연결 성공! 현재 시간:', data);
  }
} catch (err) {
  console.log('연결 테스트 에러:', err.message);
}

// REST API 직접 호출로 테이블 목록 가져오기 시도
try {
  console.log('\nREST API 직접 호출 시도...');
  
  const response = await fetch(`${SUPABASE_URL}/rest/v1/`, {
    method: 'GET',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json'
    }
  });
  
  console.log('응답 상태:', response.status);
  const text = await response.text();
  console.log('응답 내용 (일부):', text.substring(0, 200));
  
} catch (err) {
  console.log('REST API 에러:', err.message);
}