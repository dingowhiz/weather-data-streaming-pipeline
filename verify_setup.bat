@echo off
echo 🔍 Google Sheets Setup Verification
echo ================================

echo.
echo Step 1: Checking credentials file...
python verify_credentials.py

echo.
echo Step 2: Testing Google Sheets connection...
python test_google_sheets.py

echo.
echo If both tests pass, you can run the complete system:
echo   start_weather_streaming.bat
echo.
pause
