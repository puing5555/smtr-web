const { execSync } = require('child_process');
const https = require('https');

const records = [
  {"id":"56397b20-1370-4356-a594-582801aaa990","video_id":"f519DUfXkzQ"},
  {"id":"0c091db6-bf7c-41ce-9fc9-18c4fcfa59b1","video_id":"1NUkBQ9MQf8"},
  {"id":"8b67a8d4-700f-4c55-a6f6-ce1c67ebc51a","video_id":"IaPiVGPNZBo"},
  {"id":"c2e2f686-4a22-487a-9ecb-d263c558ce84","video_id":"IjDhjDgC4Ao"},
  {"id":"fe60b18c-21e6-4931-9c79-01ef495000a8","video_id":"1iuRuDfMLUE"},
  {"id":"74ba83fe-6f5f-4455-a676-447c24c7ef76","video_id":"Sb3FpphamPo"},
  {"id":"816200ae-bf67-44dc-83e4-861a88f6922a","video_id":"JzzXPN5v1BI"},
  {"id":"d2a285d8-b854-4e9d-ac30-9eb12de52971","video_id":"DCpdPagMLbQ"},
  {"id":"4f4e40d8-7bf5-462b-a15b-ce25eb43998c","video_id":"yDsIEp4Wxvw"},
  {"id":"792b4754-582e-4848-bbef-6c4866e4c673","video_id":"YJ8yppl7d2s"},
  {"id":"eafcf7ff-15ad-4537-84c0-0ab5ec3cf64c","video_id":"79PFFmQQjOw"},
  {"id":"851da4cf-98ab-4cc6-86c8-09ac1603d958","video_id":"ydsOrytrdDg"},
  {"id":"af915cfd-0c7d-44d7-a479-216c4f3f007a","video_id":"_NOK3MvL3GA"},
  {"id":"f3751feb-6bca-4023-8293-dd6728db1e08","video_id":"cteX7UIEs3E"},
  {"id":"70f88e5b-2218-4f89-8c8d-05a6cd4bfc2c","video_id":"hapDG3KzK-E"},
  {"id":"b37c9505-7eba-4fc1-8dcb-72f201d48071","video_id":"2GAaGDOcB_s"},
  {"id":"a3f24dc7-9f7a-415a-a92d-d3c54af99162","video_id":"DUJQXaRCT2M"},
  {"id":"1c56ec7a-909a-446e-9a14-9a59793c66d6","video_id":"jqCPTMWYO7I"},
  {"id":"eb5750b6-0b1e-4b82-ae84-a0cc57108cf3","video_id":"gr7Rj7EH4PE"},
  {"id":"62e5cc63-58d0-40e4-8baf-bb0d27dfa046","video_id":"4bClsFvaoLs"},
  {"id":"29e24dd8-4568-48dd-a165-ed11c17c08e0","video_id":"NlWaAL3SOxE"},
  {"id":"8c2c51fb-1d5b-4e60-9c93-1dd8f5c01713","video_id":"qkpmS6yfO_g"},
  {"id":"97516367-db60-431c-b209-3fc66e5842bb","video_id":"KvuATAaRxe8"},
  {"id":"7386a76b-cb7f-40d3-9931-d9ca17eda81d","video_id":"CN_T1V1ocjg"},
  {"id":"5ac886a8-3912-471d-a95d-8ee6f9f5a6bb","video_id":"zRGNYWXHfV4"},
  {"id":"b77e82db-3f02-4d6b-8726-7db8dc67093a","video_id":"oiAMDjdr334"},
  {"id":"16aac04d-0cfc-416a-b86c-fcf14efb9bdd","video_id":"YbbV60KVe_c"},
  {"id":"8f58c059-55fc-4d6d-afec-6af790866346","video_id":"OadsiFLklsM"},
  {"id":"06b40681-5020-42c1-88ed-d76471a68dd1","video_id":"jXME1wXZDRU"}
];

const KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

function patch(id, date) {
  return new Promise((resolve) => {
    const body = JSON.stringify({ published_at: date });
    const opts = {
      hostname: 'arypzhotxflimroprmdk.supabase.co',
      path: `/rest/v1/influencer_videos?id=eq.${id}`,
      method: 'PATCH',
      headers: {
        'apikey': KEY,
        'Authorization': `Bearer ${KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
        'Content-Length': Buffer.byteLength(body)
      }
    };
    const req = https.request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => { console.log(`  PATCH ${id.slice(0,8)}: ${res.statusCode}`); resolve(res.statusCode); });
    });
    req.write(body);
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  let success = 0, fail = 0;
  for (const rec of records) {
    try {
      const dateStr = execSync(
        `python -m yt_dlp --get-filename -o "%(upload_date)s" "https://youtube.com/watch?v=${rec.video_id}"`,
        { encoding: 'utf8', timeout: 15000 }
      ).trim();
      if (/^\d{8}$/.test(dateStr)) {
        const iso = `${dateStr.slice(0,4)}-${dateStr.slice(4,6)}-${dateStr.slice(6,8)}T00:00:00Z`;
        console.log(`${rec.video_id}: ${iso}`);
        await patch(rec.id, iso);
        success++;
      } else {
        console.log(`${rec.video_id}: bad date "${dateStr}"`);
        fail++;
      }
    } catch(e) {
      console.log(`${rec.video_id}: ERROR ${e.message.slice(0,100)}`);
      fail++;
    }
    await sleep(2000);
  }
  console.log(`\nDone: ${success} success, ${fail} fail`);
}

main();
