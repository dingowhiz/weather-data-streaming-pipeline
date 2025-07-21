@echo off
echo Starting Real-Time Weather Data Streaming Pipeline
echo ================================================
echo.

echo Checking if Kafka is running...
docker ps | findstr /C:"kafka" > nul
if errorlevel 1 (
    echo Kafka containers not found. Starting Kafka...
    call start_local_kafka_fixed.bat
    echo Waiting for Kafka to fully start...
    timeout /t 30 /nobreak > nul
) else (
    echo Kafka is already running.
)

echo.
echo Starting Weather Data Pipeline in 3 windows:
echo 1. Weather Data Producer (fetches from API)
echo 2. Stream Processor (transforms data) 
echo 3. Consumer (displays results)
echo.

REM Start weather producer in new window
start "Weather Producer" cmd /k "env\Scripts\activate && python weather_producer.py"

REM Wait a bit for producer to start
timeout /t 5 /nobreak > nul

REM Start stream processor in new window  
start "Stream Processor" cmd /k "env\Scripts\activate && python main.py"

REM Wait a bit for processor to start
timeout /t 3 /nobreak > nul

REM Start consumer in new window
start "Weather Consumer" cmd /k "env\Scripts\activate && python weather_consumer.py"

echo.
echo All components started!
echo - Weather Producer: Fetching real weather data every 5 minutes
echo - Stream Processor: Processing incoming weather data
echo - Consumer: Displaying processed results
echo.
echo Close any window to stop that component.
echo Press any key to exit this launcher...
pause > nul
