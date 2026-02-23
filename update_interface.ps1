# Update corinpapa-signals interface to include videoSummary

$corinpapaFile = "C:\Users\Mario\work\invest-sns\src\data\corinpapa-signals.ts"
$content = Get-Content $corinpapaFile -Raw

# Update the interface to include videoSummary
$updatedContent = $content -replace "hedged: boolean;", "hedged: boolean;`n  videoSummary?: string;"

# Write the updated content back to the file
$updatedContent | Set-Content $corinpapaFile -Encoding UTF8

Write-Host "Updated corinpapa-signals.ts interface with videoSummary field"