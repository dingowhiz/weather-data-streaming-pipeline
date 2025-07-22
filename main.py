import logging
import json
import sys
import os
from quixstreams import Application
from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException
import config
import time
import pygsheets
from datetime import timedelta

def check_kafka_connection(broker_address, timeout=5):
    """Check if Kafka broker is accessible"""
    try:
        admin_client = AdminClient({'bootstrap.servers': broker_address})
        # Try to get metadata with a short timeout
        metadata = admin_client.list_topics(timeout=timeout)
        logging.info(f"Successfully connected to Kafka broker at {broker_address}")
        return True
    except KafkaException as e:
        logging.error(f"Failed to connect to Kafka broker at {broker_address}: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error when connecting to Kafka: {e}")
        return False

def setup_google_sheets():
    """Setup Google Sheets connection"""
    if not config.GOOGLE_SHEETS_ENABLED:
        logging.info("Google Sheets integration is disabled")
        return None, None
    
    try:
        # Check for API key
        if config.GOOGLE_SHEETS_API_KEY:
            logging.warning("Google Sheets API key detected")        
        # Check for service account credentials
        if not os.path.exists(config.GOOGLE_SHEETS_CREDENTIALS_FILE):
            logging.warning(f"Google Sheets credentials file not found: {config.GOOGLE_SHEETS_CREDENTIALS_FILE}")
            logging.info("Google Sheets integration disabled. To enable:")
            logging.info("1. Service Account Method (RECOMMENDED):")
            logging.info("   - Follow GOOGLE_SHEETS_SETUP.md to create credentials.json")
            logging.info("   - This allows READ and WRITE operations")
            logging.info("2. API Key Method (READ-ONLY):")
            logging.info("   - Set GOOGLE_SHEETS_API_KEY environment variable")
            logging.info("   - This only allows reading sheets, not writing weather data")
            logging.info("3. Or set GOOGLE_SHEETS_ENABLED=false to suppress this warning")
            return None, None
        
        # Use service account authentication (preferred method)
        if config.GOOGLE_SHEETS_AUTH_METHOD == 'service_account':
            google_api = pygsheets.authorize(service_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
        else:
            # Try OAuth2 authentication
            google_api = pygsheets.authorize()
        
        workbook = google_api.open(config.GOOGLE_SHEETS_WORKBOOK_NAME)
        sheet = workbook[config.GOOGLE_SHEETS_WORKSHEET_INDEX]
        
        # Initialize headers if needed
        headers = ["Timestamp(GMT)", "Temperature_C", "Temperature_F", "Humidity", "Wind_Speed", "Weather_Description", "Data_Quality", "Pipeline_Name"]
        try:
            # Always update headers to ensure they are correct
            sheet.update_values('A1:H1', [headers])
            logging.info("Headers updated in Google Sheet")
            
            # Verify headers were written correctly
            try:
                existing_headers = sheet.get_values('A1', 'H1')
                if existing_headers and existing_headers[0]:
                    logging.info(f"Headers confirmed: {existing_headers[0]}")
                else:
                    logging.warning("Headers may not have been written correctly")
            except Exception as verify_error:
                logging.debug(f"Header verification failed (headers likely still updated): {verify_error}")
                
        except Exception as header_error:
            logging.error(f"Failed to update headers: {header_error}")
            logging.warning("Continuing without proper headers - manual header setup may be required")
        
        logging.info(f"Google Sheets connected: {workbook.title}")
        logging.info(f"Sheet URL: https://docs.google.com/spreadsheets/d/{workbook.id}")
        return google_api, sheet
        
    except Exception as e:
        logging.warning(f"Failed to setup Google Sheets: {e}")
        return None, None

def write_to_google_sheets(sheet, weather_data):
    """Write weather data to Google Sheets"""
    if sheet is None:
        return
        
    try:
        # Prepare row data with more comprehensive information
        row_data = [
            weather_data.get('processed_timestamp', ''),
            weather_data.get('temperature_celsius', weather_data.get('temperature', '')),
            weather_data.get('temperature_fahrenheit', ''),
            weather_data.get('humidity', ''),
            weather_data.get('wind_speed', ''),
            weather_data.get('weather_description', ''),
            weather_data.get('data_quality_score', ''),
            weather_data.get('processing_pipeline', 'weather_stream_processor')
        ]
        # Append to sheet using proper range notation
        try:
            # write data
            all_values = sheet.get_all_values()
            next_row = len(all_values) + 1
            range_notation = f'A{next_row}:H{next_row}'
            sheet.update_values(range_notation, [row_data])
        except Exception as range_error:
            # Fallback: use append_table method by adding rows to end of data
            logging.warning(f"Range method failed: {range_error}, trying append_table")
            sheet.append_table(values=[row_data])
            
        logging.info("Weather data written to Google Sheets successfully")
        
    except Exception as e:
        logging.error(f"Failed to write to Google Sheets: {e}")
        raise  
      
def initializer_fn(msg):
    temperature = msg["current"]['temperature_2m']
    return {
      "open": temperature,
      "high": temperature,
      "low": temperature,
      "close": temperature,
      }
    
def reducer_fn(summary, msg):
    temperature = msg["current"]['temperature_2m']
    return {
        "open": summary["open"],  # Keep original open
        "high": max(summary["high"], temperature),
        "low": min(summary["low"], temperature), 
        "close": temperature,  # Latest temperature becomes close
    }

def main():
  logging.info("START")
  
  # Setup Google Sheets connection (non-blocking)
  google_api, google_sheet = setup_google_sheets()
  if google_sheet is not None:
      logging.info("Google Sheets integration enabled and ready")
  else:
      logging.warning("Google Sheets integration disabled or failed - continuing without it")
  
  # Check Kafka connection before proceeding
  if not check_kafka_connection(config.KAFKA_BROKER_ADDRESS, config.KAFKA_CONNECTION_TIMEOUT):
      logging.error("Cannot proceed without Kafka connection. Please ensure Kafka is running.")
      logging.info("To start Kafka:")
      logging.info("1. Start Zookeeper: bin/zookeeper-server-start.sh config/zookeeper.properties")
      logging.info("2. Start Kafka: bin/kafka-server-start.sh config/server.properties")
      logging.info(f"Current broker address: {config.KAFKA_BROKER_ADDRESS}")
      sys.exit(1)
  
  app = Application(
      broker_address = config.KAFKA_BROKER_ADDRESS,
      loglevel = config.LOG_LEVEL,
      auto_offset_reset = config.KAFKA_AUTO_OFFSET_RESET,
      consumer_group = config.KAFKA_CONSUMER_GROUP,
  )
# with app get_producer() as producer:
#     weather = get_weather)
#     producer. produce(
#         topic="weather_data_demo",
#         key="London",
#         value=json.dumps(weather),

# with app.get_consumer() as consumer:
#      consumer.subscribe(["weather_data_demo"])

#      while True:
#          msg = consumer.poll(1)

#          if msg is None:
#              print("Waiting...")
#          elif msg.error() is not None:
#              raise Exception(msg.error())
#          else:
#              key = msg.key().decode('utf8')
#              value = json.loads(msg.value())
#              offset = msg.offset()

#              print(f"{offset} {key} {value}")
#              consumer.store_offsets(msg)

  try:
      input_topic = app.topic(config.INPUT_TOPIC)
      output_topic = app.topic(config.OUTPUT_TOPIC)
      logging.info(f"Created topics: input='{config.INPUT_TOPIC}', output='{config.OUTPUT_TOPIC}'")
  except KafkaException as e:
      logging.error(f"Failed to create topics: {e}")
      logging.info("Please ensure the topics exist or that you have permissions to create them")
      sys.exit(1)
  except Exception as e:
      logging.error(f"Unexpected error creating topics: {e}")
      sys.exit(1)

  def transform(msg):
      """Transform weather data - add processing timestamp and temperature in Fahrenheit to Google Sheets"""
      
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
              new_msg['temperature_celsius'] = celsius  # Keep original
      
      # Add weather condition description based on weather code (Open-Meteo format)
      if 'weather_code' in new_msg and isinstance(new_msg['weather_code'], int):
          weather_descriptions = {
              0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
              45: "Fog", 48: "Depositing rime fog",
              51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
              61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
              71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
              95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
          }
          new_msg['weather_description'] = weather_descriptions.get(new_msg['weather_code'], "Unknown")
      
      # Add data quality score based on completeness
      required_fields = ['timestamp', 'location', 'temperature', 'humidity']
      present_fields = sum(1 for field in required_fields if field in new_msg and new_msg[field] is not None)
      new_msg['data_quality_score'] = present_fields / len(required_fields)
      
      # Add enrichment metadata
      new_msg['processing_pipeline'] = 'weather_stream_processor'
      new_msg['processor_version'] = '1.2.0'
      
      # Write to Google Sheets if enabled (non-blocking)
      if google_sheet is not None:
          try:
              write_to_google_sheets(google_sheet, new_msg)
              logging.debug("Data written to Google Sheets")
          except Exception as e:
              logging.warning(f"Failed to write to Google Sheets (continuing anyway): {e}")
      
      logging.debug("Transformed message: %s", new_msg)
      
      return new_msg

  sdf = app.dataframe(input_topic)
  sdf = sdf.tumbling_window(duration_ms=timedelta(hours=1))
  sdf = sdf.reduce(
      initializer=initializer_fn,
      reducer=reducer_fn
  )
  sdf = sdf.final()
  sdf = sdf.update(lambda msg: logging.debug("Updated message: %s", msg))
  
  sdf = sdf.apply(transform)
  sdf = sdf.to_topic(output_topic)

  try:
      logging.info("Starting stream processing...")
      app.run(sdf)
  except KafkaException as e:
      logging.error(f"Kafka error during stream processing: {e}")
      sys.exit(1)
  except Exception as e:
      logging.error(f"Unexpected error during stream processing: {e}")
      sys.exit(1)

if __name__ == "__main__":
  try:
     logging.basicConfig(
         level=getattr(logging, config.LOG_LEVEL.upper()),
         format='%(asctime)s - %(levelname)s - %(message)s'
     )
     main()
  except KeyboardInterrupt:
     logging.info("Application interrupted by user")
  except KafkaException as e:
     logging.error(f"Kafka error: {e}")
     sys.exit(1)
  except Exception as e:
     logging.error(f"Unexpected application error: {e}")
     sys.exit(1)
  