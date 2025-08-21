# システム情報・環境

## プラットフォーム
- **OS**: Darwin (macOS)
- **OS Version**: Darwin 22.6.0
- **システム**: macOS環境

## 開発環境
- **Python**: 3.11+ (pyproject.toml で指定)
- **パッケージ管理**: uv
- **Git**: リポジトリ管理有効

## ディレクトリ構造
```
switchbot-temperature-logger/
├── main.py                 # エントリーポイント
├── pyproject.toml         # プロジェクト設定
├── uv.lock               # 依存関係ロックファイル
├── .env.example          # 環境変数テンプレート
├── .gitignore            # Git除外設定
├── .mcp.json            # MCP設定
├── README.md            # プロジェクト説明
├── config/              # 設定モジュール
│   ├── __init__.py
│   └── settings.py      # 設定クラス
├── src/                 # ソースコード
│   ├── __init__.py
│   ├── switchbot_api.py  # API クライアント
│   ├── data_storage.py   # データストレージ
│   ├── scheduler.py      # スケジューラー
│   └── logger_config.py  # ログ設定
├── data/                # データ保存ディレクトリ
├── logs/                # ログ出力ディレクトリ
```

## システム固有のコマンド
- `find`: ファイル検索
- `grep`: テキスト検索
- `ls`: ディレクトリ一覧
- `tail`: ファイル末尾表示
- `sqlite3`: SQLite CLI（データベース確認用）

## 自動実行設定（macOS）
- `launchd` を使用したサービス化が可能
- `~/Library/LaunchAgents/` にplistファイル配置