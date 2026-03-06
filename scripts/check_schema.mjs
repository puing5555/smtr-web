import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

async function checkSchema() {
  console.log('🔍 Checking database schema...\n');
  
  try {
    // Use RPC to get table information
    const { data, error } = await supabase.rpc('get_tables_info');
    
    if (error) {
      console.log('❌ RPC error:', error.message);
      
      // Try direct SQL query instead
      console.log('Trying direct SQL query...');
      const { data: tables, error: sqlError } = await supabase
        .from('information_schema.tables')
        .select('table_name')
        .eq('table_schema', 'public');
        
      if (sqlError) {
        console.log('❌ SQL error:', sqlError.message);
        
        // Last resort: try some manual table checking
        console.log('\nTrying manual table discovery...');
        
        const commonTables = [
          'influencer_signals',
          'signals', 
          'videos',
          'youtube_videos',
          'video_data',
          'transcripts',
          'subtitles'
        ];
        
        for (const table of commonTables) {
          try {
            const { count, error } = await supabase
              .from(table)
              .select('*', { count: 'exact', head: true });
              
            if (!error) {
              console.log(`✅ Table '${table}' exists with ${count} rows`);
              
              // Get column info
              const { data: sample } = await supabase
                .from(table)
                .select('*')
                .limit(1);
                
              if (sample && sample.length > 0) {
                console.log(`   Columns:`, Object.keys(sample[0]).join(', '));
              }
            }
          } catch (e) {
            // Skip
          }
        }
        
      } else {
        console.log('✅ Available tables:', tables);
      }
    } else {
      console.log('✅ Tables info:', data);
    }
    
  } catch (e) {
    console.log('❌ General error:', e.message);
  }
  
  // Let's also check what we can access from the signals table to understand the data structure
  console.log('\n🎯 Analyzing existing signals to understand data structure...');
  
  try {
    const { data: signals } = await supabase
      .from('influencer_signals')
      .select('video_id, stock, signal, key_quote, created_at')
      .not('key_quote', 'is', null)
      .limit(5);
      
    if (signals && signals.length > 0) {
      console.log(`\n📊 Sample signals with video_ids:`);
      signals.forEach((s, i) => {
        console.log(`${i+1}. Video: ${s.video_id}`);
        console.log(`   Stock: ${s.stock} (${s.signal})`);
        console.log(`   Quote: ${s.key_quote ? s.key_quote.substring(0, 100) : 'N/A'}...`);
        console.log(`   Date: ${s.created_at}`);
        console.log('');
      });
    }
    
    // Count signals by has_subtitle equivalent (check if key_quote exists and is meaningful)
    const { count: totalSignals } = await supabase
      .from('influencer_signals')
      .select('*', { count: 'exact', head: true });
      
    const { count: signalsWithQuotes } = await supabase
      .from('influencer_signals')
      .select('*', { count: 'exact', head: true })
      .not('key_quote', 'is', null)
      .neq('key_quote', '');
      
    console.log(`📈 Total signals: ${totalSignals}`);
    console.log(`📝 Signals with quotes: ${signalsWithQuotes}`);
    
  } catch (e) {
    console.log('❌ Error analyzing signals:', e.message);
  }
}

checkSchema().catch(console.error);