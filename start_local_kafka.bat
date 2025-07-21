@echo off
echo Weather Processor - Local Development Setup
echo ============================================
echo.

REM Check if Docker is running
echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    echo Download from: https://docs.docker.com/desktop/
    pause
    exit /b 1
)

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo Docker is running!
echo.

echo Starting Kafka services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Kafka services
    echo Make sure docker-compose.yml exists in this directory
    pause
    exit /b 1
)

echo.
echo Waiting for Kafka to be ready...
set /a counter=0
:wait_loop
set /a counter+=1
if %counter% gtr 40 (
    echo ERROR: Kafka took too long to start
    echo Check logs with: docker-compose logs kafka
    pause
    exit /b 1
)

timeout /t 3 >nul
docker-compose exec -T kafka kafka-broker-api-versions --bootstrap-server localhost:9092 >nul 2>&1
if %errorlevel% neq 0 (
    echo    Still waiting... (%counter%/40)
    goto wait_loop
)

echo.
echo SUCCESS! Kafka is ready!
echo.
echo ============================================
echo Next steps:
echo ============================================
echo 1. Run the weather processor:
echo    python main.py
echo.
echo 2. Send test data (in another terminal):
echo    python test_producer.py
echo.
echo 3. View processed data (in another terminal):
echo    python test_consumer.py
echo.
echo 4. Access Kafka UI in browser:
echo    http://localhost:8080
echo.
echo 5. To stop services later:
echo    docker-compose down
echo.
echo Current status:
docker-compose ps
echo.
pause
