# SmartHouse AI - Automated Runner Script
# Usage: .\run-project.ps1

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Both,
    [switch]$Tests,
    [switch]$Fresh
)

$projectRoot = $PSScriptRoot
$backendPath = "$projectRoot\backend"
$frontendPath = "$projectRoot\frontend"

function Start-Backend {
    if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
        Write-Host "Backend already listening on http://127.0.0.1:8000" -ForegroundColor Yellow
        return
    }
    Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Green
    Write-Host "   Port: 8000" -ForegroundColor Gray
    Write-Host "   Docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray
    
    Set-Location $backendPath
    & python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

function Start-Frontend {
    $frontendPort = 3000
    while (Get-NetTCPConnection -LocalPort $frontendPort -State Listen -ErrorAction SilentlyContinue) {
        $frontendPort++
    }
    Write-Host "🚀 Starting Frontend (React)..." -ForegroundColor Green
    Write-Host "   Port: $frontendPort" -ForegroundColor Gray
    Write-Host "   URL: http://127.0.0.1:$frontendPort" -ForegroundColor Gray
    
    Set-Location $frontendPath
    $env:PORT = "$frontendPort"
    & npm.cmd start
}

function Run-Tests {
    Write-Host "🧪 Running Tests..." -ForegroundColor Cyan
    Set-Location $backendPath
    & python -m pytest tests/ -v
}

function Clean-Frontend {
    Write-Host "🧹 Cleaning frontend..." -ForegroundColor Yellow
    Set-Location $frontendPath
    Write-Host "   Removing node_modules..." -ForegroundColor Gray
    Remove-Item -Path "$frontendPath\node_modules" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   Clearing npm cache..." -ForegroundColor Gray
    & npm cache clean --force
    Write-Host "   Installing dependencies..." -ForegroundColor Gray
    & npm install
}

# Main logic
if ($Both -or (-not $Backend -and -not $Frontend -and -not $Tests)) {
    # Start both in separate windows
    Write-Host "SmartHouse AI - Starting Both Backend & Frontend" -ForegroundColor Magenta
    Write-Host ""

    # Create new PowerShell window for backend
    Write-Host "Backend starting in new window..." -ForegroundColor Green
    if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
        Write-Host "Backend already listening on http://127.0.0.1:8000" -ForegroundColor Yellow
    } else {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$backendPath`"; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    }

    # Create new PowerShell window for frontend
    Write-Host "Frontend starting in new window..." -ForegroundColor Green
    $frontendPort = 3000
    while (Get-NetTCPConnection -LocalPort $frontendPort -State Listen -ErrorAction SilentlyContinue) {
        $frontendPort++
    }
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PORT='$frontendPort'; cd `"$frontendPath`"; npm.cmd start"

    Write-Host ""
    Write-Host "Both services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend:     http://127.0.0.1:$frontendPort" -ForegroundColor White
    Write-Host "  Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
    Write-Host "  Backend API:  http://127.0.0.1:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C in either window to stop the respective service." -ForegroundColor Yellow
}
elseif ($Backend) {
    Start-Backend
}
elseif ($Frontend) {
    if ($Fresh) {
        Clean-Frontend
    }
    Start-Frontend
}
elseif ($Tests) {
    Run-Tests
}
else {
    Write-Host "SmartHouse AI - Project Runner" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Usage: .\run-project.ps1 [option]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -Both       Start both backend and frontend (default)" -ForegroundColor Gray
    Write-Host "  -Backend    Start only backend" -ForegroundColor Gray
    Write-Host "  -Frontend   Start only frontend" -ForegroundColor Gray
    Write-Host "  -Fresh      Clean and reinstall before starting frontend" -ForegroundColor Gray
    Write-Host "  -Tests      Run test suite" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\run-project.ps1                  # Start both services" -ForegroundColor Gray
    Write-Host "  .\run-project.ps1 -Backend         # Start backend only" -ForegroundColor Gray
    Write-Host "  .\run-project.ps1 -Frontend -Fresh # Clean and start frontend" -ForegroundColor Gray
    Write-Host "  .\run-project.ps1 -Tests           # Run tests" -ForegroundColor Gray
}
