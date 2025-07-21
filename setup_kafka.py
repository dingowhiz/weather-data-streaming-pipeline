#!/usr/bin/env python3
"""
Setup script to start Kafka and verify everything is working
"""
import subprocess
import time
import logging
import sys
import os
from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is installed and running"""
    logging.info("Checking Docker...")
    
    # Check if Docker is installed
    success, stdout, stderr = run_command("docker --version")
    if not success:
        logging.error("Docker is not installed!")
        logging.info("Please install Docker Desktop from: https://docs.docker.com/desktop/")
        return False
    
    logging.info(f"Docker version: {stdout.strip()}")
    
    # Check if Docker is running
    success, stdout, stderr = run_command("docker ps")
    if not success:
        logging.error("Docker is not running!")
        logging.info("Please start Docker Desktop and try again.")
        return False
    
    logging.info("Docker is running ✓")
    return True

def check_kafka_connection(broker_address="localhost:9092", timeout=5):
    """Check if Kafka is accessible"""
    try:
        admin_client = AdminClient({'bootstrap.servers': broker_address})
        metadata = admin_client.list_topics(timeout=timeout)
        return True
    except:
        return False

def start_kafka():
    """Start Kafka using Docker Compose"""
    logging.info("Starting Kafka services...")
    
    if not os.path.exists("docker-compose.yml"):
        logging.error("docker-compose.yml not found in current directory!")
        return False
    
    # Start services
    success, stdout, stderr = run_command("docker-compose up -d")
    if not success:
        logging.error(f"Failed to start Kafka: {stderr}")
        return False
    
    logging.info("Kafka services started. Waiting for them to be ready...")
    
    # Wait for Kafka to be ready (max 2 minutes)
    max_wait = 120
    wait_interval = 5
    elapsed = 0
    
    while elapsed < max_wait:
        if check_kafka_connection():
            logging.info(f"Kafka is ready! (took {elapsed} seconds)")
            return True
        
        logging.info(f"Waiting for Kafka... ({elapsed}/{max_wait}s)")
        time.sleep(wait_interval)
        elapsed += wait_interval
    
    logging.error("Kafka failed to start within 2 minutes")
    return False

def show_status():
    """Show current status of services"""
    logging.info("\nCurrent Status:")
    logging.info("=" * 40)
    
    # Check Docker containers
    success, stdout, stderr = run_command("docker-compose ps")
    if success:
        logging.info("Docker Containers:")
        print(stdout)
    
    # Check Kafka connection
    if check_kafka_connection():
        logging.info("✓ Kafka is accessible at localhost:9092")
        logging.info("✓ Ready to run: python main.py")
        logging.info("✓ Ready to test: python test_producer.py")
        logging.info("✓ Kafka UI available at: http://localhost:8080")
    else:
        logging.warning("✗ Kafka is not accessible")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("  Weather Processor - Kafka Setup Script")
    print("=" * 60)
    print()
    
    # Step 1: Check Docker
    if not check_docker():
        sys.exit(1)
    
    # Step 2: Check if Kafka is already running
    if check_kafka_connection():
        logging.info("Kafka is already running!")
        show_status()
        return
    
    # Step 3: Start Kafka
    if not start_kafka():
        logging.error("Failed to start Kafka. Please check the logs:")
        run_command("docker-compose logs kafka")
        sys.exit(1)
    
    # Step 4: Show final status
    show_status()
    
    print("\n" + "=" * 60)
    print("  Setup Complete! Next steps:")
    print("=" * 60)
    print("1. Run the weather processor: python main.py")
    print("2. In another terminal, send test data: python test_producer.py")
    print("3. In another terminal, view results: python test_consumer.py")
    print("4. Access Kafka UI at: http://localhost:8080")
    print("5. To stop services: docker-compose down")
    print()

if __name__ == "__main__":
    main()
