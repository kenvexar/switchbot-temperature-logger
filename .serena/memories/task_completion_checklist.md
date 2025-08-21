# タスク完了時のチェックリスト

## SwitchBot Temperature Logger プロジェクトでタスク完了時に実行すべき項目

### 1. コード品質確認
```bash
# Python構文チェック
python -m py_compile src/*.py config/*.py main.py

# インポートエラーチェック
python -c "import sys; sys.path.append('.'); from main import *"
```

### 2. アプリケーション動作確認
```bash
# 設定チェック
uv run main.py --test

# 1回実行テスト
uv run main.py --once
```

### 3. 環境・依存関係チェック
```bash
# 依存関係の同期確認
uv sync

# 仮想環境のチェック
uv run python --version
```

### 4. ファイル・ディレクトリ構成確認
- `data/` ディレクトリの存在確認
- `logs/` ディレクトリの存在確認
- `.env` ファイルの設定確認
- 必要なファイルの権限確認

### 5. ログ・データ確認
```bash
# ログファイルの確認
ls -la logs/
tail -5 logs/temperature_logger.log

# データファイルの確認（存在する場合）
ls -la data/
```

## 注意事項
- 現在、自動化されたテスト・リント・フォーマット機能は設定されていない
- 手動でのコード品質管理が必要
- 新しい依存関係を追加した場合は `uv add` を使用
- 本番環境デプロイ前は必ず `--test` オプションでAPI接続を確認