# Map video summaries from signal-review data to corinpapa signals

# First, extract the SIGNALS_DATA from the HTML file
$htmlContent = Get-Content "C:\Users\Mario\work\smtr-web\signal-review-v3.html" -Raw
$startPattern = "const SIGNALS_DATA = \["
$endPattern = "\];"
$start = $htmlContent.IndexOf($startPattern)
$end = $htmlContent.IndexOf($endPattern, $start)

if ($start -eq -1 -or $end -eq -1) {
    Write-Error "Could not find SIGNALS_DATA array"
    exit 1
}

# Extract and parse the JSON array
$jsonString = $htmlContent.Substring($start + $startPattern.Length, $end - $start - $startPattern.Length)
$jsonString = "[$jsonString]"

try {
    $signalsData = $jsonString | ConvertFrom-Json
    Write-Host "Found $($signalsData.Length) signals in review data"
} catch {
    Write-Error "Failed to parse signals data: $_"
    exit 1
}

# Create video summary mapping
$videoSummaryMap = @{}
foreach ($signal in $signalsData) {
    if ($signal.video_summary -and $signal.video_id) {
        $videoId = $signal.video_id
        if (-not $videoSummaryMap.ContainsKey($videoId)) {
            $videoSummaryMap[$videoId] = $signal.video_summary
        }
    }
}

Write-Host "Created mapping for $($videoSummaryMap.Count) unique video summaries"

# Read the current corinpapa signals file
$corinpapaFile = "C:\Users\Mario\work\invest-sns\src\data\corinpapa-signals.ts"
$content = Get-Content $corinpapaFile -Raw

# Function to extract video ID from YouTube URL
function Extract-VideoId {
    param($youtubeUrl)
    if ($youtubeUrl -match "v=([a-zA-Z0-9_-]+)") {
        return $matches[1]
    }
    return $null
}

# Parse the TypeScript file to find signals
$lines = $content -split "`n"
$updatedLines = @()
$inSignal = $false
$currentSignal = ""

for ($i = 0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]
    
    # Check if we're starting a new signal object
    if ($line.Trim() -eq "{" -and $inSignal -eq $false -and $lines[$i-1].Trim() -match '^\d+,?\s*$') {
        $inSignal = $true
        $currentSignal = ""
    }
    
    if ($inSignal) {
        $currentSignal += $line + "`n"
        
        # Check if this line contains the youtubeLink
        if ($line -match '"youtubeLink":\s*"([^"]+)"') {
            $youtubeUrl = $matches[1]
            $videoId = Extract-VideoId -youtubeUrl $youtubeUrl
            
            if ($videoId -and $videoSummaryMap.ContainsKey($videoId)) {
                $videoSummary = $videoSummaryMap[$videoId]
                # Escape quotes in the summary
                $videoSummary = $videoSummary -replace '"', '\"'
                
                # Add videoSummary field before the closing brace
                $summaryLine = '  "videoSummary": "' + $videoSummary + '",'
                $updatedLines += $line
                $updatedLines += $summaryLine
                Write-Host "Added video summary for video ID: $videoId"
                continue
            }
        }
        
        # Check if we're ending the signal object
        if ($line.Trim() -eq "}" -or $line.Trim() -eq "},") {
            $inSignal = $false
            $currentSignal = ""
        }
    }
    
    $updatedLines += $line
}

# Write the updated content
$updatedContent = $updatedLines -join "`n"
$updatedContent | Set-Content $corinpapaFile -Encoding UTF8

Write-Host "Updated corinpapa-signals.ts with video summaries"