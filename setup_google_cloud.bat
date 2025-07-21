@echo off
echo Opening Google Cloud Console and Google Sheets for setup...
echo.

echo 1. Opening Google Cloud Console (for credentials)...
start https://console.cloud.google.com/

echo 2. Opening Google Sheets (to create 'Singapore Weather' sheet)...
start https://sheets.google.com/

echo.
echo Setup Instructions:
echo ===================
echo.
echo GOOGLE CLOUD CONSOLE:
echo 1. Create new project: "Weather Data Processor"
echo 2. Enable "Google Sheets API" 
echo 3. Create Service Account: "weather-data-service"
echo 4. Download JSON key as "credentials.json"
echo.
echo GOOGLE SHEETS:
echo 1. Create new spreadsheet
echo 2. Rename to: "Singapore Weather"
echo 3. Share with your service account email
echo 4. Give Editor permissions
echo.
echo After downloading credentials.json:
echo   python check_credentials.py
echo   python test_google_sheets.py
echo.
pause
