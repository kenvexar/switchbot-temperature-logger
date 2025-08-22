#!/bin/bash

# Google Cloud Functions デプロイスクリプト
# 使用前に環境変数を設定してください

set -e

# 設定値
FUNCTION_NAME="collect-temperature-data"
REGION="asia-northeast1"
RUNTIME="python311"
TIMEOUT="540s"  # 標準設定（無料枠なら120sを推奨）
MEMORY="256MB"   # 標準設定（無料枠なら128MBを推奨）

echo "Google Cloud Functions にデプロイしています..."

# 環境変数の確認
if [ -z "$SWITCHBOT_TOKEN" ]; then
    echo "エラー: SWITCHBOT_TOKEN 環境変数が設定されていません"
    exit 1
fi

if [ -z "$SWITCHBOT_SECRET" ]; then
    echo "エラー: SWITCHBOT_SECRET 環境変数が設定されていません"
    exit 1
fi

if [ -z "$SWITCHBOT_DEVICE_ID" ]; then
    echo "エラー: SWITCHBOT_DEVICE_ID 環境変数が設定されていません"
    exit 1
fi

# デプロイ実行
gcloud functions deploy $FUNCTION_NAME \
    --runtime $RUNTIME \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point collect_temperature_data \
    --source . \
    --timeout $TIMEOUT \
    --memory $MEMORY \
    --region $REGION \
    --set-env-vars "SWITCHBOT_TOKEN=$SWITCHBOT_TOKEN,SWITCHBOT_SECRET=$SWITCHBOT_SECRET,SWITCHBOT_DEVICE_ID=$SWITCHBOT_DEVICE_ID,DATABASE_TYPE=sqlite,DATABASE_PATH=/tmp/temperature.db,LOG_LEVEL=INFO,DATA_RETENTION_DAYS=60"

echo "デプロイが完了しました!"
echo "Function URL: https://$REGION-$(gcloud config get-value project).cloudfunctions.net/$FUNCTION_NAME"

# スケジューラーの作成（オプション）
read -p "Google Cloud Scheduler を作成しますか？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    FUNCTION_URL="https://$REGION-$(gcloud config get-value project).cloudfunctions.net/$FUNCTION_NAME"
    
    echo "30分ごとの温度データ収集ジョブを作成しています..."
    gcloud scheduler jobs create http switchbot-temperature-collector \
        --schedule="*/30 * * * *" \
        --time-zone="Asia/Tokyo" \
        --uri="$FUNCTION_URL" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --message-body='{"action": "collect"}' || echo "スケジューラーの作成に失敗しました（既に存在する可能性があります）"
    
    echo "毎日午前2時のクリーンアップジョブを作成しています..."
    gcloud scheduler jobs create http switchbot-cleanup \
        --schedule="0 2 * * *" \
        --time-zone="Asia/Tokyo" \
        --uri="$FUNCTION_URL" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --message-body='{"action": "cleanup"}' || echo "クリーンアップジョブの作成に失敗しました（既に存在する可能性があります）"
    
    echo "スケジューラーの設定が完了しました!"
fi