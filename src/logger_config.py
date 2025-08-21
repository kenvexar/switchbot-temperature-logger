import logging
import logging.handlers
from pathlib import Path
from typing import Optional

def setup_logging(
    log_file: Optional[Path] = None,
    log_level: str = "INFO",
    console_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """ログ設定を初期化"""
    
    # ログレベルを設定
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # ルートロガーを設定
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # 既存のハンドラーをクリア
    logger.handlers.clear()
    
    # フォーマッターを作成
    formatter = logging.Formatter(
        '%(asctime) s - %(name) s - %(levelname) s - %(message) s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラーを追加
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # ファイルハンドラーを追加
    if log_file:
        # ログディレクトリを作成
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ローテーションファイルハンドラーを使用
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logging.getLogger(name)