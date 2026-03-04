
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const CHANNEL_ID = 'd153b75b-1843-4a99-b49f-c31081a8f566';
const headers = { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` };

async function query(path) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, { headers });
  return res.json();
}

// Get all videos
let allVideos = [];
for (let offset = 0; ; offset += 1000) {
  const batch = await query(`influencer_videos?select=id,title,published_at&channel_id=eq.${CHANNEL_ID}&order=published_at.desc&offset=${offset}&limit=1000`);
  allVideos.push(...batch);
  if (batch.length < 1000) break;
}
console.log('Total videos:', allVideos.length);

// Get signal counts
let allSignals = [];
for (let offset = 0; ; offset += 1000) {
  const batch = await query(`influencer_signals?select=video_id&video_id=not.is.null&offset=${offset}&limit=1000`);
  allSignals.push(...batch);
  if (batch.length < 1000) break;
}
const signalCounts = {};
for (const s of allSignals) signalCounts[s.video_id] = (signalCounts[s.video_id] || 0) + 1;

// Extract guest from title
function extractGuest(title) {
  if (!title) return null;
  
  const titlePatterns = /(?:대표|박사|CIO|CEO|CFO|COO|CTO|이사|본부장|팀장|차장|교수|연구원|애널리스트|위원|소장|원장|부장|실장|센터장|전문가|전무|상무|부사장|사장|회장|총괄|디렉터|매니저|파트너|대표이사|수석|선임|책임|연구위원|작가|기자|총괄|PM)/;
  
  // Strategy: find Korean name (2-4 chars) followed by affiliation+title pattern
  // Try after separator first
  const sepIdx = Math.max(title.lastIndexOf('ㅣ'), title.lastIndexOf('|'), title.lastIndexOf('⎮'));
  
  let searchArea = title;
  if (sepIdx >= 0) {
    searchArea = title.substring(sepIdx + 1).trim();
  }
  
  // Pattern: "이름 소속 직함" or "이름 직함"  
  // Also handle: "'사토시 테라피' 저자 거스 쿤 작가" - foreign names, skip
  // Focus on Korean names: 2-4 hangul chars
  
  // Try multiple patterns
  const patterns = [
    // "정주용 그래비티벤처스 CIO" or "강정수 박사 블루닷AI"
    /([가-힣]{2,4})\s+(?:[가-힣a-zA-Z0-9]+\s+)?(?:대표|박사|CIO|CEO|CFO|COO|CTO|이사|본부장|팀장|차장|교수|연구원|애널리스트|위원|소장|원장|부장|실장|센터장|전문가|전무|상무|부사장|사장|회장|총괄|디렉터|매니저|파트너|대표이사|수석|선임|책임|연구위원|작가|기자|총괄|PM)/,
    // "이름 소속 직함" with more affiliation words
    /([가-힣]{2,4})\s+[가-힣a-zA-Z0-9]+(?:\s+[가-힣a-zA-Z0-9]+)*\s+(?:대표|박사|CIO|CEO|CFO|COO|CTO|이사|본부장|팀장|차장|교수|연구원|애널리스트|위원|소장|원장|부장|실장|센터장|전문가|전무|상무|부사장|사장|회장|총괄|디렉터|매니저|파트너|대표이사|수석|선임|책임|연구위원|작가|기자|총괄|PM)/,
  ];
  
  // First try in the area after separator
  for (const pat of patterns) {
    const m = searchArea.match(pat);
    if (m && m[1] !== '이효석') {
      return { name: m[1], context: searchArea };
    }
  }
  
  // Also try in brackets: [이정윤 세무사 4부] or (팔라티노 프라이빗에쿼티)
  // And try full title if no separator
  if (sepIdx < 0) {
    for (const pat of patterns) {
      const m = title.match(pat);
      if (m && m[1] !== '이효석') {
        return { name: m[1], context: title };
      }
    }
  }
  
  // Try patterns like "ft. name" or "w. name" or "feat. name"
  const ftMatch = title.match(/(?:ft\.|feat\.|w\.)\s*([가-힣]{2,4})\s/i);
  if (ftMatch && ftMatch[1] !== '이효석') {
    return { name: ftMatch[1], context: title };
  }
  
  return null;
}

function extractAffiliationTitle(context, name) {
  // Find the name position and extract what follows
  const idx = context.indexOf(name);
  if (idx < 0) return { affiliation: '', title: '' };
  
  let after = context.substring(idx + name.length).trim();
  // Remove brackets
  after = after.replace(/\[.*?\]/g, '').replace(/\(.*?\)/g, '').trim();
  
  const titleWords = ['대표', '박사', 'CIO', 'CEO', 'CFO', 'COO', 'CTO', '이사', '본부장', '팀장', 
    '차장', '교수', '연구원', '애널리스트', '위원', '소장', '원장', '부장', '실장', '센터장',
    '전문가', '전무', '상무', '부사장', '사장', '회장', '총괄', '디렉터', '매니저', '파트너', 
    '대표이사', '수석', '선임', '책임', '연구위원', '작가', '기자', 'PM'];
  
  let foundTitle = '';
  let affiliation = '';
  
  for (const tw of titleWords) {
    const tidx = after.indexOf(tw);
    if (tidx >= 0) {
      foundTitle = tw;
      affiliation = after.substring(0, tidx).trim();
      break;
    }
  }
  
  return { affiliation, title: foundTitle };
}

// Process
const guestMap = {};
let guestVideoCount = 0;
let totalAffectedSignals = 0;

for (const video of allVideos) {
  const result = extractGuest(video.title);
  if (!result) continue;
  
  guestVideoCount++;
  const { name, context } = result;
  const { affiliation, title } = extractAffiliationTitle(context, name);
  const sc = signalCounts[video.id] || 0;
  totalAffectedSignals += sc;
  
  if (!guestMap[name]) {
    guestMap[name] = { name, affiliation, title, videos: [], total_signals: 0 };
  }
  if (!guestMap[name].affiliation && affiliation) guestMap[name].affiliation = affiliation;
  if (!guestMap[name].title && title) guestMap[name].title = title;
  
  guestMap[name].videos.push({ video_id: video.id, title: video.title, signal_count: sc });
  guestMap[name].total_signals += sc;
}

const guests = Object.values(guestMap).sort((a, b) => b.videos.length - a.videos.length);

// Validate names
for (const g of guests) {
  if (!/^[가-힣]{2,4}$/.test(g.name)) {
    console.warn(`WARNING: Bad name: "${g.name}"`);
  }
}

const output = {
  summary: { total_videos: allVideos.length, guest_videos: guestVideoCount, unique_guests: guests.length, total_affected_signals: totalAffectedSignals },
  guests
};

import { writeFileSync, mkdirSync } from 'fs';
mkdirSync('data', { recursive: true });
writeFileSync('data/hs_guest_signals_v2.json', JSON.stringify(output, null, 2), 'utf-8');

console.log('\n=== Summary ===');
console.log(JSON.stringify(output.summary, null, 2));
console.log('\n=== Guests ===');
for (const g of guests) {
  console.log(`${g.name} | ${g.affiliation} ${g.title} | ${g.videos.length} videos | ${g.total_signals} signals`);
  for (const v of g.videos) console.log(`  - ${v.title}`);
}
