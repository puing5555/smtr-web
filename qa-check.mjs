
const BASE='https://arypzhotxflimroprmdk.supabase.co';
const KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const h={apikey:KEY,Authorization:'Bearer '+KEY};

async function run(){
  // Get video IDs for 이효석
  let r=await fetch(BASE+'/rest/v1/influencer_videos?select=id&channel_id=eq.d153b75b-1843-4a99-b49f-c31081a8f566&limit=5000',{headers:h});
  let vids=await r.json();
  let vidIds=vids.map(v=>v.id);
  console.log('Videos count:',vidIds.length);

  // Get all signals in batches
  let allSignals=[];
  for(let i=0;i<vidIds.length;i+=100){
    let batch=vidIds.slice(i,i+100);
    let q=batch.map(id=>'"'+id+'"').join(',');
    let r2=await fetch(BASE+'/rest/v1/influencer_signals?select=id,stock,ticker,signal,key_quote,timestamp,confidence,video_id,created_at&video_id=in.('+q+')&limit=5000',{headers:h});
    let sigs=await r2.json();
    allSignals.push(...sigs);
  }
  console.log('Total 이효석 signals:',allSignals.length);

  // Random 20
  let shuffled=[...allSignals].sort(()=>Math.random()-0.5);
  let sample=shuffled.slice(0,20);
  console.log('\n=== TASK 1: RANDOM 20 SIGNALS ===');
  sample.forEach((s,i)=>{
    let kq=(s.key_quote||'').substring(0,30);
    console.log(JSON.stringify({n:i+1,stock:s.stock,ticker:s.ticker,signal:s.signal,kq,ts:s.timestamp,created:s.created_at}));
  });

  // Task 2: stock counts
  console.log('\n=== TASK 2: STOCK COUNTS (이효석) ===');
  let counts={};
  allSignals.forEach(s=>{counts[s.stock]=(counts[s.stock]||0)+1});
  let sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]);
  sorted.slice(0,15).forEach(([k,v])=>console.log(k+': '+v));

  // Task 2b: ALL DB counts
  console.log('\n=== TASK 2b: ALL DB STOCK COUNTS ===');
  let allSigs=[];
  let offset=0;
  while(true){
    let r3=await fetch(BASE+'/rest/v1/influencer_signals?select=stock&limit=1000&offset='+offset,{headers:h});
    let batch=await r3.json();
    if(!batch.length) break;
    allSigs.push(...batch);
    offset+=1000;
    if(batch.length<1000) break;
  }
  console.log('Total DB signals:',allSigs.length);
  let allCounts={};
  allSigs.forEach(s=>{allCounts[s.stock]=(allCounts[s.stock]||0)+1});
  let allSorted=Object.entries(allCounts).sort((a,b)=>b[1]-a[1]);
  allSorted.slice(0,15).forEach(([k,v])=>console.log(k+': '+v));

  // Task 3: 5 random video IDs
  console.log('\n=== TASK 3: VIDEO SAMPLES ===');
  let vidSample=shuffled.slice(0,5);
  vidSample.forEach((s,i)=>{
    console.log(JSON.stringify({n:i+1,video_id:s.video_id,timestamp:s.timestamp,stock:s.stock}));
  });

  // Task 4: edge cases
  console.log('\n=== TASK 4a: OLDEST 3 ===');
  // oldest among 이효석 signals
  let sortedByDate=[...allSignals].sort((a,b)=>new Date(a.created_at)-new Date(b.created_at));
  sortedByDate.slice(0,3).forEach(s=>console.log(JSON.stringify({id:s.id,stock:s.stock,signal:s.signal,created_at:s.created_at,video_id:s.video_id})));

  console.log('\n=== TASK 4b: NEWEST 3 ===');
  sortedByDate.slice(-3).forEach(s=>console.log(JSON.stringify({id:s.id,stock:s.stock,signal:s.signal,created_at:s.created_at,video_id:s.video_id})));
}
run().catch(e=>console.error(e));
