#!/usr/bin/env python3
"""
Google Sheets 連携モジュール
温度データを Google Sheets に自動保存する機能
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsClient:
    """Google Sheets への書き込みクライアント"""
    
    def __init__(self, service_account_info: Dict, spreadsheet_id: str):
        """
        Google Sheets クライアントを初期化
        
        Args:
            service_account_info: サービスアカウント情報（ JSON ）
            spreadsheet_id: 対象スプレッドシートの ID
        """
        self.spreadsheet_id = spreadsheet_id
        self.logger = logging.getLogger(__name__)
        
        try:
            # Google Sheets API のスコープ
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            self.logger.debug(f"サービスアカウント情報のキー: {list(service_account_info.keys())}")
            
            # サービスアカウントの詳細情報をログ出力
            client_email = service_account_info.get('client_email', 'N/A')
            project_id = service_account_info.get('project_id', 'N/A')
            self.logger.info(f"使用するサービスアカウント: {client_email}")
            self.logger.info(f"プロジェクト ID: {project_id}")
            
            # 認証情報の設定
            credentials = Credentials.from_service_account_info(
                service_account_info, scopes=scopes
            )
            
            # gspread クライアントの作成
            self.gc = gspread.authorize(credentials)
            self.worksheet = None
            
            self.logger.debug("gspread クライアントの作成に成功しました")
            
        except Exception as e:
            self.logger.error(f"GoogleSheetsClient 初期化エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            raise
        
    def find_available_worksheet(self) -> Optional[str]:
        """
        利用可能なワークシートを検索
        
        Returns:
            str or None: 利用可能なワークシート名
        """
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            worksheets = spreadsheet.worksheets()
            
            self.logger.info(f"スプレッドシートに {len(worksheets)} 個のワークシートが見つかりました")
            
            for worksheet in worksheets:
                self.logger.info(f"利用可能なワークシート: '{worksheet.title}'")
            
            if worksheets:
                # 最初のワークシートを使用
                first_worksheet = worksheets[0]
                self.logger.info(f"最初のワークシート '{first_worksheet.title}' を使用します")
                return first_worksheet.title
            else:
                self.logger.error("利用可能なワークシートが見つかりません")
                return None
                
        except Exception as e:
            self.logger.error(f"ワークシート検索エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            return None
        
    def connect_worksheet(self, worksheet_name: Optional[str] = None) -> bool:
        """
        ワークシートに接続
        
        Args:
            worksheet_name: ワークシート名（None の場合は自動検出）
            
        Returns:
            bool: 接続成功かどうか
        """
        try:
            self.logger.debug(f"スプレッドシート ID '{self.spreadsheet_id}' に接続を試行しています")
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # ワークシート名が指定されていない場合は自動検出
            if worksheet_name is None:
                worksheet_name = self.find_available_worksheet()
                if worksheet_name is None:
                    return False
            
            self.logger.debug(f"ワークシート '{worksheet_name}' への接続を試行しています")
            self.worksheet = spreadsheet.worksheet(worksheet_name)
            
            self.logger.info(f"ワークシート '{worksheet_name}' に接続しました")
            return True
            
        except gspread.WorksheetNotFound as e:
            self.logger.error(f"ワークシート '{worksheet_name}' が見つかりません: {e}")
            
            # 利用可能なワークシート一覧を表示
            try:
                available_worksheet = self.find_available_worksheet()
                if available_worksheet:
                    self.logger.info(f"代わりに '{available_worksheet}' への接続を試行します")
                    return self.connect_worksheet(available_worksheet)
            except:
                pass
                
            return False
        except gspread.SpreadsheetNotFound as e:
            self.logger.error(f"スプレッドシート '{self.spreadsheet_id}' が見つかりません: {e}")
            return False
        except gspread.exceptions.APIError as e:
            self.logger.error(f"Google Sheets API エラー: {e}")
            self.logger.error(f"HTTP ステータス: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            if hasattr(e, 'response') and hasattr(e.response, 'content'):
                self.logger.error(f"レスポンス内容: {e.response.content}")
            return False
        except Exception as e:
            self.logger.error(f"ワークシート接続エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            
            # HTTPリクエストエラーの詳細を取得
            if hasattr(e, 'response'):
                self.logger.error(f"HTTP ステータス: {e.response.status_code}")
                self.logger.error(f"HTTP レスポンス: {e.response.text}")
            
            import traceback
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            return False
    
    def setup_headers(self) -> bool:
        """
        ヘッダー行を設定（初回のみ実行）
        
        Returns:
            bool: 設定成功かどうか
        """
        if not self.worksheet:
            self.logger.error("ワークシートに接続していません")
            return False
            
        headers = [
            '日時',
            '温度(°C)'
        ]
        
        try:
            # 1 行目が空の場合のみヘッダーを設定
            first_row = self.worksheet.row_values(1)
            if not first_row or first_row[0] == '':
                self.worksheet.insert_row(headers, 1)
                self.logger.info("ヘッダー行を設定しました")
            else:
                self.logger.info("ヘッダー行は既に存在します")
            
            return True
            
        except Exception as e:
            self.logger.error(f"ヘッダー設定エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            return False
    
    def append_temperature_data(self, temperature_data: Dict) -> bool:
        """
        温度データを追加（日本語時間と温度のみ）
        
        Args:
            temperature_data: 温度データ辞書
            
        Returns:
            bool: 追加成功かどうか
        """
        if not self.worksheet:
            self.logger.error("ワークシートに接続していません")
            return False
            
        try:
            # 日本時間を取得
            from zoneinfo import ZoneInfo
            japan_tz = ZoneInfo("Asia/Tokyo")
            japan_time = datetime.now(japan_tz)
            
            # 日時フォーマット（例: 2025/08/22 07:30）
            formatted_time = japan_time.strftime("%Y/%m/%d %H:%M")
            
            # データ行を準備（日本語時間と温度のみ）
            row_data = [
                formatted_time,
                temperature_data.get('temperature', 0)
            ]
            
            # データを追加
            self.worksheet.append_row(row_data)
            self.logger.info(f"データを追加しました: 時刻={formatted_time}, "
                           f"温度={temperature_data.get('temperature')}°C")
            
            return True
            
        except Exception as e:
            self.logger.error(f"データ追加エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            return False
    
    def get_row_count(self) -> int:
        """
        データ行数を取得
        
        Returns:
            int: 行数（ヘッダー含む）
        """
        if not self.worksheet:
            return 0
            
        try:
            return len(self.worksheet.get_all_values())
        except Exception as e:
            self.logger.error(f"行数取得エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            return 0


def create_sheets_client_from_env() -> Optional[GoogleSheetsClient]:
    """
    環境変数から Google Sheets クライアントを作成
    
    Returns:
        GoogleSheetsClient or None: 作成に失敗した場合は None
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 環境変数の取得
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
        
        logger.debug(f"GOOGLE_SHEETS_SPREADSHEET_ID の長さ: {len(spreadsheet_id) if spreadsheet_id else 0}")
        logger.debug(f"GOOGLE_SERVICE_ACCOUNT_KEY の長さ: {len(service_account_key) if service_account_key else 0}")
        
        if not spreadsheet_id:
            logger.error("GOOGLE_SHEETS_SPREADSHEET_ID 環境変数が設定されていません")
            return None
            
        if not service_account_key:
            logger.error("GOOGLE_SERVICE_ACCOUNT_KEY 環境変数が設定されていません")
            return None
        
        # スプレッドシート ID の妥当性チェック
        logger.info(f"対象スプレッドシート ID: {spreadsheet_id}")
        logger.info(f"スプレッドシート URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        
        # JSON 文字列をパース
        logger.debug("サービスアカウントキーの JSON 解析を開始します")
        service_account_info = json.loads(service_account_key)
        logger.debug("サービスアカウントキーの JSON 解析が完了しました")
        
        # クライアントを作成
        logger.debug("Google Sheets クライアントの作成を開始します")
        client = GoogleSheetsClient(service_account_info, spreadsheet_id)
        
        # ワークシートに接続（自動検出）
        logger.debug("ワークシートへの接続を開始します（自動検出）")
        if not client.connect_worksheet():
            logger.error("ワークシートへの接続に失敗しました")
            return None
        
        # ヘッダーを設定
        logger.debug("ヘッダーの設定を開始します")
        client.setup_headers()
        
        logger.info("Google Sheets クライアントを作成しました")
        return client
        
    except json.JSONDecodeError as e:
        logger.error(f"サービスアカウントキーの JSON 解析エラー: {e}")
        logger.error(f"JSON データの先頭100文字: {service_account_key[:100] if service_account_key else 'None'}")
        return None
    except Exception as e:
        logger.error(f"Google Sheets クライアント作成エラー: {e}")
        logger.error(f"エラータイプ: {type(e).__name__}")
        import traceback
        logger.error(f"スタックトレース: {traceback.format_exc()}")
        return None


def save_to_sheets(temperature_data: Dict) -> bool:
    """
    温度データを Google Sheets に保存
    
    Args:
        temperature_data: 温度データ辞書
        
    Returns:
        bool: 保存成功かどうか
    """
    logger = logging.getLogger(__name__)
    
    try:
        # クライアントを作成
        logger.debug("Google Sheets クライアントの作成を開始します")
        client = create_sheets_client_from_env()
        if not client:
            logger.error("Google Sheets クライアントの作成に失敗しました")
            return False
        
        # データを保存
        logger.debug("温度データの保存を開始します")
        success = client.append_temperature_data(temperature_data)
        
        if success:
            row_count = client.get_row_count()
            logger.info(f"Google Sheets への保存完了（総行数: {row_count}）")
        
        return success
        
    except Exception as e:
        logger.error(f"Google Sheets 保存エラー: {e}")
        logger.error(f"エラータイプ: {type(e).__name__}")
        import traceback
        logger.error(f"スタックトレース: {traceback.format_exc()}")
        return False