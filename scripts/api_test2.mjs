// api_test2.mjs
// 다른 모델명으로 테스트

const ANTHROPIC_API_KEY = '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';
const ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages';

const models = [
  "claude-3-5-sonnet-20241022",
  "claude-3-5-sonnet-20240620", 
  "claude-3-sonnet-20240229",
  "claude-3-haiku-20240307",
  "claude-3-opus-20240229"
];

for (const model of models) {
  console.log(`\n=== 테스트 모델: ${model} ===`);
  
  const requestBody = {
    model: model,
    max_tokens: 50,
    messages: [
      {
        role: "user", 
        content: "테스트"
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

    console.log('응답 상태:', response.status);
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ 성공!');
      console.log('응답:', result.content?.[0]?.text || 'no content');
      break; // 첫 번째 성공한 모델로 중단
    } else {
      const errorText = await response.text();
      console.log('❌ 실패:', JSON.parse(errorText).error?.message || 'unknown error');
    }
    
  } catch (error) {
    console.log('❌ 에러:', error.message);
  }
}