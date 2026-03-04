$eng = Get-Content "C:\Users\Mario\work\eng_titles.json" -Raw | ConvertFrom-Json
$url = "https://arypzhotxflimroprmdk.supabase.co"
$key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
$headers = @{"apikey"=$key;"Authorization"="Bearer $key";"Content-Type"="application/json";"Prefer"="return=minimal"}

$updated = 0
$failed = 0
$total = $eng.Count

for($i=0; $i -lt $total; $i++){
    $v = $eng[$i]
    $vid = $v.video_id
    
    # Rate limit: 2s between each, 10s rest after every 20
    if($i -gt 0 -and $i % 20 -eq 0){
        Write-Host "--- Resting 10s after $i videos ---"
        Start-Sleep -Seconds 10
    }
    
    try {
        $koTitle = & python -m yt_dlp --get-title --extractor-args "youtube:lang=ko" "https://youtube.com/watch?v=$vid" 2>$null
        if($koTitle -and $koTitle.Trim().Length -gt 0){
            $koTitle = $koTitle.Trim()
            # Check if it's actually different (has Korean chars)
            $asciiRatio = ($koTitle.ToCharArray() | Where-Object {[int]$_ -lt 128}).Count / [Math]::Max($koTitle.Length,1)
            if($asciiRatio -lt 0.7){
                # Update DB
                $body = @{"title"=$koTitle} | ConvertTo-Json -Compress
                Invoke-RestMethod "$url/rest/v1/influencer_videos?id=eq.$($v.id)" -Method Patch -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
                $updated++
                Write-Host "[$($i+1)/$total] UPDATED: $vid -> $koTitle"
            } else {
                Write-Host "[$($i+1)/$total] SKIP (still English): $vid -> $koTitle"
            }
        } else {
            $failed++
            Write-Host "[$($i+1)/$total] FAILED: $vid (no title returned)"
        }
    } catch {
        $failed++
        Write-Host "[$($i+1)/$total] ERROR: $vid - $_"
    }
    
    Start-Sleep -Seconds 2
}

Write-Host "`n=== DONE ==="
Write-Host "Updated: $updated / $total"
Write-Host "Failed: $failed"
# Save results
@{"updated"=$updated;"total"=$total;"failed"=$failed} | ConvertTo-Json | Out-File "C:\Users\Mario\work\title_update_result.json"
