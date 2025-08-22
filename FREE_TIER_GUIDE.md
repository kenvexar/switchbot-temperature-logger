# Google Cloud 無料枠運用ガイド

このドキュメントでは、SwitchBot Temperature Logger を Google Cloud の無料枠内で運用する方法を説明します。

## 無料枠の制限

### Google Cloud Functions
- **月間呼び出し数**: 200万回
- **コンピュート時間**: 400,000 GB秒
- **アウトバウンドデータ転送**: 5GB
- **ソースコードサイズ**: 100MB（ZIP圧縮後）

### Google Cloud Scheduler
- **無料ジョブ数**: 月間3ジョブまで

## 使用量見積もり

### 推奨設定での月間使用量

#### 温度データ収集（毎時00分・30分）
- **実行回数**: 48回/日 × 30日 = 1,440回/月
- **実行時間**: 約2秒/回
- **メモリ**: 128MB
- **コンピュート時間**: 1,440回 × 2秒 × 0.128GB = 368 GB秒

#### クリーンアップ（週1回）
- **実行回数**: 4回/月
- **実行時間**: 約3秒/回
- **メモリ**: 128MB
- **コンピュート時間**: 4回 × 3秒 × 0.128GB = 1.5 GB秒

#### 合計使用量
- **月間呼び出し数**: 1,444回（無料枠の0.072%）
- **コンピュート時間**: 369.5 GB秒（無料枠の0.092%）
- **Cloud Scheduler ジョブ**: 2個（無料枠の66%）

## 無料枠向けデプロイ方法

### 1. 無料枠向けデプロイスクリプトを使用
```bash
chmod +x free-tier-deploy.sh
./free-tier-deploy.sh
```

### 2. 手動デプロイ（無料枠設定）
```bash
gcloud functions deploy collect-temperature-data \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point collect_temperature_data \
  --source . \
  --timeout 120s \
  --memory 128MB \
  --region asia-northeast1
```

## 費用を抑えるためのベストプラクティス

### 1. メモリ使用量の最適化
- **最小メモリ（128MB）を使用**
- データ処理を効率化してメモリ使用量を削減

### 2. 実行時間の短縮
- **タイムアウト時間を120秒に設定**
- 不要な処理を削除してレスポンス時間を改善

### 3. 実行頻度の調整
- **毎時00分・30分**の正確なタイミングで実行
- **毎日 → 週1回**のクリーンアップで呼び出し数を大幅削減

### 4. データストレージの最適化
- Cloud Functions では一時ストレージ（/tmp）を使用
- 永続化が必要なデータは Google Sheets に保存
- ローカル SQLite は実行終了時に削除される

## 監視とアラート

### 使用量の確認方法
```bash
# Functions の使用状況確認
gcloud functions describe collect-temperature-data --region=asia-northeast1

# Scheduler ジョブの確認
gcloud scheduler jobs list

# 課金アカウントの使用量確認（Google Cloud Console）
# https://console.cloud.google.com/billing
```

### 無料枠超過を防ぐ設定
1. **課金アラート設定**
   - Google Cloud Console → Billing → Budgets & alerts
   - $1 USD でアラート設定

2. **API 制限設定**
   - Cloud Functions API のクォータ設定
   - 日次呼び出し数制限: 50回（安全マージン込み）

## トラブルシューティング

### よくある問題

#### 1. メモリ不足エラー
```
Error: function crashed, out of memory
```
**解決方法**: メモリを 256MB に一時的に増加

#### 2. タイムアウトエラー
```
Error: function execution timed out
```
**解決方法**: タイムアウトを 300s に増加、または処理の最適化

#### 3. 無料枠超過
```
Error: quota exceeded
```
**解決方法**: 実行頻度を減らす、または課金アカウントに切り替え

## 代替案

### 完全無料での運用
1. **GitHub Actions** を使用（月間2000分の無料枠）
2. **Heroku Scheduler** を使用（アプリ実行時間に制限あり）
3. **ローカル環境 + cron** での定期実行

### 低コスト運用への移行
1. **Google Cloud Run** を使用（より細かいリソース制御）
2. **AWS Lambda** を使用（同様の無料枠）
3. **VPS 運用** を検討（月額数百円）

## まとめ

推奨設定であれば、SwitchBot Temperature Logger は Google Cloud の無料枠内で余裕を持って運用できます。

- **呼び出し数**: 1,444回/月（無料枠200万回の0.072%）
- **コンピュート時間**: 369.5GB秒/月（無料枠40万GB秒の0.092%）
- **Cloud Scheduler**: 2ジョブ（無料枠3ジョブの66%）

毎時00分・30分の正確なデータ収集でも、無料枠の1%未満の使用量で長期間にわたって無料運用が可能です。