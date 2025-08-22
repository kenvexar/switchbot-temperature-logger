# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Essential Commands
```bash
# Install/sync dependencies
uv sync

# Test API connection and configuration
uv run main.py --test

# Test Google Sheets connection
uv run main.py --test-sheets

# Run once (single data collection)
uv run main.py --once

# Note: Scheduling is handled by Google Cloud Scheduler with Cloud Functions

# Clean up old data
uv run main.py --cleanup

# List available SwitchBot devices
uv run main.py --list-devices
```

### Development Setup
```bash
# Create environment file from template
cp .env.example .env
# Edit .env with actual API credentials

# View logs
tail -f logs/temperature_logger.log

# Check SQLite data
sqlite3 data/temperature.db "SELECT * FROM temperature_data ORDER BY timestamp DESC LIMIT 10;"
```

### Google Cloud Functions Deployment
```bash
# Set environment variables before deployment
export SWITCHBOT_TOKEN="your-token"
export SWITCHBOT_SECRET="your-secret"
export SWITCHBOT_DEVICE_ID="your-device-id"

# Deploy using the script
chmod +x deploy.sh
./deploy.sh

# Or deploy manually
gcloud functions deploy collect-temperature-data \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point collect_temperature_data \
  --source . \
  --timeout 540s \
  --memory 256MB \
  --region asia-northeast1

# Test the deployed function
curl -X POST "https://REGION-PROJECT.cloudfunctions.net/collect-temperature-data" \
  -H "Content-Type: application/json" \
  -d '{"action": "test"}'

# Or use the free-tier deployment script
chmod +x free-tier-deploy.sh
./free-tier-deploy.sh
```

## Architecture Overview

### Core Components
- **main.py**: Entry point with CLI argument handling and Google Cloud Functions HTTP trigger
- **src/switchbot_api.py**: SwitchBotAPI class for device communication
- **src/data_storage.py**: Abstract DataStorage with CSVStorage/SQLiteStorage implementations
- **src/google_sheets.py**: GoogleSheetsClient for cloud data backup
- **config/settings.py**: Environment-based configuration management

### Data Flow
1. Google Cloud Scheduler triggers HTTP request to Cloud Functions
2. SwitchBotAPI retrieves temperature/humidity/light data from SwitchBot Hub 2
3. DataStorage saves to temporary SQLite database or Google Sheets
4. GoogleSheetsClient optionally backs up to Google Sheets (日時 + 温度のみ)
5. Cloud Functions returns success/error response

### Storage Backends
- **CSV**: Simple file-based storage with configurable path (local development)
- **SQLite**: Relational database with automatic schema creation (temporary in Cloud Functions)
- **Google Sheets**: Primary cloud storage with Japanese time format (YYYY 年 MM 月 DD 日 HH:MM:SS)

### Configuration
Environment variables in `.env` file:
- `SWITCHBOT_TOKEN`, `SWITCHBOT_SECRET`, `SWITCHBOT_DEVICE_ID`: API access
- `DATABASE_TYPE`: "sqlite" or "csv"
- `DATABASE_PATH`, `CSV_PATH`: Storage file paths
- `GOOGLE_SHEETS_SPREADSHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_KEY`: Optional cloud backup
- `DATA_RETENTION_DAYS`: Data cleanup retention period

## Code Conventions

### Language & Style
- Python 3.11+ with Japanese comments and docstrings
- PascalCase for classes, snake_case for functions/variables
- Type hints for all function parameters and returns
- Comprehensive error handling with Japanese log messages

### Testing
No automated test framework configured. Test manually using:
- `uv run main.py --test` for API connectivity
- `uv run main.py --test-sheets` for Google Sheets connectivity
- `uv run main.py --once` for single execution verification

### Package Management
Uses `uv` with `pyproject.toml` for local development, `requirements.txt` for Cloud Functions. Dependencies include:
- `requests` for HTTP API calls
- `gspread` + `google-auth` for Google Sheets integration
- `python-dotenv` for environment configuration
- `functions-framework` for Google Cloud Functions HTTP triggers