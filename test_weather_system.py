"""
Quick test of the real-time weather streaming system
This script demonstrates fetching and processing one weather data sample
"""
import json
import logging
import config
from weather_producer import WeatherDataProducer

def main():
    """Test the weather data fetching and processing"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🌤️  Testing Real-Time Weather Data System")
    print("=" * 50)
    print(f"📍 Location: Latitude {config.LATITUDE}, Longitude {config.LONGITUDE}")
    print(f"🌐 API: Open-Meteo")
    print("=" * 50)
    
    # Create producer instance
    producer = WeatherDataProducer()
    
    # Test weather data fetching
    print("\n1️⃣  Fetching current weather data...")
    weather_data = producer.fetch_weather_data()
    
    if weather_data:
        print("✅ Successfully fetched weather data:")
        print(json.dumps(weather_data, indent=2))
        
        # Test Kafka connection
        print("\n2️⃣  Testing Kafka connection...")
        if producer.check_kafka_connection():
            print("✅ Kafka connection successful")
            
            print("\n3️⃣  Testing data production to Kafka...")
            success = producer.produce_weather_data(weather_data)
            
            if success:
                print("✅ Successfully sent weather data to Kafka!")
                print(f"📨 Data sent to topic: {config.INPUT_TOPIC}")
                print("\n🎯 Test completed successfully!")
                print("\n🚀 To start full streaming:")
                print("   Run: start_weather_streaming.bat")
                print("   Or:  python weather_producer.py")
            else:
                print("❌ Failed to send data to Kafka")
        else:
            print("❌ Kafka connection failed")
            print("💡 Make sure Kafka is running: start_local_kafka_fixed.bat")
    else:
        print("❌ Failed to fetch weather data")
        print("💡 Check internet connection and API availability")

if __name__ == "__main__":
    main()
