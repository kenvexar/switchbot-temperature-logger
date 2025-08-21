# クラウドデプロイメントガイド

SwitchBot Temperature Logger を無料でクラウドデプロイする方法を紹介します。

## 1. GitHub Actions デプロイ（推奨）

### メリット
- 完全無料（制限内）
- 設定が簡単
- 自動スケジュール実行
- Git との連携

### 制限事項
- パブリックリポジトリ：無制限
- プライベートリポジトリ：月 2,000 分まで
- データ永続化には外部サービスが必要

### セットアップ手順

#### 1. GitHub Secrets の設定

1. GitHub リポジトリページに移動
2. **Settings** → **Secrets and variables** → **Actions** 
3. 以下のシークレットを追加：

```
SWITCHBOT_TOKEN=your_token_here
SWITCHBOT_SECRET=your_secret_here
SWITCHBOT_DEVICE_ID=your_device_id_here
```

#### 2. ワークフロー有効化

- `.github/workflows/temperature-logger.yml` が既に作成済み
- リポジトリをコミット・プッシュすると自動的に有効化

#### 3. 手動実行テスト

1. **Actions** タブを開く
2. **SwitchBot Temperature Logger** を選択
3. **Run workflow** をクリックして手動実行

#### 4. データの確認

- 実行後に **Artifacts** からログとデータをダウンロード可能

### データ永続化オプション

#### A. Google Sheets 連携（推奨）
```yaml
# ワークフローに追加
- name: Upload to Google Sheets
  uses: jroehl/gsheet.action@v1.0.0
  with:
    spreadsheetId: ${{ secrets.SPREADSHEET_ID }}
    commands: |
      [
        {
          "command": "appendData",
          "args": {
            "data": [["timestamp", "temperature", "humidity"]],
            "worksheetTitle": "Temperature Data"
          }
        }
      ]
  env:
    GSHEET_CLIENT_EMAIL: ${{ secrets.GSHEET_CLIENT_EMAIL }}
    GSHEET_PRIVATE_KEY: ${{ secrets.GSHEET_PRIVATE_KEY }}
```

#### B. GitHub Gist 連携
```yaml
- name: Update Gist with data  
  uses: exuanbo/actions-deploy-gist@v1
  with:
    token: ${{ secrets.GIST_TOKEN }}
    gist_id: ${{ secrets.GIST_ID }}
    file_path: data/temperature.csv
```

## 2. Railway デプロイ

### メリット
- $5/月の無料クレジット
- データベース込み
- 簡単デプロイ

### 制限事項
- 実行時間制限
- クレジット消費制

### セットアップ

1. **Railway アカウント作成**
2. **GitHub 連携**
3. **環境変数設定**
4. **PostgreSQL アドオン追加**

```python
# settings.py に追加が必要
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway の PostgreSQL
```

## 3. Oracle Cloud Always Free

### メリット
- 本格的な VPS （永続無料）
- 1GB RAM 、 2 OCPU
- データ完全永続化

### 制限事項
- 設定が複雑
- 90 日以内のアクティビティが必要

### セットアップ

1. **Oracle Cloud アカウント作成**
2. **Compute Instance 作成**
3. **SSH 接続設定**
4. **アプリケーションデプロイ**

```bash
# Oracle Cloud での実行例
git clone <repository-url>
cd switchbot-temperature-logger
python3 -m pip install uv
uv sync
cp .env.example .env
# .env を編集

# systemd サービス作成
sudo nano /etc/systemd/system/switchbot-logger.service
```

## 4. 比較表

| サービス | 料金 | 設定難易度 | データ永続化 | 推奨度 |
|----------|------|------------|--------------|--------|
| GitHub Actions | 無料 | ★☆☆ | 外部サービス必要 | ★★★ |
| Railway | $5 クレジット | ★★☆ | ○ | ★★☆ |
| Oracle Cloud | 無料 | ★★★ | ○ | ★☆☆ |
| Render | 750 時間/月 | ★★☆ | △ | ★☆☆ |

## 推奨構成

**個人利用・学習目的:**
- GitHub Actions + Google Sheets

**本格運用:**
- Oracle Cloud Always Free

**手軽に始めたい:**
- Railway （最初の月は無料）

## トラブルシューティング

### GitHub Actions でよくある問題

1. **Secrets が設定されていない**
   - Repository Settings で正しく設定されているか確認

2. **cron スケジュールが動作しない**
   - リポジトリにアクティビティが必要（ 60 日以内）

3. **依存関係エラー**
   - `uv.lock` ファイルがリポジトリに含まれているか確認

### データ取得の注意点

- SwitchBot API のレート制限に注意
- 実行間隔は最短でも 5 分以上推奨
- エラー時のリトライ機能を活用