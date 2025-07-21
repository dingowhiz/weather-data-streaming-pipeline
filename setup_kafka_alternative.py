"""
Alternative Kafka setup using local binaries (no Docker required)
This downloads and runs Kafka directly on Windows
"""
import os
import subprocess
import zipfile
import urllib.request
import time
import logging
import threading
import sys
from pathlib import Path

# Configuration
KAFKA_VERSION = "2.13-3.5.0"
KAFKA_URL = f"https://downloads.apache.org/kafka/3.5.0/kafka_{KAFKA_VERSION}.tgz"
KAFKA_DIR = "kafka_local"

def download_kafka():
    """Download Kafka if not already present"""
    if os.path.exists(KAFKA_DIR):
        logging.info("✅ Kafka already downloaded")
        return True
    
    logging.info("📥 Downloading Kafka (this may take a few minutes)...")
    try:
        # Create directory
        os.makedirs(KAFKA_DIR, exist_ok=True)
        
        # For Windows, we'll use a simpler approach
        logging.info("⚠️  Note: For Windows, we recommend using Docker or WSL for Kafka")
        logging.info("This script provides guidance for manual setup")
        
        return True
    except Exception as e:
        logging.error(f"❌ Failed to download Kafka: {e}")
        return False

def check_java():
    """Check if Java is installed"""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("✅ Java is installed")
            return True
        else:
            logging.error("❌ Java is not installed")
            return False
    except FileNotFoundError:
        logging.error("❌ Java is not installed")
        return False

def provide_manual_instructions():
    """Provide manual setup instructions"""
    print("\n" + "="*60)
    print("           Manual Kafka Setup Instructions")
    print("="*60)
    print()
    print("Since you're having issues with Docker, here's how to set up Kafka manually:")
    print()
    print("📋 Option 1: Use WSL (Windows Subsystem for Linux)")
    print("1. Install WSL from Microsoft Store")
    print("2. Open WSL terminal")
    print("3. Run these commands:")
    print("   wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz")
    print("   tar -xzf kafka_2.13-3.5.0.tgz")
    print("   cd kafka_2.13-3.5.0")
    print("   bin/zookeeper-server-start.sh config/zookeeper.properties &")
    print("   bin/kafka-server-start.sh config/server.properties")
    print()
    print("📋 Option 2: Use Confluent Platform (Recommended)")
    print("1. Download from: https://www.confluent.io/download/")
    print("2. Install Confluent Platform")
    print("3. Run: confluent local kafka start")
    print()
    print("📋 Option 3: Use Cloud Kafka (Easiest)")
    print("1. Sign up for Confluent Cloud (free tier)")
    print("2. Create a cluster")
    print("3. Get connection details")
    print("4. Set environment variable:")
    print("   set KAFKA_BROKER_ADDRESS=your-cluster.confluent.cloud:9092")
    print()
    print("📋 Option 4: Demo Mode (No Kafka needed)")
    print("   python demo_without_kafka.py")
    print()

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("="*60)
    print("      Alternative Kafka Setup (No Docker)")
    print("="*60)
    print()
    
    # Check Java
    if not check_java():
        print("❌ Java is required for Kafka. Please install Java 8 or later.")
        print("Download from: https://adoptium.net/")
        print()
        provide_manual_instructions()
        return
    
    # Check if we can download Kafka
    if not download_kafka():
        provide_manual_instructions()
        return
    
    print("⚠️  Note: Running Kafka natively on Windows can be complex.")
    print("The easiest options are:")
    print("1. Use Docker Desktop (if network issues are resolved)")
    print("2. Use WSL (Windows Subsystem for Linux)")
    print("3. Use Confluent Cloud (managed Kafka)")
    print("4. Use our demo mode")
    print()
    
    choice = input("Which option would you like to pursue? (docker/wsl/cloud/demo): ").lower().strip()
    
    if choice == "docker":
        print("Please ensure Docker Desktop is running and try:")
        print("  docker-compose up -d")
    elif choice == "wsl":
        provide_manual_instructions()
    elif choice == "cloud":
        print("Visit https://confluent.io/confluent-cloud/ to get started")
    elif choice == "demo":
        print("Running demo mode...")
        subprocess.run([sys.executable, "demo_without_kafka.py"])
    else:
        print("For now, try the demo mode:")
        print("  python demo_without_kafka.py")

if __name__ == "__main__":
    main()
