"""
CSV Storage Alternative for Weather Data
Use this when Google Sheets authentication is not available
"""
import csv
import os
import logging
from datetime import datetime
import config

class WeatherCSVStorage:
    def __init__(self, filename='weather_data.csv'):
        self.filename = filename
        self.headers = [
            'Timestamp', 'Temperature_C', 'Temperature_F', 'Humidity', 
            'Wind_Speed', 'Weather_Description', 'Data_Quality', 
            'Processing_Pipeline', 'Data_Source', 'Location'
        ]
        self.setup_csv_file()
    
    def setup_csv_file(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.filename):
            try:
                with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.headers)
                logging.info(f"Created CSV file: {self.filename}")
            except Exception as e:
                logging.error(f"Failed to create CSV file: {e}")
    
    def write_weather_data(self, weather_data):
        """Write weather data to CSV file"""
        try:
            row_data = [
                weather_data.get('processed_timestamp', ''),
                weather_data.get('temperature_celsius', weather_data.get('temperature', '')),
                weather_data.get('temperature_fahrenheit', ''),
                weather_data.get('humidity', ''),
                weather_data.get('wind_speed', ''),
                weather_data.get('weather_description', ''),
                weather_data.get('data_quality_score', ''),
                weather_data.get('processing_pipeline', 'weather_stream_processor'),
                weather_data.get('data_source', ''),
                weather_data.get('location', '')
            ]
            
            with open(self.filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_data)
            
            logging.info(f"Weather data written to CSV: {self.filename}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to write to CSV file: {e}")
            return False
    
    def get_latest_records(self, count=10):
        """Get the latest N records from CSV"""
        try:
            if not os.path.exists(self.filename):
                return []
            
            with open(self.filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                records = list(reader)
                return records[-count:] if records else []
                
        except Exception as e:
            logging.error(f"Failed to read CSV file: {e}")
            return []
    
    def get_file_path(self):
        """Get absolute path to CSV file"""
        return os.path.abspath(self.filename)

# Global CSV storage instance
weather_csv = WeatherCSVStorage() if config.GOOGLE_SHEETS_ENABLED else None

def setup_csv_storage():
    """Setup CSV storage as alternative to Google Sheets"""
    global weather_csv
    try:
        weather_csv = WeatherCSVStorage()
        logging.info(f"CSV storage initialized: {weather_csv.get_file_path()}")
        return weather_csv
    except Exception as e:
        logging.error(f"Failed to setup CSV storage: {e}")
        return None

def write_to_csv(weather_data):
    """Write weather data to CSV file"""
    if weather_csv is None:
        return False
    return weather_csv.write_weather_data(weather_data)

def main():
    """Test CSV storage functionality"""
    import json
    
    # Test data
    test_data = {
        "processed_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "temperature_celsius": 28.5,
        "temperature_fahrenheit": 83.3,
        "humidity": 72,
        "wind_speed": 8.2,
        "weather_description": "Partly cloudy",
        "data_quality_score": 1.0,
        "processing_pipeline": "weather_stream_processor",
        "data_source": "Open-Meteo API",
        "location": "Singapore"
    }
    
    print("🧪 Testing CSV Storage")
    print("=" * 40)
    
    # Setup CSV storage
    csv_storage = setup_csv_storage()
    if csv_storage:
        print(f"✅ CSV file created: {csv_storage.get_file_path()}")
        
        # Write test data
        success = csv_storage.write_weather_data(test_data)
        if success:
            print("✅ Test data written successfully")
            
            # Read back data
            records = csv_storage.get_latest_records(1)
            if records:
                print("✅ Data read back successfully:")
                print(json.dumps(records[0], indent=2))
            else:
                print("❌ Failed to read data back")
        else:
            print("❌ Failed to write test data")
    else:
        print("❌ Failed to setup CSV storage")

if __name__ == "__main__":
    main()
