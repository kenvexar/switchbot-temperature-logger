# Google Sheets API 設定ガイド

Google Cloud Functions から Google Sheets にデータを自動保存するための設定手順です。

## 1. Google Cloud Console での設定

### 1.1 プロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
   - プロジェクト名: `switchbot-temperature-logger`
   - 組織: 個人アカウント

### 1.2 Google Sheets API 有効化

1. 左側メニューから **API とサービス** → **ライブラリ**
2. "Google Sheets API" を検索
3. **有効にする** をクリック

### 1.3 サービスアカウント作成

1. **API とサービス** → **認証情報**
2. **認証情報を作成** → **サービス アカウント**
3. サービスアカウント情報を入力:
   ```
   名前: switchbot-sheets-writer
   説明: SwitchBot データを Google Sheets に書き込み
   ```
4. **作成して続行** をクリック
5. 役割: **編集者** を選択
6. **完了** をクリック

### 1.4 サービスアカウントキーの作成

1. 作成したサービスアカウントをクリック
2. **キー** タブ → **鍵を追加** → **新しい鍵を作成**
3. **JSON** を選択
4. **作成** → JSON ファイルがダウンロードされる

⚠️ **重要**: ダウンロードした JSON ファイルは安全に保管してください

## 2. Google Sheets の準備

### 2.1 スプレッドシート作成

1. [Google Sheets](https://sheets.google.com/) で新しいスプレッドシートを作成
2. タイトル: `SwitchBot Temperature Data`
3. スプレッドシート ID をメモ（ URL の `/d/` と `/edit` の間の文字列）

例: `https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit`
→ スプレッドシート ID: `1ABC...XYZ`

### 2.2 ヘッダー行の設定

A1 セルから以下のヘッダーを設定（日本語形式で温度と日時のみ）:

| A | B |
|---|---|
| 日時 | 温度 |

**注意**: このアプリケーションは温度と日時のみを記録します。日時は日本語フォーマット（例: 2024年01月01日 12:00:00）で保存されます。

### 2.3 共有設定

1. スプレッドシートの **共有** ボタンをクリック
2. サービスアカウントのメールアドレスを追加
   - JSON ファイル内の `client_email` の値
   - 例: `switchbot-sheets-writer@project-id.iam.gserviceaccount.com`
3. 権限: **編集者**
4. **送信** をクリック

## 3. Cloud Functions 環境変数の設定

Google Cloud Functions デプロイ時に以下の環境変数を設定します:

### 基本認証情報
```bash
export SWITCHBOT_TOKEN="your_token_here"
export SWITCHBOT_SECRET="your_secret_here"
export SWITCHBOT_DEVICE_ID="your_device_id_here"
```

### Google Sheets 関連
```bash
export GOOGLE_SHEETS_SPREADSHEET_ID="1ABC...XYZ"
```

### Google サービスアカウントキー
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type":"service_account","project_id":"your-project-id",...}'
```

**GOOGLE_SERVICE_ACCOUNT_KEY の設定方法:**
1. ダウンロードした JSON ファイルをテキストエディタで開く
2. 内容全体を1行にする（改行を削除）
3. シングルクォートで囲んで環境変数に設定

例:
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account","project_id": "your-project-id","private_key_id": "...","private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email": "switchbot-sheets-writer@project-id.iam.gserviceaccount.com","client_id": "...","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "..."}'
```

### デプロイスクリプトでの自動設定

`free-tier-deploy.sh` を使用する場合、環境変数が自動的に Cloud Functions に設定されます。

## 4. 設定確認

すべての設定が完了したら:

### ローカルでのテスト
```bash
# Google Sheets 接続テスト
uv run main.py --test-sheets
```

### Cloud Functions でのテスト
```bash
# 関数をデプロイ
./free-tier-deploy.sh

# 手動でテスト実行
curl -X POST "https://REGION-PROJECT.cloudfunctions.net/collect-temperature-data" \
  -H "Content-Type: application/json" \
  -d '{"action": "collect"}'
```

### 確認項目
1. Google Sheets にデータが追加されることを確認
2. 日時が日本語形式（2024年01月01日 12:00:00）で記録されることを確認
3. 毎時00分・30分の自動実行を確認

## トラブルシューティング

### よくあるエラー

**1. "The caller does not have permission"**
- サービスアカウントがスプレッドシートに共有されているか確認
- 権限が「編集者」になっているか確認

**2. "Unable to parse range"**
- スプレッドシート ID が正しいか確認
- シート名が正しいか確認

**3. "Invalid credentials"**
- JSON キーが正しく設定されているか確認
- JSON の改行やエスケープが崩れていないか確認

### デバッグ方法

**Cloud Functions のログ確認:**
1. [Google Cloud Console](https://console.cloud.google.com/logs/query) でログを確認
2. 関数名でフィルタリング: `resource.labels.function_name="collect-temperature-data"`

**ローカルでのデバッグ:**
```bash
# 詳細ログでローカル実行
LOG_LEVEL=DEBUG uv run main.py --test-sheets
```

**環境変数の確認:**
```bash
# Cloud Functions で環境変数を確認
gcloud functions describe collect-temperature-data --region=asia-northeast1
```