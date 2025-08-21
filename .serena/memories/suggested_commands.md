# SwitchBot Temperature Logger 開発コマンド

## プロジェクト管理
```bash
# 依存関係のインストール/同期
uv sync

# 仮想環境の有効化（必要に応じて）
uv shell
```

## アプリケーション実行
```bash
# API 接続テスト
uv run main.py --test

# 1回だけデータ取得・記録
uv run main.py --once

# 定期実行モード（デフォルト10分間隔）
uv run main.py

# 古いデータのクリーンアップ
uv run main.py --cleanup
```

## 開発・メンテナンス
```bash
# 設定ファイル作成
cp .env.example .env
# その後 .env ファイルを編集してAPI認証情報を設定

# ログファイル確認
tail -f logs/temperature_logger.log

# データベース確認（SQLiteの場合）
sqlite3 data/temperature.db "SELECT * FROM temperature_data ORDER BY timestamp DESC LIMIT 10;"
```

## システムコマンド（Darwin/macOS）
```bash
# ファイル検索
find . -name "*.py" -type f

# パターン検索
grep -r "pattern" src/

# ディレクトリ一覧
ls -la

# プロセス管理（定期実行時）
ps aux | grep python
```

## 注意事項
- テスト・フォーマット・リント用の専用コマンドは現在設定されていない
- 手動でのコード品質管理が必要
- システムサービスとして実行する場合は launchd (macOS) を使用