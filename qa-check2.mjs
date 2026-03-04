
const BASE='https://arypzhotxflimroprmdk.supabase.co';
const KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';
const h={apikey:KEY,Authorization:'Bearer '+KEY};
async function run(){
  const ids=['f6b446a0-7981-4ce8-a167-0800ad573c91','8d9ed587-6a49-45bb-b363-2c33a01522d1','d400188d-0f98-49b1-90fc-049041c18e98','69641510-829c-4ead-a6ff-af85b04a76f9','7357a4d5-9450-4dbc-aa98-30106b945175','cfc9e60f-5bae-45c5-8e57-8f624f79298c','3e3a4ffc-db30-48f7-8919-e114098945d2'];
  const q=ids.map(id=>'"'+id+'"').join(',');
  let r=await fetch(BASE+'/rest/v1/influencer_videos?select=id,youtube_id,title,published_at&id=in.('+q+')',{headers:h});
  let vids=await r.json();
  console.log(JSON.stringify(vids, null, 2));
}
run();
