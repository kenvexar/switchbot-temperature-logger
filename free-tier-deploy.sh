#!/bin/bash

# Google Cloud Functions 無料枠向けデプロイスクリプト
# 月間200万回呼び出し、400,000 GB秒のコンピュート時間内で運用

set -e

# 設定値（無料枠最適化）
FUNCTION_NAME="collect-temperature-data"
REGION="asia-northeast1"
RUNTIME="python311"
MEMORY="256MB"  # Gen2 Functions 最小メモリ
TIMEOUT="120s"  # 短縮したタイムアウト

echo "Google Cloud Functions（無料枠）にデプロイしています..."
echo "設定:"
echo "  メモリ: $MEMORY"
echo "  タイムアウト: $TIMEOUT"
echo "  予想月間呼び出し数: 約720回（無料枠: 200万回）"

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

# 無料枠スケジューラーの作成（オプション）
read -p "Google Cloud Scheduler（無料枠: 3ジョブまで）を作成しますか？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    FUNCTION_URL="https://$REGION-$(gcloud config get-value project).cloudfunctions.net/$FUNCTION_NAME"
    
    echo "毎時00分と30分ちょうどの温度データ収集ジョブを作成しています..."
    gcloud scheduler jobs create http switchbot-temperature-collector \
        --schedule="0,30 * * * *" \
        --time-zone="Asia/Tokyo" \
        --uri="$FUNCTION_URL" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --message-body='{"action": "collect"}' || echo "スケジューラーの作成に失敗しました（既に存在する可能性があります）"
    
    echo "2週に1回（隔週日曜日午前2時）のクリーンアップジョブを作成しています..."
    gcloud scheduler jobs create http switchbot-cleanup \
        --schedule="0 2 * * 0" \
        --time-zone="Asia/Tokyo" \
        --uri="$FUNCTION_URL" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --message-body='{"action": "cleanup"}' || echo "クリーンアップジョブの作成に失敗しました（既に存在する可能性があります）"
    
    echo ""
    echo "=== 無料枠使用量見積もり ==="
    echo "Cloud Functions:"
    echo "  月間呼び出し数: 約1,442回（無料枠: 200万回）"
    echo "  コンピュート時間: 約370 GB秒（無料枠: 400,000 GB秒）"
    echo ""
    echo "Cloud Scheduler:"
    echo "  使用ジョブ数: 2個（無料枠: 3個）"
    echo ""
    echo "すべて無料枠内で運用可能です！"
fi