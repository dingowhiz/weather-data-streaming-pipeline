"""
Test script to simulate Kafka producer sending weather data
Run this after starting Kafka to test the weather processor
"""
import json
import time
import logging
import sys
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
import config

def check_kafka_connection(broker_address, timeout=5):
    """Check if Kafka broker is accessible"""
    try:
        admin_client = AdminClient({'bootstrap.servers': broker_address})
        metadata = admin_client.list_topics(timeout=timeout)
        logging.info(f"Successfully connected to Kafka broker at {broker_address}")
        return True, admin_client
    except KafkaException as e:
        logging.error(f"Failed to connect to Kafka broker at {broker_address}: {e}")
        return False, None
    except Exception as e:
        logging.error(f"Unexpected error when connecting to Kafka: {e}")
        return False, None

def create_topic_if_not_exists(admin_client, topic_name):
    """Create topic if it doesn't exist"""
    try:
        metadata = admin_client.list_topics(timeout=10)
        if topic_name not in metadata.topics:
            topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
            future_map = admin_client.create_topics([topic])
            # Wait for topic creation to complete
            for topic_name, future in future_map.items():
                try:
                    future.result()  # The result itself is None
                    logging.info(f"Created topic: {topic_name}")
                except Exception as e:
                    logging.error(f"Failed to create topic {topic_name}: {e}")
        else:
            logging.info(f"Topic already exists: {topic_name}")
    except Exception as e:
        logging.error(f"Error creating topic {topic_name}: {e}")

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result"""
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logging.info("Weather Data Producer Test")
    logging.info("=" * 40)
    
    # Check Kafka connection first
    is_connected, admin_client = check_kafka_connection(config.KAFKA_BROKER_ADDRESS, config.KAFKA_CONNECTION_TIMEOUT)
    
    if not is_connected:
        logging.error("Cannot proceed without Kafka connection.")
        logging.info("\nTo fix this issue:")
        logging.info("1. Make sure Docker Desktop is running")
        logging.info("2. Start Kafka using: docker-compose up -d")
        logging.info("3. Wait for Kafka to be ready (about 30-60 seconds)")
        logging.info("4. Check status with: docker-compose ps")
        logging.info(f"\nCurrent broker address: {config.KAFKA_BROKER_ADDRESS}")
        sys.exit(1)
    
    # Create topics if they don't exist
    create_topic_if_not_exists(admin_client, config.INPUT_TOPIC)
    create_topic_if_not_exists(admin_client, config.OUTPUT_TOPIC)
    
    # Create producer
    producer = Producer({'bootstrap.servers': config.KAFKA_BROKER_ADDRESS})
    
    # Sample weather data
    weather_data = [
        {
            "timestamp": "2025-07-21T16:00:00Z",
            "location": "New York",
            "temperature": 25.5,
            "humidity": 65,
            "wind_speed": 12.3,
            "conditions": "partly cloudy"
        },
        {
            "timestamp": "2025-07-21T16:05:00Z", 
            "location": "Los Angeles",
            "temperature": 28.2,
            "humidity": 45,
            "wind_speed": 8.7,
            "conditions": "sunny"
        },
        {
            "timestamp": "2025-07-21T16:10:00Z",
            "location": "Chicago", 
            "temperature": 18.9,
            "humidity": 78,
            "wind_speed": 15.2,
            "conditions": "rainy"
        }
    ]
    
    try:
        for i, data in enumerate(weather_data):
            # Produce message
            key = f"weather_{data['location'].lower().replace(' ', '_')}"
            value = json.dumps(data)
            
            producer.produce(
                config.INPUT_TOPIC,
                key=key,
                value=value,
                callback=delivery_report
            )
            
            logging.info(f"Sent weather data for {data['location']}")
            
            # Wait for delivery
            producer.poll(0)
            
            # Small delay between messages
            time.sleep(1)
        
        # Wait for all messages to be delivered
        producer.flush()
        logging.info("All messages sent successfully!")
        
    except KafkaException as e:
        logging.error(f"Kafka error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
