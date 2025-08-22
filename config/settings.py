import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent
        
        # SwitchBot API 設定
        self.SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
        self.SWITCHBOT_SECRET = os.getenv("SWITCHBOT_SECRET")
        self.SWITCHBOT_DEVICE_ID = os.getenv("SWITCHBOT_DEVICE_ID")
        
        # データベース設定
        self.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
        self.DATABASE_PATH = self.BASE_DIR / os.getenv("DATABASE_PATH", "data/temperature.db")
        self.CSV_PATH = self.BASE_DIR / os.getenv("CSV_PATH", "data/temperature.csv")
        
        # ログ設定
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = self.BASE_DIR / os.getenv("LOG_FILE", "logs/temperature_logger.log")
        
        # データ保持設定
        self.DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))
        
        # ディレクトリを作成
        self._create_directories()
    
    def _create_directories(self):
        """必要なディレクトリを作成"""
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def validate(self):
        """設定の妥当性をチェック"""
        required_settings = [
            ("SWITCHBOT_TOKEN", self.SWITCHBOT_TOKEN),
            ("SWITCHBOT_SECRET", self.SWITCHBOT_SECRET),
            ("SWITCHBOT_DEVICE_ID", self.SWITCHBOT_DEVICE_ID)
        ]
        
        missing_settings = [name for name, value in required_settings if not value]
        
        if missing_settings:
            raise ValueError(f"必要な環境変数が設定されていません: {', '.join(missing_settings)}")
        
        return True

settings = Settings()