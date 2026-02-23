# Extract video summaries from signal-review-v3.html and map to corinpapa-signals

# Read the HTML file and extract SIGNALS_DATA
$htmlContent = Get-Content "C:\Users\Mario\work\smtr-web\signal-review-v3.html" -Raw
$startPattern = "const SIGNALS_DATA = \["
$endPattern = "\];"
$start = $htmlContent.IndexOf($startPattern)
$end = $htmlContent.IndexOf($endPattern, $start)

if ($start -eq -1 -or $end -eq -1) {
    Write-Error "Could not find SIGNALS_DATA array"
    exit 1
}

# Extract the JSON array
$jsonString = $htmlContent.Substring($start + $startPattern.Length, $end - $start - $startPattern.Length)
$jsonString = "[$jsonString]"

# Parse JSON
try {
    $signalsData = $jsonString | ConvertFrom-Json
    Write-Host "Found $($signalsData.Length) signals in review data"
} catch {
    Write-Error "Failed to parse signals data: $_"
    exit 1
}

# Create mapping: video_id + asset -> video_summary
$videoSummaryMap = @{}
foreach ($signal in $signalsData) {
    if ($signal.video_summary -and $signal.video_id -and $signal.asset) {
        $key = "$($signal.video_id)|$($signal.asset)"
        $videoSummaryMap[$key] = $signal.video_summary
    }
}

Write-Host "Created mapping for $($videoSummaryMap.Count) video summaries"

# Stock name variants mapping
$stockNameVariants = @{
    "켄톤" = "캔톤네트워크 (CC)"
    "캔톤" = "캔톤네트워크 (CC)"
    "CC코인" = "캔톤네트워크 (CC)"
    "CC 코인" = "캔톤네트워크 (CC)"
    "켄톤 네트워크" = "캔톤네트워크 (CC)"
    "캔톤 네트워크" = "캔톤네트워크 (CC)"
    "캔톤네트워크" = "캔톤네트워크 (CC)"
    "켄톤 코인" = "캔톤네트워크 (CC)"
    "캔톤코인" = "캔톤네트워크 (CC)"
    "캐톤" = "캔톤네트워크 (CC)"
}

function Get-VideoIdFromUrl {
    param($url)
    if ($url -match "v=([a-zA-Z0-9_-]+)") {
        return $matches[1]
    }
    return $null
}

function Normalize-StockName {
    param($stockName)
    if ($stockNameVariants[$stockName]) {
        return $stockNameVariants[$stockName]
    }
    return $stockName
}

# Read current corinpapa-signals.ts
$corinpapaFile = "C:\Users\Mario\work\invest-sns\src\data\corinpapa-signals.ts"
$corinpapaContent = Get-Content $corinpapaFile -Raw

# Parse the TypeScript file to extract signals array
$signalsStart = $corinpapaContent.IndexOf("export const corinpapaSignals: CorinpapaSignal[] = [")
$signalsArrayStart = $corinpapaContent.IndexOf("[", $signalsStart)
$signalsArrayEnd = $corinpapaContent.LastIndexOf("];")

if ($signalsStart -eq -1 -or $signalsArrayStart -eq -1 -or $signalsArrayEnd -eq -1) {
    Write-Error "Could not parse corinpapa-signals.ts structure"
    exit 1
}

# Extract just the interface and beginning
$beforeSignals = $corinpapaContent.Substring(0, $signalsStart)
$afterSignals = $corinpapaContent.Substring($signalsArrayEnd)

# Update the interface to include videoSummary
$updatedInterface = $beforeSignals -replace "hedged: boolean;", "hedged: boolean;`n  videoSummary?: string;"

Write-Host "Updated interface with videoSummary field"

# For now, let's just update the interface and create a separate script to update the data
$newContent = $updatedInterface + "export const corinpapaSignals: CorinpapaSignal[] = [" + $corinpapaContent.Substring($signalsArrayStart + 1, $signalsArrayEnd - $signalsArrayStart - 1) + "];"

# Write updated file
$newContent | Set-Content $corinpapaFile -Encoding UTF8

Write-Host "Updated corinpapa-signals.ts with videoSummary interface field"
Write-Host "Mapping data saved for next step"

# Save the mapping for the next script
$mappingData = @{
    videoSummaryMap = $videoSummaryMap
    stockNameVariants = $stockNameVariants
}

$mappingData | ConvertTo-Json -Depth 10 | Set-Content "C:\Users\Mario\work\video_summary_mapping.json" -Encoding UTF8