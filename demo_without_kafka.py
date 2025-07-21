"""
Alternative test script that simulates Kafka functionality for development
Use this when Docker/Kafka is not available
"""
import json
import time
import logging
import threading
import queue
from datetime import datetime
import config

class MockKafka:
    """Simple mock Kafka implementation for testing"""
    
    def __init__(self):
        self.topics = {}
        self.consumers = {}
        self.running = False
        
    def create_topic(self, topic_name):
        if topic_name not in self.topics:
            self.topics[topic_name] = queue.Queue()
            logging.info(f"Created mock topic: {topic_name}")
    
    def produce(self, topic, key, value):
        if topic not in self.topics:
            self.create_topic(topic)
        
        message = {
            'key': key,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'partition': 0,
            'offset': self.topics[topic].qsize()
        }
        
        self.topics[topic].put(message)
        logging.info(f"Produced message to {topic}: key={key}")
        return message
    
    def consume(self, topic, timeout=1):
        if topic not in self.topics:
            return None
            
        try:
            message = self.topics[topic].get(timeout=timeout)
            return message
        except queue.Empty:
            return None
    
    def list_topics(self):
        return list(self.topics.keys())

def transform_weather_data(msg):
    """Transform weather data - same as in main.py"""
    import time
    
    # Make a copy of the message
    new_msg = msg.copy()
    
    # Add processing timestamp
    new_msg['processed_at'] = time.time()
    new_msg['processed_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    
    # Convert temperature to Fahrenheit if it exists and looks like Celsius
    if 'temperature' in new_msg and isinstance(new_msg['temperature'], (int, float)):
        celsius = new_msg['temperature']
        # Assume input is in Celsius if temperature is reasonable for Celsius
        if -50 <= celsius <= 60:
            fahrenheit = (celsius * 9/5) + 32
            new_msg['temperature_fahrenheit'] = round(fahrenheit, 1)
    
    # Add data quality score based on completeness
    required_fields = ['timestamp', 'location', 'temperature', 'humidity']
    present_fields = sum(1 for field in required_fields if field in new_msg and new_msg[field] is not None)
    new_msg['data_quality_score'] = present_fields / len(required_fields)
    
    return new_msg

def simulate_stream_processing():
    """Simulate the stream processing pipeline"""
    
    mock_kafka = MockKafka()
    
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
        },
        {
            "timestamp": "2025-07-21T16:15:00Z",
            "location": "Miami", 
            "temperature": 32.1,
            "humidity": 85,
            "wind_speed": 6.2,
            "conditions": "humid"
        },
        {
            "timestamp": "2025-07-21T16:20:00Z",
            "location": "Seattle", 
            "temperature": 15.3,
            "humidity": 90,
            "wind_speed": 11.8,
            "conditions": "drizzle"
        }
    ]
    
    logging.info("Starting mock stream processing demonstration...")
    logging.info("=" * 60)
    
    # Simulate producer
    for i, data in enumerate(weather_data):
        key = f"weather_{data['location'].lower().replace(' ', '_')}"
        
        # Produce to input topic
        msg = mock_kafka.produce(config.INPUT_TOPIC, key, json.dumps(data))
        logging.info(f"📤 PRODUCED: {data['location']} - {data['temperature']}°C")
        
        # Simulate stream processing (consume from input, transform, produce to output)
        input_msg = mock_kafka.consume(config.INPUT_TOPIC)
        if input_msg:
            # Parse the message value
            weather_data_parsed = json.loads(input_msg['value'])
            
            # Transform the data
            transformed_data = transform_weather_data(weather_data_parsed)
            
            # Produce to output topic
            output_msg = mock_kafka.produce(
                config.OUTPUT_TOPIC, 
                input_msg['key'], 
                json.dumps(transformed_data)
            )
            
            logging.info(f"🔄 TRANSFORMED: Added Fahrenheit ({transformed_data.get('temperature_fahrenheit', 'N/A')}°F), Quality Score: {transformed_data['data_quality_score']:.2f}")
            
            # Simulate consumer showing the result
            result_msg = mock_kafka.consume(config.OUTPUT_TOPIC)
            if result_msg:
                result_data = json.loads(result_msg['value'])
                logging.info(f"📥 CONSUMED: {result_data['location']}")
                logging.info(f"    Original: {result_data['temperature']}°C")
                logging.info(f"    Converted: {result_data.get('temperature_fahrenheit', 'N/A')}°F") 
                logging.info(f"    Quality: {result_data['data_quality_score']:.2f}")
                logging.info(f"    Processed at: {result_data['processed_timestamp']}")
                
        logging.info("-" * 40)
        time.sleep(2)  # Simulate real-time processing
    
    logging.info("=" * 60)
    logging.info("Mock stream processing complete!")
    logging.info(f"Topics created: {mock_kafka.list_topics()}")
    logging.info("✓ This demonstrates how your weather processor will work with real Kafka")

def main():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("  Weather Processor - Mock Demo (No Kafka Required)")
    print("=" * 60)
    print()
    
    logging.info("This demo simulates your Kafka stream processing pipeline")
    logging.info("It shows exactly what will happen when you run with real Kafka")
    print()
    
    try:
        simulate_stream_processing()
        
        print("\n" + "=" * 60)
        print("  To run with real Kafka:")
        print("=" * 60)
        print("1. Start Docker Desktop")
        print("2. Run: docker-compose up -d")
        print("3. Wait for Kafka to start (about 1-2 minutes)")
        print("4. Run: python main.py")
        print("5. In another terminal: python test_producer.py")
        print("6. In another terminal: python test_consumer.py")
        print()
        
    except KeyboardInterrupt:
        logging.info("Demo interrupted by user")
    except Exception as e:
        logging.error(f"Demo error: {e}")

if __name__ == "__main__":
    main()
