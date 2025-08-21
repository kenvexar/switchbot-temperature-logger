# SwitchBot Temperature Logger プロジェクト概要

## プロジェクトの目的
SwitchBot ハブ 2 から気温・湿度・照度データを自動的に取得し、定期的にログ記録するシステム。

## 技術スタック
- **言語**: Python 3.11+
- **パッケージ管理**: uv (pyproject.toml ベース)
- **主要依存関係**:
  - `python-dotenv>=1.1.1` - 環境変数管理
  - `requests>=2.32.5` - HTTP クライアント
  - `schedule>=1.2.2` - スケジューリング

## アーキテクチャ概要
- **main.py**: エントリーポイント、引数処理、メイン実行ループ
- **src/switchbot_api.py**: SwitchBot API クライアント
- **src/data_storage.py**: データストレージ（CSV、SQLite 対応）
- **src/scheduler.py**: スケジューリング管理
- **src/logger_config.py**: ログ設定
- **config/settings.py**: 設定管理（環境変数ベース）

## データストレージ
- SQLite または CSV ファイル対応
- データ保持期間の設定可能（デフォルト 30 日）
- 自動クリーンアップ機能

## 設定管理
- `.env` ファイルベースの設定
- 必要な環境変数: SWITCHBOT_TOKEN, SWITCHBOT_SECRET, SWITCHBOT_DEVICE_ID
- ログレベル、記録間隔、データ保持期間などカスタマイズ可能