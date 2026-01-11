# Create a local temp directory if it doesn't exist
$localTemp = "$PWD\temp_build"
if (!(Test-Path $localTemp)) {
    New-Item -ItemType Directory -Force -Path $localTemp | Out-Null
}

# Override system temp variables for this session
$env:TEMP = $localTemp
$env:TMP = $localTemp

Write-Host "🚀 Starting Rasa Training with custom temp dir: $localTemp" -ForegroundColor Green

# Run the training command
.\venv\Scripts\python -m rasa train --debug

# Optional: Clean up after (commented out to debug if needed)
# Remove-Item -Recurse -Force $localTemp
