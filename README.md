# SwitchBot Temperature Logger

SwitchBot ハブ 2 の気温・湿度・照度データを Google Cloud Functions で自動記録するシステム

## 特徴

- **サーバーレス実行**: Google Cloud Functions で完全自動化
- **定期実行**: Cloud Scheduler で毎時00分・30分に自動実行
- **無料運用**: Google Cloud 無料枠内で月間1,400回以上実行可能
- **柔軟なストレージ**: Google Sheets または SQLite データベースに対応
- **自動クリーンアップ**: 週1回の古いデータ削除
- **設定管理**: 環境変数による柔軟な設定
- **接続テスト**: API 接続確認機能

## 必要条件

- Google Cloud Platform アカウント
- SwitchBot 公式 API のトークンとシークレットキー  
- SwitchBot ハブ 2 デバイス
- Python 3.11+（ローカル開発時のみ）

## クイックスタート

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd switchbot-temperature-logger
```

### 2. Google Cloud Functions へのデプロイ（推奨）

**無料枠での運用:**
```bash
# 環境変数を設定
export SWITCHBOT_TOKEN="your_token_here"
export SWITCHBOT_SECRET="your_secret_here"  
export SWITCHBOT_DEVICE_ID="your_device_id_here"

# 無料枠向けデプロイ
chmod +x free-tier-deploy.sh
./free-tier-deploy.sh
```

**標準デプロイ:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. ローカル開発・テスト

```bash
# 依存関係をインストール
uv sync

# API 接続テスト
uv run main.py --test
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

### Cloud Functions での自動実行

デプロイ後は Google Cloud Scheduler により自動実行されます：

- **温度データ収集**: 毎時00分・30分（月間1,440回）
- **データクリーンアップ**: 毎週月曜日午前2時（月間4回）

### 手動実行・テスト

**ローカルでのテスト:**
```bash
# API 接続テスト
uv run main.py --test

# デバイス一覧表示
uv run main.py --list-devices

# 1回だけ実行
uv run main.py --once

# Google Sheets 接続テスト
uv run main.py --test-sheets

# 古いデータの削除
uv run main.py --cleanup
```

**Cloud Functions での手動実行:**
```bash
# 温度データ収集
curl -X POST "https://REGION-PROJECT.cloudfunctions.net/collect-temperature-data" \
  -H "Content-Type: application/json" \
  -d '{"action": "collect"}'

# 接続テスト  
curl -X POST "https://REGION-PROJECT.cloudfunctions.net/collect-temperature-data" \
  -H "Content-Type: application/json" \
  -d '{"action": "test"}'

# クリーンアップ
curl -X POST "https://REGION-PROJECT.cloudfunctions.net/collect-temperature-data" \
  -H "Content-Type: application/json" \
  -d '{"action": "cleanup"}'
```

## データ構造とストレージ

### Google Sheets（推奨）

Google Sheets に温度と時刻のみを記録（日本語フォーマット）：

| 列 | 説明 | 例 |
|---|------|-----|  
| A | 日時 | 2024年01月01日 12:00:00 |
| B | 温度 | 22.5 |

### SQLite データベース（ローカル/一時）

テーブル名: `temperature_data`

| カラム名 | 型 | 説明 |
|----------|-----|------|
| id | INTEGER | 主キー |
| timestamp | TEXT | データ取得時刻（ISO形式） |
| device_id | TEXT | デバイス ID |
| temperature | REAL | 気温（℃） |
| humidity | REAL | 湿度（%） |
| light_level | INTEGER | 照度レベル |
| device_type | TEXT | デバイス種別 |
| version | TEXT | ファームウェアバージョン |
| created_at | TIMESTAMP | レコード作成時刻 |

**注意**: Cloud Functions では /tmp に保存され、実行終了時に削除されます。

## ログ出力

### Cloud Functions
Google Cloud Console の Logs Explorer で確認：
```
https://console.cloud.google.com/logs/query
```

### ローカル開発
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

## 費用とリソース

### 無料枠での運用

Google Cloud 無料枠内での月間使用量：

- **Cloud Functions**: 1,444回実行（無料枠200万回の0.072%）
- **Cloud Scheduler**: 2ジョブ（無料枠3ジョブの66%）
- **コンピュート時間**: 約370GB秒（無料枠40万GB秒の0.09%）

詳細は `FREE_TIER_GUIDE.md` を参照してください。

## ファイル構成

### プロジェクト構造

```
switchbot-temperature-logger/
├── main.py                      # メインエントリーポイント + Cloud Functions
├── src/
│   ├── switchbot_api.py        # SwitchBot API クライアント
│   ├── data_storage.py         # データストレージ管理
│   ├── google_sheets.py        # Google Sheets 連携
│   └── logger_config.py        # ログ設定
├── config/
│   └── settings.py             # 設定管理
├── requirements.txt            # Cloud Functions 依存関係
├── pyproject.toml              # ローカル開発依存関係
├── deploy.sh                   # 標準デプロイスクリプト
├── free-tier-deploy.sh         # 無料枠向けデプロイスクリプト
├── free-tier-30min-scheduler.yaml # スケジューラー設定
├── FREE_TIER_GUIDE.md          # 無料枠運用ガイド
├── .env.example               # 環境変数テンプレート
└── README.md                  # このファイル
```

## 関連ドキュメント

- **[FREE_TIER_GUIDE.md](FREE_TIER_GUIDE.md)**: 無料枠での運用方法
- **[GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md)**: Google Sheets 連携設定
- **[CLAUDE.md](CLAUDE.md)**: 開発者向け詳細情報

## ライセンス

MIT License

## 貢献

問題の報告や機能改善の提案は Issue からお知らせください。