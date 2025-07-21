"""
Enhanced weather data consumer with improved display formatting
Reads processed weather data from Kafka and displays it in a user-friendly format
"""
import json
import logging
import sys
import signal
from datetime import datetime
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient
import config

class WeatherConsumer:
    def __init__(self):
        self.consumer = None
        self.running = False
        self.message_count = 0
        self.setup_consumer()
        
    def setup_consumer(self):
        """Initialize Kafka consumer"""
        consumer_config = {
            'bootstrap.servers': config.KAFKA_BROKER_ADDRESS,
            'group.id': f"{config.KAFKA_CONSUMER_GROUP}_display",
            'auto.offset.reset': config.KAFKA_AUTO_OFFSET_RESET,
            'enable.auto.commit': True,
        }
        
        try:
            self.consumer = Consumer(consumer_config)
            logging.info("Weather consumer initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize consumer: {e}")
            raise
    
    def check_kafka_connection(self, timeout=5):
        """Check if Kafka broker is accessible"""
        try:
            admin_client = AdminClient({'bootstrap.servers': config.KAFKA_BROKER_ADDRESS})
            metadata = admin_client.list_topics(timeout=timeout)
            logging.info("Successfully connected to Kafka broker")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Kafka broker: {e}")
            return False
    
    def format_weather_display(self, weather_data):
        """Format weather data for nice display"""
        try:
            timestamp = weather_data.get('timestamp', 'N/A')
            location = weather_data.get('location', 'Unknown')
            
            # Temperature info
            temp_c = weather_data.get('temperature', weather_data.get('temperature_celsius', 'N/A'))
            temp_f = weather_data.get('temperature_fahrenheit', 'N/A')
            
            humidity = weather_data.get('humidity', 'N/A')
            wind_speed = weather_data.get('wind_speed', 'N/A')
            weather_desc = weather_data.get('weather_description', 'N/A')
            data_quality = weather_data.get('data_quality_score', 'N/A')
            data_source = weather_data.get('data_source', 'Unknown')
            
            # Processing info
            processed_at = weather_data.get('processed_timestamp', 'N/A')
            
            # Create display
            display = f"""
╔══════════════════════════════════════════════════════════════╗
║                      WEATHER UPDATE #{self.message_count:<3}                      ║
╠══════════════════════════════════════════════════════════════╣
║ 📍 Location: {location:<47} ║
║ ⏰ Timestamp: {timestamp:<46} ║
╠══════════════════════════════════════════════════════════════╣
║ 🌡️  Temperature: {temp_c}°C ({temp_f}°F)                    ║
║ 💧 Humidity: {humidity}%                                      ║
║ 💨 Wind Speed: {wind_speed} km/h                             ║
║ ☁️  Conditions: {weather_desc:<43} ║
╠══════════════════════════════════════════════════════════════╣
║ 📊 Data Quality: {data_quality:.1f}/1.0                             ║
║ 🔄 Processed: {processed_at:<45} ║
║ 📡 Source: {data_source:<49} ║
╚══════════════════════════════════════════════════════════════╝
"""
            return display
            
        except Exception as e:
            return f"Error formatting weather data: {e}\nRaw data: {weather_data}"
    
    def start_consuming(self):
        """Start consuming weather data"""
        if not self.check_kafka_connection():
            logging.error("Cannot start consuming without Kafka connection")
            return False
            
        try:
            self.consumer.subscribe([config.OUTPUT_TOPIC])
            self.running = True
            
            print("\n" + "="*70)
            print("🌤️  REAL-TIME WEATHER DATA STREAM CONSUMER")
            print("="*70)
            print(f"📡 Consuming from topic: {config.OUTPUT_TOPIC}")
            print(f"🏢 Kafka broker: {config.KAFKA_BROKER_ADDRESS}")
            print(f"👥 Consumer group: {config.KAFKA_CONSUMER_GROUP}_display")
            print("⌨️  Press Ctrl+C to stop")
            print("="*70)
            
            while self.running:
                try:
                    msg = self.consumer.poll(1.0)
                    
                    if msg is None:
                        continue
                    
                    if msg.error():
                        if msg.error().code() != -191:  # Ignore partition EOF
                            logging.error(f"Consumer error: {msg.error()}")
                        continue
                    
                    # Process message
                    self.message_count += 1
                    
                    try:
                        weather_data = json.loads(msg.value().decode('utf-8'))
                        display = self.format_weather_display(weather_data)
                        print(display)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse weather data: {e}")
                        print(f"Raw message: {msg.value()}")
                    except Exception as e:
                        print(f"❌ Error processing message: {e}")
                        
                except KeyboardInterrupt:
                    print("\n🛑 Stopping weather consumer...")
                    break
                except Exception as e:
                    logging.error(f"Error in consumer loop: {e}")
                    
        except Exception as e:
            logging.error(f"Fatal error in consumer: {e}")
        finally:
            self.stop_consuming()
    
    def stop_consuming(self):
        """Stop consuming and cleanup"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            print(f"\n✅ Consumer stopped. Processed {self.message_count} weather updates.")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal...")
    sys.exit(0)

def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(levelname)s - [WeatherConsumer] %(message)s'
    )
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    consumer = WeatherConsumer()
    
    try:
        consumer.start_consuming()
    except Exception as e:
        logging.error(f"Failed to start weather consumer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
