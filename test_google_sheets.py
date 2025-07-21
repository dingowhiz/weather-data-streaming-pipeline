"""
Test Google Sheets integration
Run this to verify your Google Sheets setup before running the full pipeline
"""
import logging
import sys
import config

def test_google_sheets():
    """Test Google Sheets connection and setup"""
    
    print("🧪 Testing Google Sheets Integration")
    print("=" * 50)
    
    # Check if Google Sheets is enabled
    if not config.GOOGLE_SHEETS_ENABLED:
        print("❌ Google Sheets integration is DISABLED")
        print("💡 Set GOOGLE_SHEETS_ENABLED=true in config.py or environment")
        return False
    
    print("✅ Google Sheets integration is ENABLED")
    
    # Check credentials file
    import os
    if not os.path.exists(config.GOOGLE_SHEETS_CREDENTIALS_FILE):
        print(f"❌ Credentials file not found: {config.GOOGLE_SHEETS_CREDENTIALS_FILE}")
        print("💡 Please follow GOOGLE_SHEETS_SETUP.md to create credentials.json")
        return False
    
    print(f"✅ Credentials file found: {config.GOOGLE_SHEETS_CREDENTIALS_FILE}")
    
    # Test pygsheets import
    try:
        import pygsheets
        print("✅ pygsheets library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pygsheets: {e}")
        print("💡 Run: pip install pygsheets")
        return False
    
    # Test Google API connection
    try:
        print("🔍 Testing Google API connection...")
        google_api = pygsheets.authorize(service_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
        print("✅ Google API authorization successful")
    except Exception as e:
        print(f"❌ Google API authorization failed: {e}")
        print("💡 Check your credentials.json file and Google Cloud setup")
        return False
    
    # Test workbook access
    try:
        print(f"🔍 Testing access to workbook: {config.GOOGLE_SHEETS_WORKBOOK_NAME}")
        workbook = google_api.open(config.GOOGLE_SHEETS_WORKBOOK_NAME)
        print(f"✅ Workbook opened successfully: {workbook.title}")
    except Exception as e:
        print(f"❌ Failed to open workbook: {e}")
        print("💡 Make sure:")
        print("   1. The Google Sheet exists")
        print("   2. It's named exactly:", config.GOOGLE_SHEETS_WORKBOOK_NAME)
        print("   3. You've shared it with your service account email")
        return False
    
    # Test worksheet access
    try:
        sheet = workbook[config.GOOGLE_SHEETS_WORKSHEET_INDEX]
        print(f"✅ Worksheet accessed successfully: {sheet.title}")
    except Exception as e:
        print(f"❌ Failed to access worksheet: {e}")
        return False
    
    # Test writing
    try:
        print("🔍 Testing write access...")
        
        # Write test headers (check if they already exist)
        try:
            existing_data = sheet.get_values('A1', 'F1')
            if not existing_data or not existing_data[0]:
                # No headers exist, write them
                test_headers = ["Timestamp", "Temperature_C", "Temperature_F", "Humidity", "Wind_Speed", "Weather_Description"]
                sheet.update_values('A1:F1', [test_headers])
                print("✅ Headers written to row 1")
            else:
                print("✅ Headers already exist in row 1")
        except Exception as header_error:
            print(f"⚠️  Header check failed, trying to write headers: {header_error}")
            test_headers = ["Timestamp", "Temperature_C", "Temperature_F", "Humidity", "Wind_Speed", "Weather_Description"]
            sheet.update_values('A1:F1', [test_headers])
        
        # Write test data to next available row
        from datetime import datetime
        test_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            "25.0",
            "77.0", 
            "60",
            "10.5",
            "Test - Clear sky"
        ]
        
        # Find next empty row
        try:
            next_row = len(sheet.get_all_values()) + 1
            range_to_update = f'A{next_row}:F{next_row}'
            sheet.update_values(range_to_update, [test_data])
            print(f"✅ Test data written to row {next_row}")
        except Exception as write_error:
            # Fallback: just append to row 2
            sheet.update_values('A2:F2', [test_data])
            print("✅ Test data written to row 2")
        
        print("✅ Write test successful - check your Google Sheet!")
        print(f"🌐 Sheet URL: https://docs.google.com/spreadsheets/d/{workbook.id}")
        
    except Exception as e:
        print(f"❌ Write test failed: {e}")
        print("💡 Make sure the service account has Editor permissions on the sheet")
        return False
    
    print("\n🎉 Google Sheets integration is working perfectly!")
    print("🚀 You can now run the full weather streaming pipeline")
    return True

def main():
    """Main test function"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        success = test_google_sheets()
        if success:
            print("\n✅ All tests passed! Google Sheets is ready.")
            sys.exit(0)
        else:
            print("\n❌ Tests failed. Please fix the issues above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
