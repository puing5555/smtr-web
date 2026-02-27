// YouTube 스크립트 추출 자동화
// 1. 더보기 클릭 → 스크립트 표시 클릭 → 자막 텍스트 추출

async function extractTranscript() {
  // 1. 더보기 버튼 클릭
  const moreBtn = document.querySelector('tp-yt-paper-button#expand');
  if (moreBtn) moreBtn.click();
  await new Promise(r => setTimeout(r, 1000));
  
  // 2. 스크립트 표시 버튼 찾기 및 클릭
  const buttons = [...document.querySelectorAll('button')];
  const scriptBtn = buttons.find(b => b.textContent.includes('스크립트 표시'));
  if (scriptBtn) {
    scriptBtn.click();
    await new Promise(r => setTimeout(r, 2000));
  }
  
  // 3. 자막 추출
  const panel = document.querySelector('ytd-transcript-renderer, ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-searchable-transcript"]');
  if (!panel) return 'NO_PANEL';
  
  const segments = panel.querySelectorAll('ytd-transcript-segment-renderer');
  if (segments.length === 0) return 'NO_SEGMENTS';
  
  let text = '';
  segments.forEach(seg => {
    const ts = seg.querySelector('.segment-timestamp')?.textContent?.trim() || '';
    const body = seg.querySelector('.segment-text')?.textContent?.trim() || '';
    text += ts + ' ' + body + '\n';
  });
  
  return text + '\n--- Total: ' + segments.length + ' segments ---';
}

return extractTranscript();
