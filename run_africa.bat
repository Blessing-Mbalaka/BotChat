@echo off
REM Quick runner for African Business Schools Discovery
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║    AFRICAN BUSINESS SCHOOL DISCOVERY RUNNER                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Running discovery for all 8 African countries...
echo.

call .\.venv\Scripts\activate.bat
python run_discovery.py --regions Africa

echo.
echo ✨ Discovery complete! Check health_app/business_school_data/ for exports
pause
