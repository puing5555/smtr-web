Get-ChildItem C:\Users\Mario\work\scripts -Filter "v11*" | ForEach-Object { Write-Host "$($_.Name) $($_.Length)" }
Get-ChildItem C:\Users\Mario\work\scripts -Filter "*reclassify*" | ForEach-Object { Write-Host "$($_.Name) $($_.Length)" }
