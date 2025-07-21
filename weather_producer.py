"""
Real-time weather data producer
Fetches weather data from Open-Meteo API and streams it to Kafka
"""
import json
import time
import logging
import sys
import threading
from datetime import datetime
import requests
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
import config

class WeatherDataProducer:
    def __init__(self):
        self.producer = None
        self.admin_client = None
        self.running = False
        self.setup_kafka()
    
    def setup_kafka(self):
        """Initialize Kafka producer and admin client"""
        kafka_config = {
            'bootstrap.servers': config.KAFKA_BROKER_ADDRESS,
            'client.id': 'weather-producer'
        }
        
        try:
            self.producer = Producer(kafka_config)
            self.admin_client = AdminClient({'bootstrap.servers': config.KAFKA_BROKER_ADDRESS})
            logging.info("Kafka producer initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def check_kafka_connection(self, timeout=5):
        """Check if Kafka broker is accessible"""
        try:
            metadata = self.admin_client.list_topics(timeout=timeout)
            logging.info(f"Successfully connected to Kafka broker")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Kafka broker: {e}")
            return False
    
    def create_topic_if_not_exists(self, topic_name):
        """Create topic if it doesn't exist"""
        try:
            metadata = self.admin_client.list_topics(timeout=10)
            if topic_name not in metadata.topics:
                topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
                future_map = self.admin_client.create_topics([topic])
                
                for topic, future in future_map.items():
                    try:
                        future.result()
                        logging.info(f"Created topic: {topic}")
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            logging.error(f"Failed to create topic {topic}: {e}")
            else:
                logging.info(f"Topic already exists: {topic_name}")
        except Exception as e:
            logging.error(f"Error checking/creating topic {topic_name}: {e}")
    
    def fetch_weather_data(self):
        """Fetch current weather data from Open-Meteo API"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": config.LATITUDE,
                "longitude": config.LONGITUDE,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto"
            }
            
            logging.debug(f"Fetching weather data for coordinates: {config.LATITUDE}, {config.LONGITUDE}")
            
            response = requests.get(url, params=params, timeout=config.WEATHER_API_TIMEOUT)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Transform the API response into our standardized format
            current = raw_data.get('current', {})
            weather_data = {
                "timestamp": current.get('time', datetime.now().isoformat()),
                "location": f"Lat:{config.LATITUDE}, Lon:{config.LONGITUDE}",
                "temperature": current.get('temperature_2m'),
                "humidity": current.get('relative_humidity_2m'),
                "wind_speed": current.get('wind_speed_10m'),
                "weather_code": current.get('weather_code'),
                "data_source": "Open-Meteo API",
                "fetch_timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Fetched weather data: T={weather_data['temperature']}°C, H={weather_data['humidity']}%")
            return weather_data
            
        except requests.exceptions.Timeout:
            logging.error(f"Weather API request timed out after {config.WEATHER_API_TIMEOUT} seconds")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Weather API request failed: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching weather data: {e}")
            return None
    
    def delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result"""
        if err is not None:
            logging.error(f'Weather data delivery failed: {err}')
        else:
            logging.debug(f'Weather data delivered to {msg.topic()} [{msg.partition()}]')
    
    def produce_weather_data(self, weather_data):
        """Send weather data to Kafka topic"""
        try:
            key = f"weather_{int(time.time())}"
            value = json.dumps(weather_data)
            
            self.producer.produce(
                config.INPUT_TOPIC,
                key=key,
                value=value,
                callback=self.delivery_report
            )
            
            # Wait for any outstanding messages to be delivered
            self.producer.poll(0)
            
            logging.info(f"Produced weather data to topic '{config.INPUT_TOPIC}'")
            return True
            
        except Exception as e:
            logging.error(f"Failed to produce weather data: {e}")
            return False
    
    def start_streaming(self):
        """Start the weather data streaming process"""
        if not self.check_kafka_connection():
            logging.error("Cannot start streaming without Kafka connection")
            return False
        
        # Create topic if needed
        self.create_topic_if_not_exists(config.INPUT_TOPIC)
        
        self.running = True
        logging.info(f"Starting weather data streaming (interval: {config.WEATHER_API_FETCH_INTERVAL} seconds)")
        
        try:
            while self.running:
                # Fetch weather data
                weather_data = self.fetch_weather_data()
                
                if weather_data:
                    # Send to Kafka
                    success = self.produce_weather_data(weather_data)
                    if success:
                        logging.info("Weather data cycle completed successfully")
                    else:
                        logging.warning("Failed to send weather data to Kafka")
                else:
                    logging.warning("Failed to fetch weather data, will retry")
                
                # Wait for next fetch interval
                if self.running:  # Check if still running before sleeping
                    time.sleep(config.WEATHER_API_FETCH_INTERVAL)
                    
        except KeyboardInterrupt:
            logging.info("Streaming interrupted by user")
        except Exception as e:
            logging.error(f"Unexpected error in streaming loop: {e}")
        finally:
            self.stop_streaming()
    
    def stop_streaming(self):
        """Stop the streaming process"""
        self.running = False
        if self.producer:
            # Wait for outstanding messages to be delivered
            self.producer.flush(timeout=10)
            logging.info("Weather data streaming stopped")

def main():
    """Main function to run the weather data producer"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(levelname)s - [WeatherProducer] %(message)s'
    )
    
    logging.info("Weather Data Producer Starting...")
    logging.info(f"Target location: Latitude {config.LATITUDE}, Longitude {config.LONGITUDE}")
    logging.info(f"Fetch interval: {config.WEATHER_API_FETCH_INTERVAL} seconds")
    logging.info(f"Kafka broker: {config.KAFKA_BROKER_ADDRESS}")
    logging.info(f"Output topic: {config.INPUT_TOPIC}")
    
    producer = WeatherDataProducer()
    
    try:
        producer.start_streaming()
    except Exception as e:
        logging.error(f"Failed to start weather producer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
