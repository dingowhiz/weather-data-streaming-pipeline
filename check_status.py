"""
Quick status check for the weather processor setup
"""
import subprocess
import logging
from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException
import config

def check_docker():
    """Check Docker status"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed:", result.stdout.strip())
            
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker is running")
                return True
            else:
                print("❌ Docker is not running - Start Docker Desktop")
                return False
        else:
            print("❌ Docker is not installed")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def check_kafka():
    """Check Kafka status"""
    try:
        admin_client = AdminClient({'bootstrap.servers': config.KAFKA_BROKER_ADDRESS})
        metadata = admin_client.list_topics(timeout=5)
        print(f"✅ Kafka is running at {config.KAFKA_BROKER_ADDRESS}")
        
        topics = list(metadata.topics.keys())
        if topics:
            print(f"✅ Available topics: {', '.join(topics)}")
        else:
            print("ℹ️  No topics found (will be auto-created)")
        return True
    except KafkaException as e:
        print(f"❌ Kafka connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Kafka error: {e}")
        return False

def check_docker_compose():
    """Check if docker-compose services are running"""
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Docker Compose Status:")
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Has content beyond header
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        print(f"   {line}")
                return True
            else:
                print("   No services running")
                return False
        else:
            print("❌ Docker Compose not available")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose not found")
        return False

def main():
    print("=" * 50)
    print("  Weather Processor - Status Check")
    print("=" * 50)
    print()
    
    docker_ok = check_docker()
    print()
    
    if docker_ok:
        compose_ok = check_docker_compose()
        print()
    else:
        compose_ok = False
    
    kafka_ok = check_kafka()
    print()
    
    print("=" * 50)
    print("  Summary")
    print("=" * 50)
    
    if kafka_ok:
        print("🎉 Everything is ready!")
        print("📝 You can now run:")
        print("   python main.py")
        print("   python test_producer.py")
        print("   python test_consumer.py")
    elif docker_ok and compose_ok:
        print("⏳ Kafka is starting up...")
        print("📝 Wait a moment and try again, or run:")
        print("   docker-compose logs kafka")
    elif docker_ok:
        print("🚀 Docker is ready, start Kafka:")
        print("   docker-compose up -d")
    else:
        print("🔧 Next steps:")
        print("1. Start Docker Desktop")
        print("2. Run: docker-compose up -d")
        print("3. Wait 1-2 minutes")
        print("4. Run this check again")
    
    print()
    print("🎯 Alternative: Run demo without Kafka:")
    print("   python demo_without_kafka.py")
    print()

if __name__ == "__main__":
    main()
