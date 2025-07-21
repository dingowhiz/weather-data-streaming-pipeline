"""
Helper script to verify your credentials.json file
Run this after downloading credentials from Google Cloud Console
"""
import json
import os

def check_credentials():
    print("🔍 Checking Google Sheets Credentials")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found in current directory")
        print()
        print("📋 To get credentials.json:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Create Credentials → Service Account")
        print("3. Download JSON key")
        print("4. Rename to 'credentials.json'")
        print("5. Move to this folder")
        return False
    
    try:
        # Read and validate JSON
        with open("credentials.json", "r") as f:
            creds = json.load(f)
        
        print("✅ credentials.json found and valid!")
        print()
        
        # Extract key information
        email = creds.get("client_email", "NOT_FOUND")
        project_id = creds.get("project_id", "UNKNOWN")
        private_key_id = creds.get("private_key_id", "NOT_FOUND")
        
        print("📄 Credentials Details:")
        print(f"   📧 Service Account Email: {email}")
        print(f"   🏗️  Project ID: {project_id}")
        print(f"   🔑 Private Key ID: {private_key_id[:8]}...")
        print()
        
        print("📋 Next Steps:")
        print("1. Create Google Sheet named: 'Singapore Weather'")
        print("2. Share sheet with service account email above")
        print("3. Give 'Editor' permissions")
        print("4. Run: python test_google_sheets.py")
        print()
        print("🔗 Quick links:")
        print(f"   📊 Google Sheets: https://sheets.google.com")
        print(f"   ⚙️  Google Cloud: https://console.cloud.google.com")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

if __name__ == "__main__":
    check_credentials()
