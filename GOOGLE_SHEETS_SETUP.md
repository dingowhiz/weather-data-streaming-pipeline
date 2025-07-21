# 📊 Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration to automatically save weather data.

## 📋 Prerequisites

1. **Google Account** with access to Google Sheets
2. **Google Cloud Console Project** with Sheets API enabled
3. **Service Account** with JSON credentials

## 🛠️ Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name it something like "Weather Data Processor"

### Step 2: Enable Google Sheets API

1. In your Google Cloud project, go to **APIs & Services > Library**
2. Search for "Google Sheets API"
3. Click on it and press **Enable**

### Step 3: Create Service Account

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > Service Account**
3. Fill in details:
   - Name: `weather-data-service`
   - Description: `Service account for weather data processor`
4. Click **Create and Continue**
5. Skip role assignment (click **Continue**)
6. Skip user access (click **Done**)

### Step 4: Generate JSON Key

1. Find your service account in the list
2. Click on the service account email
3. Go to **Keys** tab
4. Click **Add Key > Create New Key**
5. Select **JSON** format
6. Click **Create**
7. Save the downloaded JSON file as `credentials.json` in your project folder

### Step 5: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Rename it to: `Singapore Weather` (or update `config.py`)
4. **Important**: Share the sheet with your service account email
   - Click **Share** button
   - Add the service account email (from credentials.json)
   - Give **Editor** permissions

### Step 6: Update Configuration

Your `config.py` should already have these settings:

```python
# Google Sheets Configuration
GOOGLE_SHEETS_ENABLED = os.getenv('GOOGLE_SHEETS_ENABLED', 'true').lower() == 'true'
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEETS_WORKBOOK_NAME = os.getenv('GOOGLE_SHEETS_WORKBOOK_NAME', 'Singapore Weather')
GOOGLE_SHEETS_WORKSHEET_INDEX = int(os.getenv('GOOGLE_SHEETS_WORKSHEET_INDEX', '0'))
```

## 📁 File Structure

After setup, your project should look like:

```
weather_processor/
├── credentials.json          # ← Your Google service account key
├── config.py                # ← Configuration with Google Sheets settings
├── main.py                  # ← Updated with Google Sheets integration
├── weather_producer.py      # ← Weather data producer
└── ...other files
```

## 🔒 Security Notes

1. **Never commit `credentials.json` to version control**
2. Add it to your `.gitignore`:
   ```
   credentials.json
   *.json
   ```
3. Keep the file secure and don't share it

## 🧪 Testing

1. **Test the setup**:
   ```powershell
   .\env\Scripts\activate
   python -c "import pygsheets; gc = pygsheets.authorize(service_file='credentials.json'); print('✅ Google Sheets connection successful!')"
   ```

2. **Run the weather system**:
   ```powershell
   start_weather_streaming.bat
   ```

3. **Check your Google Sheet** - you should see:
   - Headers in row 1: `Timestamp`, `Temperature_C`, `Temperature_F`, `Humidity`, `Wind_Speed`, `Weather_Description`
   - Weather data being added automatically

## 📊 Expected Sheet Output

Your Google Sheet will look like:

| Timestamp | Temperature_C | Temperature_F | Humidity | Wind_Speed | Weather_Description |
|-----------|---------------|---------------|----------|------------|-------------------|
| 2025-07-21 18:34:15 UTC | 29.8 | 85.6 | 66 | 9.8 | Overcast |
| 2025-07-21 18:39:15 UTC | 30.1 | 86.2 | 68 | 8.5 | Partly cloudy |

## 🚨 Troubleshooting

### Common Issues:

**1. "credentials.json not found"**
- Make sure the file is in the project root
- Check the filename is exactly `credentials.json`

**2. "Access denied" or "Sheet not found"**
- Make sure you shared the sheet with the service account email
- Check the sheet name matches `GOOGLE_SHEETS_WORKBOOK_NAME` in config

**3. "API not enabled"**
- Ensure Google Sheets API is enabled in Google Cloud Console

**4. "Service account has no access"**
- Share your Google Sheet with the service account email
- Give Editor permissions

## ⚙️ Environment Variables (Optional)

You can customize settings with environment variables:

```powershell
# Disable Google Sheets integration
$env:GOOGLE_SHEETS_ENABLED = "false"

# Use different credentials file
$env:GOOGLE_SHEETS_CREDENTIALS_FILE = "my-credentials.json"

# Use different sheet name
$env:GOOGLE_SHEETS_WORKBOOK_NAME = "Weather Data 2025"
```

## 🎯 What Happens Now

Once set up, the weather processor will:

1. ✅ **Fetch** real weather data every 5 minutes
2. ✅ **Process** the data (temperature conversion, quality scoring)
3. ✅ **Stream** through Kafka
4. ✅ **Save** to Google Sheets automatically
5. ✅ **Display** in the console

Your Google Sheet becomes a **permanent record** of all processed weather data! 📈

---

**🌟 Happy Weather Tracking!** 🌟
