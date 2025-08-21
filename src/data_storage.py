import csv
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class DataStorage(ABC):
    """データストレージの抽象基底クラス"""
    
    @abstractmethod
    def save_temperature_data(self, data: Dict) -> bool:
        """温度データを保存"""
        pass
    
    @abstractmethod
    def get_recent_data(self, hours: int = 24) -> List[Dict]:
        """最近のデータを取得"""
        pass
    
    @abstractmethod
    def cleanup_old_data(self, days: int) -> int:
        """古いデータを削除"""
        pass

class CSVStorage(DataStorage):
    """CSV ファイルによるデータストレージ"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """CSV ファイルが存在しない場合は作成"""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'device_id', 'temperature', 'humidity',
                    'light_level', 'device_type', 'version'
                ])
    
    def save_temperature_data(self, data: Dict) -> bool:
        """温度データを CSV に保存"""
        try:
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data.get('timestamp'),
                    data.get('device_id'),
                    data.get('temperature'),
                    data.get('humidity'),
                    data.get('light_level'),
                    data.get('device_type'),
                    data.get('version')
                ])
            self.logger.info(f"データを保存しました: {data.get('timestamp')}")
            return True
        except Exception as e:
            self.logger.error(f"CSV への保存に失敗しました: {e}")
            return False
    
    def get_recent_data(self, hours: int = 24) -> List[Dict]:
        """最近のデータを CSV から取得"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_data = []
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                    if timestamp >= cutoff_time:
                        recent_data.append(row)
            
            return recent_data
        except Exception as e:
            self.logger.error(f"CSV からのデータ取得に失敗しました: {e}")
            return []
    
    def cleanup_old_data(self, days: int) -> int:
        """古いデータを削除"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            temp_file = self.file_path.with_suffix('.tmp')
            deleted_count = 0
            
            with open(self.file_path, 'r', encoding='utf-8') as input_f, \
                 open(temp_file, 'w', newline='', encoding='utf-8') as output_f:
                reader = csv.DictReader(input_f)
                writer = csv.DictWriter(output_f, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                for row in reader:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                    if timestamp >= cutoff_time:
                        writer.writerow(row)
                    else:
                        deleted_count += 1
            
            temp_file.replace(self.file_path)
            self.logger.info(f"{deleted_count} 件の古いデータを削除しました")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"古いデータの削除に失敗しました: {e}")
            return 0

class SQLiteStorage(DataStorage):
    """SQLite データベースによるデータストレージ"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """データベースとテーブルを初期化"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temperature_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    light_level INTEGER,
                    device_type TEXT,
                    version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON temperature_data(timestamp)
            """)
    
    def save_temperature_data(self, data: Dict) -> bool:
        """温度データを SQLite に保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO temperature_data 
                    (timestamp, device_id, temperature, humidity, light_level, device_type, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('device_id'),
                    data.get('temperature'),
                    data.get('humidity'),
                    data.get('light_level'),
                    data.get('device_type'),
                    data.get('version')
                ))
            
            self.logger.info(f"データを保存しました: {data.get('timestamp')}")
            return True
            
        except Exception as e:
            self.logger.error(f"SQLite への保存に失敗しました: {e}")
            return False
    
    def get_recent_data(self, hours: int = 24) -> List[Dict]:
        """最近のデータを SQLite から取得"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM temperature_data 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"SQLite からのデータ取得に失敗しました: {e}")
            return []
    
    def cleanup_old_data(self, days: int) -> int:
        """古いデータを削除"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM temperature_data 
                    WHERE timestamp < ?
                """, (cutoff_time,))
                
                deleted_count = cursor.rowcount
                self.logger.info(f"{deleted_count} 件の古いデータを削除しました")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"古いデータの削除に失敗しました: {e}")
            return 0

def create_storage(storage_type: str, file_path: Path) -> DataStorage:
    """ストレージタイプに応じてインスタンスを作成"""
    if storage_type.lower() == "csv":
        return CSVStorage(file_path)
    elif storage_type.lower() == "sqlite":
        return SQLiteStorage(file_path)
    else:
        raise ValueError(f"サポートされていないストレージタイプです: {storage_type}")