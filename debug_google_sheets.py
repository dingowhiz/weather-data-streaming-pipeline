"""
Debug Google Sheets setup - inspect actual sheet structure
"""
import pygsheets
import config

def debug_google_sheets():
    """Debug Google Sheets connection to see actual structure"""
    
    print("🔍 Debugging Google Sheets Setup")
    print("=" * 50)
    
    try:
        # Connect to Google API
        print("🔐 Authorizing with Google API...")
        google_api = pygsheets.authorize(service_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE)
        print("✅ Authorization successful")
        
        # Open workbook
        print(f"📂 Opening workbook: {config.GOOGLE_SHEETS_WORKBOOK_NAME}")
        workbook = google_api.open(config.GOOGLE_SHEETS_WORKBOOK_NAME)
        print(f"✅ Workbook opened: {workbook.title}")
        print(f"📝 Workbook ID: {workbook.id}")
        print(f"🌐 URL: https://docs.google.com/spreadsheets/d/{workbook.id}")
        
        # List all worksheets
        print(f"\n📋 Found {len(workbook.worksheets())} worksheets:")
        for i, worksheet in enumerate(workbook.worksheets()):
            print(f"  [{i}] {worksheet.title} (ID: {worksheet.id})")
            
        # Check the worksheet we're trying to use
        print(f"\n🎯 Trying to access worksheet at index {config.GOOGLE_SHEETS_WORKSHEET_INDEX}:")
        try:
            target_sheet = workbook[config.GOOGLE_SHEETS_WORKSHEET_INDEX]
            print(f"✅ Target worksheet: {target_sheet.title}")
            
            # Check if it has data
            print(f"📏 Sheet dimensions: {target_sheet.rows}x{target_sheet.cols}")
            
            # Read first few rows to see existing data
            print("\n📖 First 5 rows of data:")
            try:
                data = target_sheet.get_values('A1:Z5')
                for i, row in enumerate(data, 1):
                    if row:  # Only show non-empty rows
                        print(f"  Row {i}: {row}")
                    else:
                        print(f"  Row {i}: (empty)")
            except Exception as e:
                print(f"  ⚠️  Could not read data: {e}")
                
        except Exception as e:
            print(f"❌ Could not access target worksheet: {e}")
            
        print(f"\n✅ Debug complete!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    debug_google_sheets()
