# SwitchBot Temperature Logger

SwitchBot ハブ 2 の気温・湿度・照度データを自動的に記録するシステム

## 特徴

- **自動記録**: 指定された間隔で温度データを自動取得・記録
- **柔軟なストレージ**: CSV ファイルまたは SQLite データベースに対応
- **スケジューリング**: 定期実行とデータクリーンアップ機能
- **設定管理**: 環境変数による柔軟な設定
- **接続テスト**: API 接続確認機能
- **ログ機能**: 詳細なログ出力とローテーション

## 必要条件

- Python 3.11+
- SwitchBot 公式 API のトークンとシークレットキー
- SwitchBot ハブ 2 デバイス

## インストール

1. リポジトリをクローン:
   ```bash
   git clone <repository-url>
   cd switchbot-temperature-logger
   ```

2. 依存関係をインストール:
   ```bash
   uv sync
   ```

## 設定

### 1. SwitchBot API 設定

1. SwitchBot アプリでデベロッパーモードを有効にする
2. API トークンとシークレットキーを取得
3. 対象デバイスの ID を確認（ハブ 2 の場合は約 10 桁の ID ）
4. API の接続を確認
5. SwitchBot ハブ 2 のデバイス ID と BLE MAC アドレスを記録

### 2. 環境変数設定

`.env.example` をコピーして `.env` ファイルを作成し、設定を行う:

```bash
cp .env.example .env
```

`.env` ファイルを編集:
```env
# SwitchBot API 設定
SWITCHBOT_TOKEN=your_token_here
SWITCHBOT_SECRET=your_secret_here
SWITCHBOT_DEVICE_ID=your_device_id_here

# データベース設定
DATABASE_TYPE=sqlite  # sqlite または csv
DATABASE_PATH=data/temperature.db
CSV_PATH=data/temperature.csv

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=logs/temperature_logger.log

# スケジュール設定
RECORD_INTERVAL_MINUTES=10
DATA_RETENTION_DAYS=30
```

## 使用方法

### API 接続テスト

設定確認と API 接続テスト:
```bash
uv run main.py --test
```

### 1 回だけ実行

データを 1 度だけ取得・記録:
```bash
uv run main.py --once
```

### 定期実行モード

定期的に実行（デフォルトは 10 分間隔）:
```bash
uv run main.py
```

デフォルトの記録間隔は 10 分で、設定により変更可能です。  
停止する場合は `Ctrl+C` で終了してください。

### 古いデータの削除

```bash
uv run main.py --cleanup
```

### 自動実行設定

システムサービスとして実行する場合は systemd （ Linux ）や launchd （ macOS ）を使用:

**macOS での launchd 設定例:**
```bash
# ~/Library/LaunchAgents/switchbot.temperature.logger.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>switchbot.temperature.logger</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/uv</string>
        <string>run</string>
        <string>/path/to/your/switchbot-temperature-logger/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/your/switchbot-temperature-logger</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

## データ構造

### SQLite データベース

テーブル名: `temperature_data`

| カラム名 | 型 | 説明 |
|----------|-----|------|
| id | INTEGER | 主キー |
| timestamp | TEXT | データ取得時刻（ ISO 形式） |
| device_id | TEXT | デバイス ID |
| temperature | REAL | 気温（℃） |
| humidity | REAL | 湿度（% ） |
| light_level | INTEGER | 照度レベル |
| device_type | TEXT | デバイス種別 |
| version | TEXT | デバイスファームウェアバージョン |
| created_at | TIMESTAMP | レコード作成時刻 |

### CSV ファイル

ヘッダー: `timestamp,device_id,temperature,humidity,light_level,device_type,version`

## ログ出力

ログは `logs/temperature_logger.log` に出力されます。  
ログファイルは 10MB で自動ローテーションし、最大 5 世代まで保持されます。

## トラブルシューティング

### API エラー

- **401 Unauthorized**: トークンまたはシークレットが正しくない
- **404 Not Found**: デバイス ID が正しくない
- **Rate Limit**: API 呼び出し制限に達した場合は時間をおいて再実行

### 接続エラー

- ネットワーク接続を確認
- SwitchBot のサーバー状況を確認
- デバイスが正常に動作しているか確認

### ログが記録されない

- 設定ファイルの確認
- ファイル/ディレクトリの書き込み権限確認
- ログファイルの容量制限確認

## ファイル構成

### プロジェクト構造

```
switchbot-temperature-logger/
├── main.py                    # メインエントリーポイント
├── src/
│   ├── switchbot_api.py      # SwitchBot API クライアント
│   ├── data_storage.py       # データストレージ管理
│   ├── scheduler.py          # スケジューラー
│   └── logger_config.py      # ログ設定
├── config/
│   └── settings.py           # 設定管理
├── data/                     # データファイル
├── logs/                     # ログファイル
├── .env.example             # 環境変数テンプレート
├── .env                     # 環境変数（実際の設定）
└── README.md                # このファイル
```

### コマンド例

```bash
# API 接続テスト
uv run main.py --test

# 単発実行テスト
uv run main.py --once
```

## ライセンス

MIT License

## 貢献

問題の報告や機能改善の提案は Issue からお知らせください。