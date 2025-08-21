import os
import time
import uuid
import hashlib
import hmac
import base64
import requests
import logging
from typing import Dict, Optional
from datetime import datetime

class SwitchBotAPI:
    """SwitchBot API v1.1 クライアント"""
    
    BASE_URL = "https://api.switch-bot.com/v1.1"
    
    def __init__(self, token: str, secret: str):
        self.token = token
        self.secret = secret
        self.logger = logging.getLogger(__name__)
    
    def _generate_headers(self) -> Dict[str, str]:
        """API 認証用のヘッダーを生成"""
        nonce = str(uuid.uuid4())
        t = int(round(time.time() * 1000))
        string_to_sign = f"{self.token}{t}{nonce}"
        
        sign = base64.b64encode(
            hmac.new(
                bytes(self.secret, "utf-8"),
                msg=bytes(string_to_sign, "utf-8"),
                digestmod=hashlib.sha256
            ).digest()
        )
        
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "charset": "utf8",
            "t": str(t),
            "sign": str(sign, "utf-8"),
            "nonce": nonce
        }
    
    def get_device_status(self, device_id: str, max_retries: int = 3) -> Optional[Dict]:
        """デバイスのステータスを取得"""
        url = f"{self.BASE_URL}/devices/{device_id}/status"
        
        for attempt in range(max_retries):
            try:
                headers = self._generate_headers()
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("statusCode") == 100:
                    self.logger.info(f"デバイス {device_id} のステータスを正常に取得しました")
                    return data.get("body")
                else:
                    self.logger.error(f"API エラー: {data.get('message', 'Unknown error')}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"API リクエストエラー (試行 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数バックオフ
        
        return None
    
    def get_temperature_data(self, device_id: str) -> Optional[Dict]:
        """温度データを取得して整形"""
        status = self.get_device_status(device_id)
        
        if not status:
            return None
        
        return {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "temperature": status.get("temperature"),
            "humidity": status.get("humidity"),
            "light_level": status.get("lightLevel"),
            "device_type": status.get("deviceType", "Unknown"),
            "version": status.get("version", "Unknown")
        }
    
    def test_connection(self, device_id: str) -> bool:
        """API 接続をテスト"""
        try:
            result = self.get_temperature_data(device_id)
            return result is not None
        except Exception as e:
            self.logger.error(f"接続テストに失敗しました: {e}")
            return False

    def get_device_list(self) -> Optional[Dict]:
        """登録済みデバイス一覧を取得"""
        url = f"{self.BASE_URL}/devices"
        
        try:
            headers = self._generate_headers()
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("statusCode") == 100:
                self.logger.info("デバイス一覧を正常に取得しました")
                return data.get("body")
            else:
                self.logger.error(f"API エラー: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API リクエストエラー: {e}")
            raise
        
        return None
