# Troubleshooting Guide - Kafka Connection Errors

## Problem: `KafkaError{code=_TRANSPORT,val=-195,str="Failed to get metadata: Local: Broker transport failure"}`

This error means your application cannot connect to the Kafka broker. Here are the solutions:

## Solution 1: Start Docker Desktop and Kafka (Recommended)

### Step 1: Install and Start Docker Desktop
1. **Download Docker Desktop** from: https://docs.docker.com/desktop/
2. **Install** following the setup wizard
3. **Start Docker Desktop** (look for the Docker whale icon in system tray)
4. **Wait** for Docker to fully start (icon should be solid, not animated)

### Step 2: Start Kafka Services
```bash
# Navigate to your project directory
cd "C:\DATA\Data_Engineering\weather_processor"

# Start Kafka and Zookeeper
docker-compose up -d

# Wait for services to be ready (1-2 minutes)
# Check status
docker-compose ps
```

### Step 3: Verify Kafka is Running
```bash
# Check if Kafka is accessible
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Or use our setup script
python setup_kafka.py
```

### Step 4: Test Your Application
```bash
# Terminal 1: Start the weather processor
python main.py

# Terminal 2: Send test data
python test_producer.py

# Terminal 3: View processed results
python test_consumer.py
```

## Solution 2: Use the Demo Mode (No Kafka Required)

If you can't get Kafka running, use our demo:

```bash
python demo_without_kafka.py
```

This shows exactly how your code will work with real Kafka.

## Solution 3: Use Cloud Kafka (Confluent Cloud)

1. **Sign up** for Confluent Cloud (free tier available)
2. **Create a cluster** and get connection details
3. **Update configuration**:
   ```bash
   set KAFKA_BROKER_ADDRESS=your-cluster.confluent.cloud:9092
   python main.py
   ```

## Solution 4: Alternative Local Kafka Setup

### Using Kafka Binary (Without Docker)
1. **Download Kafka** from: https://kafka.apache.org/downloads
2. **Extract** to a folder (e.g., `C:\kafka`)
3. **Start Zookeeper**:
   ```bash
   cd C:\kafka
   bin\windows\zookeeper-server-start.bat config\zookeeper.properties
   ```
4. **Start Kafka** (in another terminal):
   ```bash
   cd C:\kafka
   bin\windows\kafka-server-start.bat config\server.properties
   ```

## Common Issues and Solutions

### Issue: "Docker is not running"
- **Solution**: Start Docker Desktop application
- **Check**: Look for Docker whale icon in system tray

### Issue: "docker-compose command not found"
- **Solution**: Docker Compose comes with Docker Desktop
- **Alternative**: Use `docker compose` (with space) instead of `docker-compose`

### Issue: Kafka takes too long to start
- **Solution**: Wait longer (up to 3-5 minutes on slower machines)
- **Check logs**: `docker-compose logs kafka`
- **Restart**: `docker-compose down && docker-compose up -d`

### Issue: Port 9092 already in use
- **Check what's using it**: `netstat -an | findstr :9092`
- **Kill the process** or use a different port
- **Change port** in docker-compose.yml and config.py

### Issue: Memory/Resource issues
- **Increase Docker memory** in Docker Desktop settings
- **Close other applications** to free up resources
- **Use lighter Kafka image** (modify docker-compose.yml)

## Environment Variables

You can customize the setup using environment variables:

```bash
# Change Kafka broker address
set KAFKA_BROKER_ADDRESS=different-host:9092

# Change topic names
set INPUT_TOPIC=my_weather_input
set OUTPUT_TOPIC=my_weather_output

# Change log level
set LOG_LEVEL=INFO

# Run with custom settings
python main.py
```

## Quick Commands Reference

```bash
# Start everything
start_local_kafka.bat

# Check if Kafka is running
docker-compose ps

# View Kafka logs
docker-compose logs kafka

# Stop everything
docker-compose down

# Remove all data (clean restart)
docker-compose down -v

# Test without Kafka
python demo_without_kafka.py

# Access Kafka UI
# Open browser: http://localhost:8080
```

## Still Having Issues?

1. **Run the diagnostic script**:
   ```bash
   python setup_kafka.py
   ```

2. **Check the demo** to verify your code logic:
   ```bash
   python demo_without_kafka.py
   ```

3. **Review logs** for specific error messages:
   ```bash
   docker-compose logs
   ```

The main goal is to have a Kafka broker running on `localhost:9092`. Once that's working, your weather processor application will run perfectly!
