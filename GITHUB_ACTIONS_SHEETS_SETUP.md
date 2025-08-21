# GitHub Actions + Google Sheets セットアップガイド

SwitchBot Temperature Logger を GitHub Actions で実行し、データを Google Sheets に自動保存する完全ガイドです。

## 概要

- **GitHub Actions**: 30 分間隔で自動実行（完全無料）
- **Google Sheets**: データの永続化とリアルタイム確認
- **バックアップ**: CSV ファイルも GitHub Artifacts に保存

## 🚀 クイックセットアップ

### 1. Google Sheets API 設定

#### 1.1 Google Cloud Console
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクト作成: `switchbot-temperature-logger`
3. **Google Sheets API** を有効化
4. **サービスアカウント** 作成:
   ```
   名前: switchbot-sheets-writer
   役割: 編集者
   ```
5. **JSON キー** をダウンロード

#### 1.2 Google Sheets 準備
1. 新しいスプレッドシート作成: `SwitchBot Temperature Data`
2. スプレッドシート ID をコピー（ URL の `/d/` と `/edit` の間）
3. ヘッダー行を設定:
   ```
   timestamp | device_id | temperature | humidity | light_level | device_type | version | created_at
   ```
4. サービスアカウントに共有権限付与（編集者）

### 2. GitHub リポジトリ設定

#### 2.1 リポジトリ作成
```bash
git clone <repository-url>
cd switchbot-temperature-logger
git add .
git commit -m "Initial commit with Google Sheets integration"
git push origin main
```

#### 2.2 GitHub Secrets 設定
**Settings** → **Secrets and variables** → **Actions** で追加:

```
# SwitchBot API
SWITCHBOT_TOKEN=your_token_here
SWITCHBOT_SECRET=your_secret_here
SWITCHBOT_DEVICE_ID=your_device_id_here

# Google Sheets
GOOGLE_SHEETS_SPREADSHEET_ID=1ABC...XYZ
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account",...}
```

### 3. 動作確認

#### 3.1 手動テスト実行
1. **Actions** タブを開く
2. **SwitchBot Temperature Logger** を選択
3. **Run workflow** をクリック
4. 実行完了後、 Google Sheets にデータが追加されることを確認

#### 3.2 ローカルテスト（オプション）
```bash
# 依存関係インストール
uv sync

# SwitchBot API テスト
uv run main.py --test

# デバイス一覧取得
uv run main.py --devices

# Google Sheets 接続テスト
uv run main.py --test-sheets

# 1 回実行（ Google Sheets に保存）
uv run main.py --once
```

## 📊 使用方法

### 自動実行
- **頻度**: 30 分間隔
- **データ保存先**: Google Sheets + GitHub Artifacts （バックアップ）
- **停止方法**: GitHub Actions 無効化

### データ確認
1. **Google Sheets**: リアルタイムでデータ確認
2. **GitHub Actions ログ**: 実行状況確認
3. **GitHub Artifacts**: バックアップ CSV ダウンロード

### 設定変更
- **実行間隔**: `.github/workflows/temperature-logger.yml` の cron 設定
- **Google Sheets**: スプレッドシート ID を変更

## 🛠️ コマンドリファレンス

| コマンド | 説明 |
|----------|------|
| `uv run main.py --test` | SwitchBot API 接続テスト |
| `uv run main.py --devices` | デバイス一覧表示 |
| `uv run main.py --test-sheets` | Google Sheets 接続テスト |
| `uv run main.py --once` | 1 回だけ実行（ Sheets 保存） |
| `uv run main.py --cleanup` | 古いローカルデータ削除 |

## 🔧 カスタマイズ

### 実行間隔の変更
`.github/workflows/temperature-logger.yml`:
```yaml
schedule:
  - cron: '*/15 * * * *'  # 15 分間隔
  - cron: '0 * * * *'     # 1 時間間隔
  - cron: '0 */6 * * *'   # 6 時間間隔
```

### 複数デバイス対応
複数のデバイスを監視する場合は、デバイスごとにワークフローを作成するか、配列で管理。

### 通知設定
Slack や Discord への通知機能も追加可能。

## ❗ トラブルシューティング

### よくあるエラー

**1. "The caller does not have permission"**
```
解決方法:
- Google Sheets でサービスアカウントに共有権限があるか確認
- 権限が「編集者」になっているか確認
```

**2. "Invalid credentials"**
```
解決方法:
- JSON キーが正しく設定されているか確認
- 改行やエスケープ文字が崩れていないか確認
```

**3. "Device not found"**
```
解決方法:
- uv run main.py --devices でデバイス一覧確認
- SWITCHBOT_DEVICE_ID が正しいか確認
```

**4. "GitHub Actions が動作しない"**
```
解決方法:
- リポジトリがアクティブかどうか確認（ 60 日以内のコミット必要）
- Secrets が正しく設定されているか確認
```

### デバッグ手順

1. **ローカルテスト**:
   ```bash
   uv run main.py --test
   uv run main.py --test-sheets
   ```

2. **GitHub Actions ログ確認**:
   - Actions タブ → 失敗したワークフロー → 詳細ログ

3. **Google Sheets アクセス確認**:
   - サービスアカウントメールに共有通知が来ているか
   - スプレッドシート ID が正しいか

## 💰 コスト

- **GitHub Actions**: パブリックリポジトリは無料
- **Google Sheets API**: 月 100 リクエストまで無料（十分）
- **ストレージ**: Google Drive の無料容量内

**推定コスト**: 完全無料 ✅

## 🔒 セキュリティ

- API キーは GitHub Secrets で暗号化保存
- サービスアカウントは最小権限（ Sheets 編集のみ）
- リポジトリをプライベートにすることを推奨

## 📈 運用のベストプラクティス

1. **定期的な確認**:
   - 週 1 回は Google Sheets でデータを確認
   - GitHub Actions の実行状況をチェック

2. **バックアップ**:
   - GitHub Artifacts からの定期的なデータダウンロード
   - Google Sheets のエクスポート

3. **監視**:
   - 異常値やデータ欠損の早期発見
   - API レート制限の監視

設定完了後は、 30 分間隔で自動的に温度データが Google Sheets に蓄積されます！