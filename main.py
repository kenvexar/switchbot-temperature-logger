#!/usr/bin/env python3
"""
SwitchBot Temperature Logger
SwitchBot ハブ 2 の気温データを自動で記録するメインスクリプト
"""

import sys
from pathlib import Path

# プロジェクトのルートパスを sys.path に追加
sys.path.append(str(Path(__file__).parent))

from src.switchbot_api import SwitchBotAPI
from src.data_storage import create_storage
from src.logger_config import setup_logging
from config.settings import settings

def log_temperature_data():
    """温度データを取得して記録する"""
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)
    
    try:
        # SwitchBot API クライアントを作成
        api = SwitchBotAPI(settings.SWITCHBOT_TOKEN, settings.SWITCHBOT_SECRET)
        
        # データストレージを作成
        if settings.DATABASE_TYPE.lower() == "csv":
            storage = create_storage("csv", settings.CSV_PATH)
        else:
            storage = create_storage("sqlite", settings.DATABASE_PATH)
        
        # 温度データを取得
        temperature_data = api.get_temperature_data(settings.SWITCHBOT_DEVICE_ID)
        
        if temperature_data:
            # データを保存
            success = storage.save_temperature_data(temperature_data)
            if success:
                logger.info(f"温度: {temperature_data['temperature']}°C, "
                          f"湿度: {temperature_data['humidity']}%, "
                          f"照度: {temperature_data['light_level']}")
                
                # Google Sheets にも保存（環境変数が設定されている場合）
                try:
                    from src.google_sheets import save_to_sheets
                    if save_to_sheets(temperature_data):
                        logger.info("Google Sheets への保存も完了しました")
                    else:
                        logger.warning("Google Sheets への保存に失敗しました")
                except ImportError:
                    logger.debug("Google Sheets 連携モジュールがインポートできませんでした")
                except Exception as e:
                    logger.warning(f"Google Sheets 連携エラー: {e}")
                    
            else:
                logger.error("データの保存に失敗しました")
        else:
            logger.error("温度データの取得に失敗しました")
            
    except Exception as e:
        logger.error(f"ログ処理中にエラーが発生しました: {e}")

def cleanup_old_data():
    """古いデータをクリーンアップする"""
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)
    
    try:
        # データストレージを作成
        if settings.DATABASE_TYPE.lower() == "csv":
            storage = create_storage("csv", settings.CSV_PATH)
        else:
            storage = create_storage("sqlite", settings.DATABASE_PATH)
        
        # 古いデータを削除
        deleted_count = storage.cleanup_old_data(settings.DATA_RETENTION_DAYS)
        logger.info(f"クリーンアップ完了: {deleted_count} 件のデータを削除しました")
        
    except Exception as e:
        logger.error(f"クリーンアップ中にエラーが発生しました: {e}")

def test_connection():
    """API 接続をテストする"""
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL, console_output=True)
    
    try:
        settings.validate()
        logger.info("設定の検証が完了しました")
        
        api = SwitchBotAPI(settings.SWITCHBOT_TOKEN, settings.SWITCHBOT_SECRET)
        
        logger.info("API 接続をテストしています...")
        if api.test_connection(settings.SWITCHBOT_DEVICE_ID):
            logger.info("✓ API 接続テストに成功しました")
            
            # テストデータを取得
            data = api.get_temperature_data(settings.SWITCHBOT_DEVICE_ID)
            if data:
                logger.info(f"取得したデータ:")
                logger.info(f"  温度: {data['temperature']}°C")
                logger.info(f"  湿度: {data['humidity']}%")
                logger.info(f"  照度: {data['light_level']}")
                logger.info(f"  デバイス: {data['device_type']} ({data['version']})")
                return True
        else:
            logger.error("✗ API 接続テストに失敗しました")
            return False
            
    except ValueError as e:
        logger.error(f"設定エラー: {e}")
        return False
    except Exception as e:
        logger.error(f"テスト中にエラーが発生しました: {e}")
        return False

def list_devices():
    """登録済みデバイス一覧を表示する"""
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL, console_output=True)
    
    try:
        settings.validate()
        logger.info("デバイス一覧を取得しています...")
        
        api = SwitchBotAPI(settings.SWITCHBOT_TOKEN, settings.SWITCHBOT_SECRET)
        device_data = api.get_device_list()
        
        if device_data:
            print("\n=== 登録済みデバイス一覧 ===")
            
            # 物理デバイス
            if device_data.get('deviceList'):
                print("\n[物理デバイス]")
                for device in device_data['deviceList']:
                    print(f"  名前: {device.get('deviceName', 'Unknown')}")
                    print(f"  ID: {device.get('deviceId', 'Unknown')}")
                    print(f"  タイプ: {device.get('deviceType', 'Unknown')}")
                    if device.get('hubDeviceId'):
                        print(f"  ハブ ID: {device.get('hubDeviceId')}")
                    print(f"  ---")
            
            # 仮想赤外線リモートデバイス
            if device_data.get('infraredRemoteList'):
                print("\n[仮想赤外線リモートデバイス]")
                for device in device_data['infraredRemoteList']:
                    print(f"  名前: {device.get('deviceName', 'Unknown')}")
                    print(f"  ID: {device.get('deviceId', 'Unknown')}")
                    print(f"  タイプ: {device.get('remoteType', 'Unknown')}")
                    if device.get('hubDeviceId'):
                        print(f"  ハブ ID: {device.get('hubDeviceId')}")
                    print(f"  ---")
            
            print("\n 温度センサーデータを取得したいデバイスの「 ID 」を .env ファイルの SWITCHBOT_DEVICE_ID に設定してください。")
            return True
        else:
            logger.error("デバイス一覧の取得に失敗しました")
            return False
            
    except ValueError as e:
        logger.error(f"設定エラー: {e}")
        logger.error("API トークンとシークレットを .env ファイルに設定してください")
        return False
    except Exception as e:
        logger.error(f"デバイス一覧取得中にエラーが発生しました: {e}")
        return False

