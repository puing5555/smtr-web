import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

async function exploreDB() {
  console.log('=== Exploring Supabase Database ===\n');
  
  // Let's check the influencer_signals table first to understand the data structure
  console.log('🔍 Checking influencer_signals table...');
  try {
    const { data: signals, error } = await supabase
      .from('influencer_signals')
      .select('*')
      .limit(3);
      
    if (error) {
      console.log('❌ Error:', error.message);
    } else {
      console.log(`✅ Found ${signals.length} sample signals:`);
      signals.forEach((signal, i) => {
        console.log(`\nSignal ${i + 1}:`);
        console.log(`- video_id: ${signal.video_id}`);
        console.log(`- stock: ${signal.stock}`);
        console.log(`- signal: ${signal.signal}`);
        console.log(`- pipeline_version: ${signal.pipeline_version}`);
        console.log(`- created_at: ${signal.created_at}`);
      });
    }
  } catch (e) {
    console.log('❌ Error:', e.message);
  }

  // Get unique video_ids to understand the video ID pattern
  console.log('\n🎥 Getting unique video IDs...');
  try {
    const { data: videoIds, error } = await supabase
      .from('influencer_signals')
      .select('video_id')
      .limit(10);
      
    if (error) {
      console.log('❌ Error:', error.message);
    } else {
      const uniqueIds = [...new Set(videoIds.map(v => v.video_id))];
      console.log(`✅ Sample video IDs:`, uniqueIds.slice(0, 5));
    }
  } catch (e) {
    console.log('❌ Error:', e.message);
  }

  // Try other common table names
  const possibleTables = [
    'youtube_data', 
    'video_metadata', 
    'channel_videos',
    'scraped_videos',
    'content',
    'video_transcripts'
  ];
  
  console.log('\n📋 Checking other possible tables...');
  for (const tableName of possibleTables) {
    try {
      const { data, error, count } = await supabase
        .from(tableName)
        .select('*', { count: 'exact', head: true });
        
      if (!error) {
        console.log(`✅ Table '${tableName}' exists with ${count} rows`);
        
        // Get sample data to see columns
        const { data: sample } = await supabase
          .from(tableName)
          .select('*')
          .limit(1);
          
        if (sample && sample[0]) {
          console.log(`   Columns:`, Object.keys(sample[0]).slice(0, 10).join(', '));
        }
      }
    } catch (e) {
      // Table doesn't exist, continue
    }
  }
}

exploreDB().catch(console.error);