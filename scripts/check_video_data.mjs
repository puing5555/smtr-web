import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

async function checkVideoData() {
  console.log('🎥 Analyzing video data structure...\n');
  
  // Get unique video_ids
  console.log('📊 Getting unique video IDs...');
  const { data: videoIds, error } = await supabase
    .from('influencer_signals')
    .select('video_id')
    .order('created_at', { ascending: false });
    
  if (error) {
    console.log('❌ Error:', error.message);
    return;
  }
  
  const uniqueVideoIds = [...new Set(videoIds.map(v => v.video_id))];
  console.log(`✅ Found ${uniqueVideoIds.length} unique videos from ${videoIds.length} signals`);
  
  // Check if we have tables that might contain video metadata or transcripts
  console.log('\n🔍 Checking for video metadata in other tables...');
  
  const testVideoId = uniqueVideoIds[0];
  console.log(`Testing with video_id: ${testVideoId}`);
  
  // Check the empty tables we found earlier
  const emptyTables = ['videos', 'youtube_videos', 'video_data', 'transcripts', 'subtitles'];
  
  for (const table of emptyTables) {
    try {
      console.log(`\nChecking ${table}...`);
      
      // Try to get any data
      const { data, error, count } = await supabase
        .from(table)
        .select('*', { count: 'exact' })
        .limit(5);
        
      if (error) {
        console.log(`   ❌ Error: ${error.message}`);
      } else {
        console.log(`   📊 Found ${count} rows`);
        if (data && data.length > 0) {
          console.log(`   📝 Sample columns:`, Object.keys(data[0]));
          
          // Check if any have video_id matching our test
          const matchingRows = data.filter(row => 
            Object.values(row).includes(testVideoId) ||
            Object.keys(row).some(key => key.includes('video'))
          );
          
          if (matchingRows.length > 0) {
            console.log(`   ✅ Found matching video data!`);
            console.log(`   Sample:`, matchingRows[0]);
          }
        }
      }
    } catch (e) {
      console.log(`   ❌ Exception: ${e.message}`);
    }
  }
  
  // Let's check the video distribution and see what we're working with
  console.log('\n📈 Analyzing video signal distribution...');
  
  // Group signals by video_id
  const videoSignalCounts = {};
  const videoTitles = {};
  
  for (const videoId of uniqueVideoIds.slice(0, 20)) { // Check first 20 videos
    const { data: signals } = await supabase
      .from('influencer_signals')
      .select('stock, signal, key_quote, reasoning')
      .eq('video_id', videoId);
      
    if (signals) {
      videoSignalCounts[videoId] = signals.length;
      
      // Try to extract video title from reasoning or key_quote
      const sampleQuote = signals[0]?.key_quote || '';
      videoTitles[videoId] = sampleQuote.substring(0, 50) + '...';
    }
  }
  
  console.log('\n📊 Sample videos and their signal counts:');
  Object.entries(videoSignalCounts).slice(0, 10).forEach(([videoId, count], i) => {
    console.log(`${i+1}. ${videoId}: ${count} signals`);
    console.log(`    Sample: ${videoTitles[videoId]}`);
  });
  
  // Check if there are any videos with many signals (might indicate rich transcript data)
  const videosWithManySignals = Object.entries(videoSignalCounts)
    .filter(([_, count]) => count >= 5)
    .sort((a, b) => b[1] - a[1]);
    
  console.log(`\n🎯 Videos with 5+ signals (${videosWithManySignals.length} videos):`);
  videosWithManySignals.slice(0, 5).forEach(([videoId, count], i) => {
    console.log(`${i+1}. ${videoId}: ${count} signals`);
  });
  
  if (videosWithManySignals.length > 0) {
    console.log('\n🔍 Analyzing a rich video in detail...');
    const [richVideoId] = videosWithManySignals[0];
    
    const { data: richSignals } = await supabase
      .from('influencer_signals')
      .select('*')
      .eq('video_id', richVideoId);
      
    if (richSignals) {
      console.log(`\n📝 Video ${richVideoId} details:`);
      console.log(`   Signals: ${richSignals.length}`);
      console.log(`   Stocks: ${[...new Set(richSignals.map(s => s.stock))].join(', ')}`);
      console.log(`   Signal types: ${[...new Set(richSignals.map(s => s.signal))].join(', ')}`);
      console.log(`   Total quote text length: ${richSignals.map(s => s.key_quote || '').join(' ').length} characters`);
    }
  }
}

checkVideoData().catch(console.error);