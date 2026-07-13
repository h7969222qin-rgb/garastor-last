@echo off
cd /d "D:\jonhos总文件\jonhos国际"
echo Starting JONHOS server...
echo.
echo ============================================
echo   JONHOS Luxury Flooring - Local Server
echo   http://127.0.0.1:8080
echo ============================================
echo.
echo Press Ctrl+C to stop the server
echo.
npx http-server . -p 8080 -c-1 -o --cors
pause