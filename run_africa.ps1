#!/usr/bin/env pwsh
<#
Quick runner for African Business Schools Discovery
PowerShell version for Windows users
#>

Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    AFRICAN BUSINESS SCHOOL DISCOVERY RUNNER                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Running discovery for all 8 African countries..." -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Run discovery
Write-Host "Starting discovery..." -ForegroundColor Cyan
Write-Host ""
python run_discovery.py --regions Africa

Write-Host ""
Write-Host "✨ Discovery complete!" -ForegroundColor Green
Write-Host "📁 Check health_app/business_school_data/ for exports" -ForegroundColor Green
Write-Host ""
