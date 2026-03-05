$headers = @{'apikey'='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'}
$base = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1'

$ch = Invoke-RestMethod "$base/influencer_channels?select=id,channel_name" -Headers $headers
foreach($c in $ch){ Write-Host "$($c.id) $($c.channel_name)" }

$vids = Invoke-RestMethod "$base/influencer_videos?select=id,channel_id,video_id,title&limit=1000" -Headers $headers
Write-Host "Total videos: $($vids.Count)"
foreach($g in ($vids | Group-Object channel_id)){ Write-Host "ch $($g.Name): $($g.Count)" }
