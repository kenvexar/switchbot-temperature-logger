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

# Run continuous monitoring (executes at :00 and :30 minutes each hour)
uv run main.py

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

## Architecture Overview

### Core Components
- **main.py**: Entry point with CLI argument handling and main execution loops
- **src/switchbot_api.py**: SwitchBotAPI class for device communication
- **src/data_storage.py**: Abstract DataStorage with CSVStorage/SQLiteStorage implementations
- **src/google_sheets.py**: GoogleSheetsClient for cloud data backup
- **src/scheduler.py**: TemperatureScheduler for periodic execution
- **config/settings.py**: Environment-based configuration management

### Data Flow
1. SwitchBotAPI retrieves temperature/humidity/light data from SwitchBot Hub 2
2. DataStorage saves to local CSV or SQLite database
3. GoogleSheetsClient optionally backs up to Google Sheets (日時 + 温度のみ)
4. TemperatureScheduler manages periodic execution and cleanup

### Storage Backends
- **CSV**: Simple file-based storage with configurable path
- **SQLite**: Relational database with automatic schema creation
- **Google Sheets**: Cloud backup with Japanese time format (YYYY 年 MM 月 DD 日 HH:MM:SS)

### Configuration
Environment variables in `.env` file:
- `SWITCHBOT_TOKEN`, `SWITCHBOT_SECRET`, `SWITCHBOT_DEVICE_ID`: API access
- `DATABASE_TYPE`: "sqlite" or "csv"
- `DATABASE_PATH`, `CSV_PATH`: Storage file paths
- `GOOGLE_SHEETS_SPREADSHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_KEY`: Optional cloud backup
- `RECORD_INTERVAL_MINUTES`: Legacy parameter (now runs at :00 and :30 each hour)
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
Uses `uv` with `pyproject.toml`. Dependencies include:
- `requests` for HTTP API calls
- `schedule` for periodic execution
- `gspread` + `google-auth` for Google Sheets integration
- `python-dotenv` for environment configuration