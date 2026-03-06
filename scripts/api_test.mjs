// api_test.mjs
// Anthropic API 간단 테스트

const ANTHROPIC_API_KEY = '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';
const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';

console.log('=== Anthropic API 테스트 ===');

const requestBody = {
  model: "claude-3-5-sonnet-20241022",
  max_tokens: 100,
  messages: [
    {
      role: "user",
      content: "안녕하세요. 간단히 '테스트 성공'이라고 응답해주세요."
    }
  ]
};

try {
  console.log('API 호출 중...');
  
  const response = await fetch(ANTHROPIC_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify(requestBody)
  });

  console.log('응답 상태:', response.status);
  console.log('응답 헤더:', response.headers);
  
  if (!response.ok) {
    const errorText = await response.text();
    console.log('에러 응답:', errorText);
  } else {
    const result = await response.json();
    console.log('성공 응답:', JSON.stringify(result, null, 2));
  }
  
} catch (error) {
  console.error('API 에러:', error.message);
}