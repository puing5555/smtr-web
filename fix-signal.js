const https = require('https');
const key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

function runSQL(sql) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ query: sql });
    const opts = {
      method: 'POST',
      hostname: 'arypzhotxflimroprmdk.supabase.co',
      path: '/rest/v1/rpc/exec_sql',
      headers: { apikey: key, Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' }
    };
    const req = https.request(opts, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.write(body); req.end();
  });
}

function supaRest(method, path, body) {
  return new Promise((resolve, reject) => {
    const opts = {
      method,
      hostname: 'arypzhotxflimroprmdk.supabase.co',
      path: '/rest/v1/' + path,
      headers: { apikey: key, Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', Prefer: 'return=minimal' }
    };
    const req = https.request(opts, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function main() {
  // We need to use the Supabase Management API to run DDL
  // Try using the database connection string directly via pg
  // Or use the Supabase dashboard SQL editor API
  
  // Actually, let's try the management API
  const mgmtKey = process.env.SUPABASE_ACCESS_TOKEN;
  const projectRef = 'arypzhotxflimroprmdk';
  
  const sql = "ALTER TABLE public.influencer_signals DROP CONSTRAINT influencer_signals_signal_check; ALTER TABLE public.influencer_signals ADD CONSTRAINT influencer_signals_signal_check CHECK (signal IN ('매수', '긍정', '중립', '부정', '매도')); UPDATE public.influencer_signals SET signal = '부정' WHERE signal = '경계';";
  
  const body = JSON.stringify({ query: sql });
  
  return new Promise((resolve) => {
    const opts = {
      method: 'POST',
      hostname: 'api.supabase.com',
      path: `/v1/projects/${projectRef}/database/query`,
      headers: {
        Authorization: 'Bearer ' + mgmtKey,
        'Content-Type': 'application/json'
      }
    };
    const req = https.request(opts, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { console.log(res.statusCode, d.substring(0, 2000)); resolve(); });
    });
    req.write(body); req.end();
  });
}

main();
