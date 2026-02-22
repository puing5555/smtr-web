# Tunnel Watchdog - 터널 자동 재시작
# Usage: powershell -ExecutionPolicy Bypass -File tunnel-watchdog.ps1

$tunnels = @(
    @{ Port = 8899; Subdomain = "smtr-sonnet"; Name = "Sonnet Review" }
)

$procs = @{}

function Start-Tunnel($t) {
    $p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npx localtunnel --port $($t.Port) --subdomain $($t.Subdomain)" -PassThru -WindowStyle Hidden
    $procs[$t.Subdomain] = $p
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Started tunnel $($t.Name) -> $($t.Subdomain).loca.lt (PID: $($p.Id))"
}

function Test-Tunnel($t) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$($t.Port)" -UseBasicParsing -TimeoutSec 3
        # Local server is up, now check tunnel
        $r2 = Invoke-WebRequest -Uri "https://$($t.Subdomain).loca.lt" -UseBasicParsing -TimeoutSec 10
        return $r2.StatusCode -eq 200
    } catch {
        return $false
    }
}

Write-Host "=== Tunnel Watchdog Started ==="
Write-Host "Monitoring tunnels every 30 seconds..."

# Initial start
foreach ($t in $tunnels) {
    Start-Tunnel $t
}

while ($true) {
    Start-Sleep -Seconds 30
    foreach ($t in $tunnels) {
        $alive = Test-Tunnel $t
        if (-not $alive) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Tunnel $($t.Name) is DOWN! Restarting..."
            $p = $procs[$t.Subdomain]
            if ($p -and !$p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
            Start-Sleep 2
            Start-Tunnel $t
        }
    }
}
