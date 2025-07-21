@echo off
setlocal enabledelayedexpansion
echo ================================================================
echo              Weather Processor - Kafka Setup
echo ================================================================
echo.

REM Check if Docker is running
echo [1/6] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker is not installed
    echo.
    echo Please install Docker Desktop from:
    echo https://docs.docker.com/desktop/
    echo.
    pause
    exit /b 1
)

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker Desktop is not running
    echo.
    echo Please start Docker Desktop and try again
    echo You can find Docker Desktop in your Start menu
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Check what's using port 9092
echo [2/6] Checking port 9092...
netstat -an | findstr :9092 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  WARNING: Port 9092 is already in use
    echo Checking if it's already Kafka...
    timeout /t 2 >nul
)

REM Try to connect to existing Kafka
echo [3/6] Testing existing Kafka connection...
C:/DATA/Data_Engineering/weather_processor/env/Scripts/python.exe -c "from confluent_kafka.admin import AdminClient; AdminClient({'bootstrap.servers': 'localhost:9092'}).list_topics(timeout=3)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Kafka is already running!
    echo.
    goto :success
)

echo 🔄 No existing Kafka found, starting new instance...
echo.

REM Stop any existing containers
echo [4/6] Cleaning up existing containers...
docker-compose -f docker-compose-simple.yml down >nul 2>&1
docker-compose down >nul 2>&1

REM Try to start with simple compose first
echo [5/6] Starting Kafka (attempt 1/2 - simple setup)...
docker-compose -f docker-compose-simple.yml up -d
if %errorlevel% neq 0 (
    echo ⚠️  Simple setup failed, trying full setup...
    docker-compose up -d
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Both setups failed
        echo.
        echo This could be due to:
        echo 1. Network connectivity issues
        echo 2. Docker resource limitations
        echo 3. Port conflicts
        echo.
        echo ======================== Solutions ========================
        echo Option 1: Try the demo mode (no Kafka needed):
        echo    python demo_without_kafka.py
        echo.
        echo Option 2: Check network and retry:
        echo    1. Check your internet connection
        echo    2. Restart Docker Desktop
        echo    3. Run this script again
        echo.
        echo Option 3: Use a different port:
        echo    set KAFKA_BROKER_ADDRESS=localhost:9093
        echo    (then modify docker-compose.yml to use port 9093)
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Containers started successfully
echo.

echo [6/6] Waiting for Kafka to be ready...
set /a counter=0
set /a max_wait=30

:wait_loop
set /a counter+=1
if %counter% gtr %max_wait% (
    echo ❌ ERROR: Kafka took too long to start (%max_wait% attempts)
    echo.
    echo Checking container status...
    docker-compose ps
    echo.
    echo Checking logs...
    docker-compose logs --tail=10 kafka
    echo.
    echo ======================== Next Steps ========================
    echo 1. Try the demo mode: python demo_without_kafka.py
    echo 2. Check container logs: docker-compose logs kafka
    echo 3. Restart setup: docker-compose down ^&^& .\start_local_kafka_fixed.bat
    echo.
    pause
    exit /b 1
)

echo    Testing connection... (attempt %counter%/%max_wait%)
timeout /t 3 >nul

REM Test Kafka connection with Python
C:/DATA/Data_Engineering/weather_processor/env/Scripts/python.exe -c "from confluent_kafka.admin import AdminClient; AdminClient({'bootstrap.servers': 'localhost:9092'}).list_topics(timeout=2)" >nul 2>&1
if %errorlevel% neq 0 (
    goto wait_loop
)

:success
echo.
echo ================================================================
echo                    🎉 SUCCESS! Kafka is ready! 🎉
echo ================================================================
echo.
echo ✅ Kafka broker: localhost:9092
echo ✅ Connection: Working
echo ✅ Auto-topic creation: Enabled
echo.
echo ======================== Next Steps ========================
echo 1. Run the weather processor:
echo    python main.py
echo.
echo 2. Send test data (in another terminal):
echo    python test_producer.py
echo.
echo 3. View processed data (in another terminal):
echo    python test_consumer.py
echo.
echo 4. Check status anytime:
echo    python check_status.py
echo.
echo 5. View current containers:
docker-compose ps 2>nul || docker-compose -f docker-compose-simple.yml ps
echo.
echo ======================== Troubleshooting ========================
echo • Still having issues? Run: python demo_without_kafka.py
echo • Stop services: docker-compose down
echo • View logs: docker-compose logs kafka
echo.
pause
endlocal
