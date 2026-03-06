@echo off
REM Runner for Global Business Schools Discovery (All Continents)
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║    GLOBAL BUSINESS SCHOOL DISCOVERY RUNNER                    ║
echo ║    Running discovery for 40+ countries across all continents   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo This will process:
echo   ✓ Africa     (8 countries)
echo   ✓ Europe     (10 countries)
echo   ✓ Asia       (10 countries)
echo   ✓ Americas   (10 countries)
echo.
echo Estimated time: 3-5 minutes
echo.
pause

call .\.venv\Scripts\activate.bat
python run_discovery.py --regions Africa Europe Asia Americas

echo.
echo ✨ Global discovery complete! Check health_app/business_school_data/ for exports
pause
