
import fetch from 'node-fetch';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const headers = {
  'apikey': SUPABASE_KEY,
  'Authorization': `Bearer ${SUPABASE_KEY}`,
  'Content-Type': 'application/json'
};

async function query(table, params = '') {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${params}`, { headers });
  return res.json();
}

// 1. Get channel_id for 이효석아카데미
const channels = await query('influencer_videos', 'select=channel_id,channel_name&channel_name=eq.이효석아카데미&limit=1');
if (!channels.length) { console.error('Channel not found'); process.exit(1); }
const channelId = channels[0].channel_id;
console.log('Channel ID:', channelId);

// 2. Get all videos
let allVideos = [];
let offset = 0;
while (true) {
  const batch = await query('influencer_videos', `select=id,title,published_at&channel_id=eq.${channelId}&order=published_at.desc&offset=${offset}&limit=1000`);
  allVideos.push(...batch);
  if (batch.length < 1000) break;
  offset += 1000;
}
console.log('Total videos:', allVideos.length);

// 3. Get signal counts per video
let allSignals = [];
offset = 0;
while (true) {
  const batch = await query('influencer_signals', `select=video_id&video_id=not.is.null&offset=${offset}&limit=1000`);
  allSignals.push(...batch);
  if (batch.length < 1000) break;
  offset += 1000;
}

// Count signals per video
const signalCounts = {};
for (const s of allSignals) {
  signalCounts[s.video_id] = (signalCounts[s.video_id] || 0) + 1;
}

// 4. Extract guest names from titles
function extractGuest(title) {
  if (!title) return null;
  
  // Pattern 1: After ㅣ or |
  const separatorMatch = title.match(/[ㅣ|]\s*([가-힣]{2,4})\s+(?:[가-힣a-zA-Z0-9\s]+\s+)?(?:대표|박사|CIO|CEO|CFO|COO|CTO|이사|본부장|팀장|차장|교수|연구원|애널리스트|위원|소장|원장|부장|실장|센터장|전문가|전무|상무|부사장|사장|회장|총괄|디렉터|매니저|파트너|대표이사|수석|선임|책임)/);
  if (separatorMatch) {
    const name = separatorMatch[1];
    if (name !== '이효석') return { name, afterSep: title.split(/[ㅣ|]/).slice(1).join('|').trim() };
  }
  
  // Pattern 2: After ㅣ or |, name followed by affiliation
  const sepParts = title.split(/[ㅣ|]/);
  if (sepParts.length > 1) {
    const after = sepParts.slice(1).join('|').trim();
    const nameMatch = after.match(/^([가-힣]{2,4})\s/);
    if (nameMatch && nameMatch[1] !== '이효석') {
      return { name: nameMatch[1], afterSep: after };
    }
  }
  
  // Pattern 3: Title starts with name + title
  const startMatch = title.match(/^([가-힣]{2,4})\s+(?:대표|박사|CIO|CEO|이사|본부장|팀장|차장|교수|연구원|애널리스트|위원|소장|원장)/);
  if (startMatch && startMatch[1] !== '이효석') {
    return { name: startMatch[1], afterSep: title };
  }
  
  return null;
}

function extractAffiliationAndTitle(text, guestName) {
  if (!text) return { affiliation: '', title: '' };
  
  // Remove name from start
  let remaining = text.replace(new RegExp(`^${guestName}\\s*`), '').trim();
  
  // Remove [1부], [2부], [풀영상] etc
  remaining = remaining.replace(/\[.*?\]/g, '').trim();
  
  const titlePatterns = ['대표', '박사', 'CIO', 'CEO', 'CFO', 'COO', 'CTO', '이사', '본부장', '팀장', 
    '차장', '교수', '연구원', '애널리스트', '위원', '소장', '원장', '부장', '실장', '센터장',
    '전문가', '전무', '상무', '부사장', '사장', '회장', '총괄', '디렉터', '매니저', '파트너', 
    '대표이사', '수석', '선임', '책임'];
  
  let foundTitle = '';
  let affiliation = '';
  
  for (const tp of titlePatterns) {
    const idx = remaining.indexOf(tp);
    if (idx >= 0) {
      foundTitle = tp;
      affiliation = remaining.substring(0, idx).trim();
      break;
    }
  }
  
  return { affiliation, title: foundTitle };
}

// Process all videos
const guestMap = {};
let guestVideoCount = 0;
let totalAffectedSignals = 0;

for (const video of allVideos) {
  const result = extractGuest(video.title);
  if (!result) continue;
  
  guestVideoCount++;
  const { name, afterSep } = result;
  const { affiliation, title } = extractAffiliationAndTitle(afterSep, name);
  const sc = signalCounts[video.id] || 0;
  totalAffectedSignals += sc;
  
  if (!guestMap[name]) {
    guestMap[name] = { name, affiliation, title, videos: [], total_signals: 0 };
  }
  
  // Update affiliation/title if we find better info
  if (!guestMap[name].affiliation && affiliation) guestMap[name].affiliation = affiliation;
  if (!guestMap[name].title && title) guestMap[name].title = title;
  
  guestMap[name].videos.push({ video_id: video.id, title: video.title, signal_count: sc });
  guestMap[name].total_signals += sc;
}

const guests = Object.values(guestMap).sort((a, b) => b.videos.length - a.videos.length);

const output = {
  summary: {
    total_videos: allVideos.length,
    guest_videos: guestVideoCount,
    unique_guests: guests.length,
    total_affected_signals: totalAffectedSignals
  },
  guests
};

// Validate: no guest name should look like truncated text
for (const g of guests) {
  if (!/^[가-힣]{2,4}$/.test(g.name)) {
    console.warn(`WARNING: Suspicious guest name: "${g.name}"`);
  }
}

import { writeFileSync, mkdirSync } from 'fs';
mkdirSync('data', { recursive: true });
writeFileSync('data/hs_guest_signals_v2.json', JSON.stringify(output, null, 2), 'utf-8');

console.log('\n=== Summary ===');
console.log(`Total videos: ${output.summary.total_videos}`);
console.log(`Guest videos: ${output.summary.guest_videos}`);
console.log(`Unique guests: ${output.summary.unique_guests}`);
console.log(`Total affected signals: ${output.summary.total_affected_signals}`);
console.log('\n=== Guests ===');
for (const g of guests) {
  console.log(`${g.name} (${g.affiliation} ${g.title}) - ${g.videos.length} videos, ${g.total_signals} signals`);
}
