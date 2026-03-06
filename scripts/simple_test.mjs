// simple_test.mjs
// 간단한 테스트로 모듈 동작 확인

import { chunkSubtitle } from './subtitle_chunker.mjs';

console.log('=== 간단한 청킹 테스트 ===');

const testSubtitle = "안녕하세요. 오늘은 삼성전자에 대해 이야기해보겠습니다. 삼성전자는 현재 좋은 모습을 보이고 있습니다. 실적이 개선되고 있어요. 이 종목을 추천드립니다. 다음으로는 LG전자를 살펴보겠습니다. LG전자도 나쁘지 않은 종목입니다. 하지만 조심스럽게 접근해야 합니다. 마지막으로 SK하이닉스를 보겠습니다. 이 종목은 정말 좋습니다. 지금 당장 사시기 바랍니다.";

console.log('원본 자막 길이:', testSubtitle.length);

const chunks = chunkSubtitle(testSubtitle, 200, 50);

console.log('생성된 chunks:', chunks.length);
chunks.forEach((chunk, index) => {
  console.log(`Chunk ${index + 1}: ${chunk.length}자`);
  console.log(`내용: ${chunk.substring(0, 50)}...`);
  console.log('---');
});

console.log('테스트 완료');