def test_sheets_connection():
    """Google Sheets 接続をテストする"""
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL, console_output=True)
    
    try:
        from src.google_sheets import create_sheets_client_from_env
        
        logger.info("Google Sheets 接続をテストしています...")
        
        client = create_sheets_client_from_env()
        if client:
            logger.info("✓ Google Sheets 接続テストに成功しました")
            
            # テストデータを作成
            test_data = {
                'timestamp': '2024-01-01T12:00:00',
                'device_id': 'TEST_DEVICE',
                'temperature': 25.0,
                'humidity': 50.0,
                'light_level': 100,
                'device_type': 'Test',
                'version': '1.0.0'
            }
            
            # テストデータを保存
            if client.append_temperature_data(test_data):
                logger.info("✓ テストデータの書き込みに成功しました")
                row_count = client.get_row_count()
                logger.info(f"現在の行数: {row_count}")
                return True
            else:
                logger.error("✗ テストデータの書き込みに失敗しました")
                return False
        else:
            logger.error("✗ Google Sheets 接続テストに失敗しました")
            return False
            
    except ImportError:
        logger.error("✗ Google Sheets 依存関係がインストールされていません")
        logger.error("実行: uv add gspread google-auth")
        return False
    except Exception as e:
        logger.error(f"✗ Google Sheets テスト中にエラーが発生しました: {e}")
        return False

def main():
    """メインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SwitchBot Temperature Logger')
    parser.add_argument('--test', action='store_true', help='API 接続をテストする')
    parser.add_argument('--once', action='store_true', help='1 回だけ実行する')
    parser.add_argument('--cleanup', action='store_true', help='古いデータをクリーンアップする')
    parser.add_argument('--devices', action='store_true', help='登録済みデバイス一覧を表示する')
    parser.add_argument('--test-sheets', action='store_true', help='Google Sheets 接続をテストする')
    
    args = parser.parse_args()
    
    if args.test:
        success = test_connection()
        sys.exit(0 if success else 1)
    
    if args.devices:
        success = list_devices()
        sys.exit(0 if success else 1)
    
    if args.test_sheets:
        success = test_sheets_connection()
        sys.exit(0 if success else 1)
    
    if args.cleanup:
        cleanup_old_data()
        sys.exit(0)
    
    if args.once:
        log_temperature_data()
        sys.exit(0)
    
    # Google Cloud Functions でのスケジューリングを想定しているため、
    print("Google Cloud Functions でのスケジューリングを想定しているため、")
    print("プログラム自体にはスケジューリング機能がありません。")
    print("")
    print("一回だけ実行する場合: python main.py --once")
    print("テスト実行: python main.py --test")
    sys.exit(0)

# Google Cloud Functions 用のエントリーポイント
def collect_temperature_data(request):
    """
    Google Cloud Functions の HTTP トリガー用エントリーポイント
    Cloud Scheduler からの定期実行に使用される
    """
    import json
    from flask import jsonify
    
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)
    
    try:
        logger.info("Cloud Functions での温度データ収集を開始します")
        
        # リクエストパラメータを確認
        request_json = request.get_json(silent=True)
        action = None
        
        if request_json and 'action' in request_json:
            action = request_json['action']
        elif request.args.get('action'):
            action = request.args.get('action')
        
        # アクションに応じて処理を分岐
        if action == 'cleanup':
            cleanup_old_data()
            return jsonify({'status': 'success', 'message': 'データクリーンアップが完了しました'})
        elif action == 'test':
            success = test_connection()
            if success:
                return jsonify({'status': 'success', 'message': 'API 接続テストに成功しました'})
            else:
                return jsonify({'status': 'error', 'message': 'API 接続テストに失敗しました'}), 500
        else:
            # デフォルトアクション: 温度データ収集
            log_temperature_data()
            return jsonify({'status': 'success', 'message': '温度データの収集が完了しました'})
            
    except Exception as e:
        logger.error(f"Cloud Functions 実行中にエラーが発生しました: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    main()
