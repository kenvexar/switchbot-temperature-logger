import time
import logging
import schedule
from datetime import datetime
from typing import Callable, Optional
import signal
import sys

class TemperatureScheduler:
    """温度データの定期取得スケジューラー"""
    
    def __init__(self, interval_minutes: int = None):
        self.interval_minutes = interval_minutes  # 後方互換性のため保持
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """シグナルハンドラーを設定"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """シグナル受信時の処理"""
        self.logger.info(f"シグナル {signum} を受信しました。終了処理を開始します...")
        self.stop()
        sys.exit(0)
    
    def add_job(self, job_func: Callable, *args, **kwargs):
        """スケジュールにジョブを追加（00分と30分ちょうどに実行）"""
        # 毎時00分と30分に実行
        schedule.every().hour.at(":00").do(job_func, *args, **kwargs)
        schedule.every().hour.at(":30").do(job_func, *args, **kwargs)
        self.logger.info("ジョブを追加しました: 毎時00分と30分に実行")
    
    def add_cleanup_job(self, cleanup_func: Callable, hour: str = "02:00", *args, **kwargs):
        """日次クリーンアップジョブを追加"""
        schedule.every().day.at(hour).do(cleanup_func, *args, **kwargs)
        self.logger.info(f"日次クリーンアップジョブを追加しました: {hour}")
    
    def run_once(self, job_func: Callable, *args, **kwargs) -> bool:
        """ジョブを 1 回だけ実行"""
        try:
            self.logger.info("ジョブを 1 回実行します...")
            job_func(*args, **kwargs)
            return True
        except Exception as e:
            self.logger.error(f"ジョブの実行に失敗しました: {e}")
            return False
    
    def start(self, run_immediately: bool = True):
        """スケジューラーを開始"""
        self.is_running = True
        self.logger.info("スケジューラーを開始しました")
        
        if run_immediately:
            self.logger.info("初回実行を開始します...")
            for job in schedule.jobs:
                try:
                    # クリーンアップジョブは初回実行しない
                    if hasattr(job.job_func, '__name__') and 'cleanup' not in job.job_func.__name__.lower():
                        job.run()
                except Exception as e:
                    self.logger.error(f"初回実行でエラーが発生しました: {e}")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt を受信しました")
            self.stop()
        except Exception as e:
            self.logger.error(f"スケジューラー実行中にエラーが発生しました: {e}")
            self.stop()
    
    def stop(self):
        """スケジューラーを停止"""
        self.is_running = False
        self.logger.info("スケジューラーを停止しました")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """次回実行時刻を取得"""
        if not schedule.jobs:
            return None
        
        next_run = min(job.next_run for job in schedule.jobs)
        return next_run
    
    def list_jobs(self) -> list:
        """登録されているジョブのリストを取得"""
        jobs_info = []
        for job in schedule.jobs:
            jobs_info.append({
                'interval': job.interval,
                'unit': job.unit,
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'job_func': job.job_func.__name__ if hasattr(job.job_func, '__name__') else str(job.job_func)
            })
        return jobs_info