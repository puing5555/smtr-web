const{createClient}=require('@supabase/supabase-js');
const fs=require('fs');
const env=fs.readFileSync('invest-sns/.env.local','utf8');
const url=env.match(/NEXT_PUBLIC_SUPABASE_URL=(.+)/)[1].trim();
const key=env.match(/NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)/)[1].trim();
const s=createClient(url,key);

(async()=>{
  // Get existing hs_academy videos
  const{data:ch}=await s.from('influencer_channels').select('id').eq('channel_name','이효석아카데미');
  console.log('Channel:', ch);
  
  if(!ch || !ch.length) {
    console.log('이효석아카데미 channel not found, checking all channels...');
    const{data:all}=await s.from('influencer_channels').select('id,channel_name');
    console.log(JSON.stringify(all));
    return;
  }
  
  const chId = ch[0].id;
  const{data:vids}=await s.from('influencer_videos').select('video_id').eq('channel_id',chId);
  const existing = new Set(vids.map(v=>v.video_id));
  console.log('Existing videos in DB:', existing.size);
  
  // Read filtered list
  const lines = fs.readFileSync('hs_academy_stock_filtered.tsv','utf8').trim().split('\n');
  console.log('Filtered candidates:', lines.length);
  
  let newCount = 0;
  let dupCount = 0;
  const newVideos = [];
  for(const line of lines) {
    const [vidId, title, date, stocks] = line.split('\t');
    if(existing.has(vidId)) {
      dupCount++;
    } else {
      newCount++;
      newVideos.push({vidId, title, stocks});
    }
  }
  
  console.log('Duplicates:', dupCount);
  console.log('New videos:', newCount);
  
  // Save new list
  fs.writeFileSync('hs_academy_new.tsv', newVideos.map(v=>`${v.vidId}\t${v.title}\t${v.stocks}`).join('\n'));
})();
