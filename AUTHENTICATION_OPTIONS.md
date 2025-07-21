# 🔑 Google Sheets Authentication Options

## ❗ Important: API Key Limitations

**Google Sheets API keys have severe limitations:**
- ✅ **READ operations only** (view data)
- ❌ **NO WRITE operations** (cannot add/modify data)
- ❌ **Cannot create sheets or modify content**

Since our weather processor needs to **WRITE data** to Google Sheets, API keys won't work for our use case.

## 🛠️ Available Authentication Methods

### 1. 🏆 **Service Account (RECOMMENDED)**
- ✅ **Full read/write access**
- ✅ **No user interaction required**
- ✅ **Perfect for automated systems**
- ✅ **Secure and robust**

**How to set up:**
```powershell
# Follow the Google Cloud Console setup
# Download credentials.json
# Set in environment or use default location
```

### 2. 🔐 **OAuth2 (Interactive)**
- ✅ **Full read/write access**
- ❌ **Requires user login each time**
- ❌ **Not suitable for automated systems**

### 3. 🔑 **API Key (LIMITED)**
- ✅ **Simple to set up**
- ❌ **READ ONLY - Cannot write weather data**
- ❌ **Useless for our weather processor**

## ⚡ **Quick Setup Options**

### Option A: Use Service Account (Best)
```powershell
# 1. Get credentials.json from Google Cloud Console
# 2. Place it in your project folder
# 3. Run the system
start_weather_streaming.bat
```

### Option B: Use Public Google Sheet (Alternative)
If you don't want to set up authentication, you can:

1. **Create a public Google Sheet**
2. **Make it editable by anyone with the link**
3. **Use Google Forms** to submit data
4. **Use webhooks** to send data

### Option C: Use Alternative Storage
Instead of Google Sheets, you could use:
- **CSV files** (local storage)
- **SQLite database** (local database)
- **InfluxDB** (time-series database)
- **MongoDB** (document database)

## 🔧 **Current Configuration Options**

Your `config.py` now supports:

```python
# Method 1: Service Account (credentials.json)
GOOGLE_SHEETS_AUTH_METHOD = 'service_account'
GOOGLE_SHEETS_CREDENTIALS_FILE = 'credentials.json'

# Method 2: OAuth2 (user login)
GOOGLE_SHEETS_AUTH_METHOD = 'oauth2'

# Method 3: API Key (read-only, not useful for our case)
GOOGLE_SHEETS_API_KEY = 'your-api-key-here'

# Sheet identification
GOOGLE_SHEETS_WORKBOOK_NAME = 'Singapore Weather'
GOOGLE_SHEETS_WORKBOOK_ID = 'your-sheet-id-here'  # Alternative to name
```

## 🚀 **Recommended Next Steps**

### For Full Functionality:
1. **Get credentials.json** from Google Cloud Console
2. **Place it in your project folder**
3. **Test**: `python test_google_sheets.py`
4. **Run**: `start_weather_streaming.bat`

### For Quick Testing without Google Sheets:
1. **Disable Google Sheets** in config.py:
   ```python
   GOOGLE_SHEETS_ENABLED = False
   ```
2. **Use CSV logging** instead (I can help set this up)

## 💡 **Alternative: CSV File Storage**

Would you like me to create a CSV file storage option instead? This would:
- ✅ **Store all weather data locally**
- ✅ **No authentication required**
- ✅ **Easy to import into Excel/Google Sheets later**
- ✅ **Works immediately**

Let me know which option you prefer!

---

**Bottom line:** For writing weather data, you need either:
1. **Service Account credentials.json** (recommended)
2. **Alternative storage method** (CSV, database, etc.)

API keys alone won't work for writing data to Google Sheets.
