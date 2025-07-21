"""
Configuration settings for the weather processor application
"""
import os

# Application settings
LATITUDE = os.getenv('LATITUDE', '1.3642662')
LONGITUDE = os.getenv('LONGITUDE', '103.8665583')

# Weather API settings
WEATHER_API_FETCH_INTERVAL = int(os.getenv('WEATHER_API_FETCH_INTERVAL', '300'))  # 5 minutes
WEATHER_API_TIMEOUT = int(os.getenv('WEATHER_API_TIMEOUT', '10'))  # 10 seconds

# Kafka Configuration
KAFKA_BROKER_ADDRESS = os.getenv('KAFKA_BROKER_ADDRESS', 'localhost:9092')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', 'weather_processor')
KAFKA_AUTO_OFFSET_RESET = os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')

# Topics
INPUT_TOPIC = os.getenv('INPUT_TOPIC', 'weather_data_demo')
OUTPUT_TOPIC = os.getenv('OUTPUT_TOPIC', 'tmp')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

# Connection settings
KAFKA_CONNECTION_TIMEOUT = int(os.getenv('KAFKA_CONNECTION_TIMEOUT', '5'))

# Google Sheets Configuration
GOOGLE_SHEETS_ENABLED = os.getenv('GOOGLE_SHEETS_ENABLED', 'true').lower() == 'true'
GOOGLE_SHEETS_AUTH_METHOD = os.getenv('GOOGLE_SHEETS_AUTH_METHOD', 'service_account')  # 'service_account' or 'oauth2'
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY', '')  # For read-only operations only
GOOGLE_SHEETS_WORKBOOK_NAME = os.getenv('GOOGLE_SHEETS_WORKBOOK_NAME', 'Singapore Weather')
GOOGLE_SHEETS_WORKBOOK_ID = os.getenv('GOOGLE_SHEETS_WORKBOOK_ID', '')  # Alternative to workbook name
GOOGLE_SHEETS_WORKSHEET_INDEX = int(os.getenv('GOOGLE_SHEETS_WORKSHEET_INDEX', '0'))
GOOGLE_SHEETS_UPDATE_INTERVAL = int(os.getenv('GOOGLE_SHEETS_UPDATE_INTERVAL', '60'))  # seconds