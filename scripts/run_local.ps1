# Run Local Demo - PowerShell Script
# Academic Advisor Chatbot - UPM

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Academic Advisor Chatbot - Local Demo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found. Create one first:" -ForegroundColor Red
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Load environment variables from .env file
if (Test-Path ".\.env") {
    Write-Host "[INFO] Loading environment variables from .env..." -ForegroundColor Green
    Get-Content ".\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)\s*=\s*(.+)\s*$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Host "[ERROR] .env file not found. Copy .env.example to .env and fill in your values." -ForegroundColor Red
    exit 1
}

# Check for trained model
$modelFiles = Get-ChildItem -Path ".\models" -Filter "*.tar.gz" -ErrorAction SilentlyContinue
if (-not $modelFiles) {
    Write-Host "[WARNING] No trained model found in ./models/" -ForegroundColor Yellow
    Write-Host "[INFO] Training model first (this may take a few minutes)..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
    rasa train
}

Write-Host ""
Write-Host "[INFO] Starting Action Server in background..." -ForegroundColor Green
$actionServer = Start-Process -FilePath "powershell" -ArgumentList "-Command", "& .\venv\Scripts\Activate.ps1; rasa run actions --port 5055" -PassThru -WindowStyle Minimized
Write-Host "[INFO] Action Server started (PID: $($actionServer.Id))" -ForegroundColor Green

# Wait for action server to initialize
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[INFO] Starting Rasa Server..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SERVER RUNNING - Use Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps for Telegram integration:" -ForegroundColor Yellow
Write-Host "  1. In a new terminal, run: ngrok http 5005" -ForegroundColor White
Write-Host "  2. Copy the https URL from ngrok" -ForegroundColor White
Write-Host "  3. Set the webhook:" -ForegroundColor White
Write-Host "     https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/setWebhook?url=<NGROK_URL>/webhooks/telegram/webhook" -ForegroundColor Gray
Write-Host ""

# Activate venv and start Rasa
& .\venv\Scripts\Activate.ps1
rasa run --enable-api --cors "*" --port 5005 --endpoints endpoints.local.yml --credentials credentials.local.yml

# Cleanup: stop action server when Rasa is stopped
if ($actionServer -and -not $actionServer.HasExited) {
    Write-Host "[INFO] Stopping Action Server..." -ForegroundColor Yellow
    Stop-Process -Id $actionServer.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "[INFO] Demo stopped." -ForegroundColor Green
