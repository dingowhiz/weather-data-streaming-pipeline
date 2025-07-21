"""
Test script to consume processed weather data from the output topic
Run this after starting the weather processor to see the results
"""
import json
import logging
from confluent_kafka import Consumer, KafkaException
import config

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create consumer
    consumer = Consumer({
        'bootstrap.servers': config.KAFKA_BROKER_ADDRESS,
        'group.id': 'test_consumer',
        'auto.offset.reset': 'earliest'
    })
    
    try:
        # Subscribe to output topic
        consumer.subscribe([config.OUTPUT_TOPIC])
        logging.info(f"Subscribed to topic: {config.OUTPUT_TOPIC}")
        logging.info("Waiting for messages... (Press Ctrl+C to stop)")
        
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                logging.error(f"Consumer error: {msg.error()}")
                continue
            
            # Process message
            key = msg.key().decode('utf-8') if msg.key() else None
            value = json.loads(msg.value().decode('utf-8'))
            
            logging.info(f"Received processed message:")
            logging.info(f"  Key: {key}")
            logging.info(f"  Value: {json.dumps(value, indent=2)}")
            logging.info(f"  Partition: {msg.partition()}")
            logging.info(f"  Offset: {msg.offset()}")
            logging.info("-" * 50)
            
    except KeyboardInterrupt:
        logging.info("Consumer interrupted by user")
    except KafkaException as e:
        logging.error(f"Kafka error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        consumer.close()
        logging.info("Consumer closed")

if __name__ == "__main__":
    main()
