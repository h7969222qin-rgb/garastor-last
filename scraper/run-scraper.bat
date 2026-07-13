@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════
echo   GARASTOR Journal Content Fetcher
echo ═══════════════════════════════════════
echo.
cd /d "%~dp0"
node fetch-journal-content.js
echo.
echo ── Done ──
echo Results saved to: fetched\latest-summary.txt
echo.
pause