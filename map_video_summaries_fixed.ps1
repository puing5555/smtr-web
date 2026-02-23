# Map video summaries from signal-review data to corinpapa signals

# First, create a simple mapping from the extracted data
$videoSummaryMap = @{}

# Sample mappings based on the data we saw
$videoSummaryMap["7AaksU-R3dg"] = "화자가 트럼프가 운영하는 월드리버티파이낸셜(WLFI)의 마라라고 포럼 개최가 XRP에게 치명적인 위협이 된다고 주장한다. 포럼에는 400여명의 금융계 거물들이 참석했고, 골드만삭스 회장은 규제 기반 시스템의 중요성을 강조하며 무규제 암호화폐 지지자들을 비판했다..."

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

# For now, let's add the videoSummary field without populating the data
# We'll update the interface and add dummy content first

$updatedContent = $content -replace '("hedged": [^,]+,)(\s*\n\s*})([,]?)', '$1$2  "videoSummary"?: string;$2$3'

Write-Host "Updated TypeScript file structure"

# Now let's create a simpler version - just read the InfluencerDetailClient.tsx and update it
$modalFile = "C:\Users\Mario\work\invest-sns\src\app\(main)\influencers\[id]\InfluencerDetailClient.tsx"
if (Test-Path $modalFile) {
    Write-Host "Found modal file: $modalFile"
    $modalContent = Get-Content $modalFile -Raw
    
    # Add showSummary state
    if ($modalContent -notmatch "showSummary") {
        $modalContent = $modalContent -replace "const \[modalSignal, setModalSignal\] = useState<typeof influencerSignals\[0\] \| null>\(null\)", 
        "const [modalSignal, setModalSignal] = useState<typeof influencerSignals[0] | null>(null);`n  const [showSummary, setShowSummary] = useState(false);"
        
        Write-Host "Added showSummary state"
    }
    
    # Find and replace the modal content sections
    # This is where we need to remove the analysis summary and metadata sections
    # and add the new video summary toggle and buttons
    
    $replacementSection = @"
                {/* 영상요약 보기/접기 */}
                {modalSignal.videoSummary && (
                  <div>
                    <button 
                      onClick={() => setShowSummary(!showSummary)} 
                      className="text-sm text-blue-500 hover:text-blue-700 font-medium flex items-center gap-1"
                    >
                      📋 영상요약 {showSummary ? '접기' : '보기'}
                    </button>
                    {showSummary && (
                      <div className="mt-2 bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <p className="text-gray-800 text-sm leading-relaxed">{modalSignal.videoSummary}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* 차트보기 + 영상보기 버튼 */}
                <div className="flex gap-4 pt-4 border-t border-gray-200">
                  <a 
                    href={``/smtr-web/guru_tracker_v24.html``} 
                    target="_blank"
                    className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                  >
                    📊 차트보기
                  </a>
                  {modalSignal.youtubeLink && (
                    <a 
                      href={modalSignal.youtubeLink} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                    >
                      ▶ 영상보기
                    </a>
                  )}
                </div>
"@

    $modalContent | Set-Content $modalFile -Encoding UTF8
    Write-Host "Modal file updated"
} else {
    Write-Host "Modal file not found at: $modalFile"
}

Write-Host "Script completed"