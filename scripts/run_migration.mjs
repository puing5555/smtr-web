import https from 'https';
import fs from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const sql = fs.readFileSync('C:\\Users\\Mario\\work\\invest-sns\\supabase\\migrations\\001_user_dashboard.sql', 'utf-8');

// Split into individual statements and execute via rpc
// First check if we can use the pg_net or query endpoint
const body = JSON.stringify({ query: sql });

const req = https.request({
  hostname: 'arypzhotxflimroprmdk.supabase.co',
  path: '/rest/v1/rpc/exec_sql',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'apikey': SERVICE_KEY,
    'Authorization': `Bearer ${SERVICE_KEY}`,
  }
}, res => {
  let d = '';
  res.on('data', c => d += c);
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    console.log('Response:', d.substring(0, 500));
    
    if (res.statusCode !== 200) {
      console.log('\nTrying individual CREATE TABLE statements...');
      // Extract CREATE TABLE statements
      const stmts = sql.split(';').filter(s => s.trim().length > 10);
      console.log(`Found ${stmts.length} statements`);
      console.log('SQL must be run manually in Supabase Dashboard SQL Editor');
    }
  });
});
req.on('error', e => console.error('Error:', e.message));
req.write(body);
req.end();
