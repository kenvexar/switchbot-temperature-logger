# SwitchBot Temperature Logger コードスタイル・規約

## 言語・文字エンコーディング
- Python 3.11+ 対応
- UTF-8 エンコーディング
- 日本語コメント・docstring使用

## 命名規則
- **クラス名**: PascalCase (SwitchBotAPI, DataStorage, TemperatureScheduler)
- **関数・メソッド名**: snake_case (get_temperature_data, create_storage)
- **変数名**: snake_case (device_id, temperature_data)
- **定数名**: UPPER_SNAKE_CASE (BASE_URL, SWITCHBOT_TOKEN)
- **プライベートメソッド**: アンダースコア接頭辞 (_generate_headers, _create_directories)

## 型ヒント
- 関数引数・戻り値に型ヒントを使用
- 例: `def get_device_status(self, device_id: str) -> Dict[str, Any]:`
- `Optional`, `List`, `Dict` などの型アノテーションを活用

## docstring規約
- 関数・クラスには日本語のdocstring
- 簡潔で分かりやすい説明
- 例: `"""温度データを取得して記録する"""`

## エラーハンドリング
- try-catch ブロックを適切に使用
- ログ出力による詳細なエラー情報記録
- 例外の適切な再発生・処理

## ログ出力
- ログレベルの適切な使い分け (INFO, ERROR, DEBUG)
- 構造化されたログメッセージ
- 日本語メッセージでユーザーフレンドリー

## モジュール構成
- 機能別にファイルを分割
- `__init__.py` でモジュール化
- 依存関係を明確化（sys.path追加パターン使用）

## 設定管理パターン
- 環境変数ベースの設定
- デフォルト値の提供
- バリデーション機能の実装