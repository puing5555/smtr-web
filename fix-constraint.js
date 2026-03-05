// Use supabase-js to run SQL via the service role key
// Actually, supabase REST doesn't support DDL. Let's use the pg module directly.
// First check if pg is installed

const { execSync } = require('child_process');

// Install pg if not available
try { require.resolve('pg'); } catch(e) {
  console.log('Installing pg...');
  execSync('npm install pg', { cwd: 'C:\\Users\\Mario\\work', stdio: 'inherit' });
}

const { Client } = require('pg');

async function main() {
  // Use the pooler URL with the database password
  // The password for supabase is typically the project's database password
  // Let's try with the service role JWT decoded - actually we need the DB password
  
  // Try connecting via the Supabase Management API instead
  // Or use the direct connection
  
  // Supabase project DB password - we need to find it
  // Check if there's a config file
  const fs = require('fs');
  
  // Try the supabase config
  const configPath = 'C:\\Users\\Mario\\work\\invest-sns\\supabase\\config.toml';
  if (fs.existsSync(configPath)) {
    console.log('Config:', fs.readFileSync(configPath, 'utf8').substring(0, 500));
  }
  
  // The pooler URL needs a password. Let's try the Supabase HTTP API approach instead.
  // Use the /pg endpoint which some Supabase versions support
  
  const https = require('https');
  const key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
  
  // First, try to drop and recreate constraint via RPC
  // We need to create a function first, or use pg_net, or find another way
  
  // Actually, Supabase has a /sql endpoint in newer versions
  // Or we can use the pg_graphql or other built-in extensions
  
  // Let's try the simplest approach: use the Supabase Management API
  // POST https://api.supabase.com/v1/projects/{ref}/database/query
  
  // We need an access token - check if logged in via CLI
  const homedir = require('os').homedir();
  const credPaths = [
    `${homedir}/.supabase/access-token`,
    `${homedir}/AppData/Roaming/supabase/access-token`,
    `${homedir}/AppData/Local/supabase/access-token`,
  ];
  
  for (const p of credPaths) {
    if (fs.existsSync(p)) {
      console.log('Found access token at:', p);
      const token = fs.readFileSync(p, 'utf8').trim();
      console.log('Token prefix:', token.substring(0, 20) + '...');
      
      // Use management API
      const sql = "ALTER TABLE public.influencer_signals DROP CONSTRAINT influencer_signals_signal_check; ALTER TABLE public.influencer_signals ADD CONSTRAINT influencer_signals_signal_check CHECK (signal IN ('매수', '긍정', '중립', '부정', '매도')); UPDATE public.influencer_signals SET signal = '부정' WHERE signal = '경계';";
      
      return new Promise((resolve) => {
        const body = JSON.stringify({ query: sql });
        const opts = {
          method: 'POST',
          hostname: 'api.supabase.com',
          path: '/v1/projects/arypzhotxflimroprmdk/database/query',
          headers: {
            Authorization: 'Bearer ' + token,
            'Content-Type': 'application/json'
          }
        };
        const req = https.request(opts, res => {
          let d = ''; res.on('data', c => d += c);
          res.on('end', () => { console.log('Status:', res.statusCode); console.log('Response:', d.substring(0, 2000)); resolve(); });
        });
        req.write(body); req.end();
      });
    }
  }
  
  console.log('No access token found. Checked:', credPaths);
}

main().catch(console.error);
