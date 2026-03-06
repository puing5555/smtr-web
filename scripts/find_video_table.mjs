import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

async function findVideoTable() {
  console.log('🔍 Looking for video table with subtitle data...\n');
  
  const candidateTables = [
    'video_metadata',
    'scraped_videos', 
    'video_transcripts',
    'youtube_data',
    'channel_videos',
    'content'
  ];
  
  for (const tableName of candidateTables) {
    try {
      console.log(`\n📋 Checking table: ${tableName}`);
      
      // Get a sample row to see structure
      const { data, error } = await supabase
        .from(tableName)
        .select('*')
        .limit(1);
        
      if (error) {
        console.log(`   ❌ Error: ${error.message}`);
        continue;
      }
      
      if (!data || data.length === 0) {
        console.log(`   ⚠️  Table is empty`);
        continue;
      }
      
      const sampleRow = data[0];
      const columns = Object.keys(sampleRow);
      console.log(`   📝 Columns (${columns.length}):`, columns.slice(0, 15).join(', '));
      
      // Check for subtitle-related columns
      const subtitleColumns = columns.filter(col => 
        col.toLowerCase().includes('subtitle') || 
        col.toLowerCase().includes('transcript') ||
        col.toLowerCase().includes('text') ||
        col.toLowerCase().includes('caption')
      );
      
      if (subtitleColumns.length > 0) {
        console.log(`   🎯 Subtitle-related columns:`, subtitleColumns);
        
        // Check if it has video_id or similar
        const idColumns = columns.filter(col => 
          col.toLowerCase().includes('video_id') ||
          col.toLowerCase().includes('id') ||
          col.toLowerCase().includes('youtube_id')
        );
        console.log(`   🆔 ID columns:`, idColumns);
        
        // Sample the subtitle content
        const subtitleCol = subtitleColumns[0];
        if (sampleRow[subtitleCol]) {
          const preview = sampleRow[subtitleCol].toString().substring(0, 200);
          console.log(`   📄 Sample content (${subtitleCol}):`, preview + '...');
        }
      }
      
    } catch (e) {
      console.log(`   ❌ Exception: ${e.message}`);
    }
  }
  
  // Also check if we can find videos that match signals by looking for matching video_ids
  console.log('\n🔗 Checking for video_id matches with signals...');
  
  // Get a few video_ids from signals
  const { data: signalVideoIds } = await supabase
    .from('influencer_signals')
    .select('video_id')
    .limit(5);
    
  if (signalVideoIds && signalVideoIds.length > 0) {
    const testVideoId = signalVideoIds[0].video_id;
    console.log(`\n🧪 Testing with video_id: ${testVideoId}`);
    
    for (const tableName of candidateTables) {
      try {
        const { data, error } = await supabase
          .from(tableName)
          .select('*')
          .eq('video_id', testVideoId)
          .limit(1);
          
        if (!error && data && data.length > 0) {
          console.log(`✅ Found matching video in '${tableName}' table!`);
          console.log(`   Columns:`, Object.keys(data[0]));
          
          // Check for subtitle fields
          const subtitleFields = Object.keys(data[0]).filter(col => 
            col.toLowerCase().includes('subtitle') || 
            col.toLowerCase().includes('transcript') ||
            col.toLowerCase().includes('text')
          );
          console.log(`   📝 Subtitle fields:`, subtitleFields);
        }
      } catch (e) {
        // Table might not have video_id column, that's ok
      }
    }
  }
}

findVideoTable().catch(console.error);