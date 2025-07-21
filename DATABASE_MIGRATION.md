# データベースマイグレーション ガイド

## 概要
Flask-Migrateを使用してデータベースの変更を管理します。これにより、既存のデータを保持しながらスキーマの変更が可能になります。

**重要**: このアプリケーションでは **自動マイグレーション** が有効になっているため、通常は手動でのマイグレーション操作は不要です。

## 自動マイグレーション機能

### 起動時自動実行
アプリケーション起動時に以下が自動実行されます：

```bash
# 通常の起動でマイグレーションが自動実行される
python app.py              # Flask開発サーバー
uvicorn asgi:app --reload   # Uvicorn ASGIサーバー
```

### 自動実行内容
1. **環境確認**: Flask-Migrateの利用可能性をチェック
2. **初期化**: `migrations`フォルダが存在しない場合は自動作成
3. **重複クリーンアップ**: 重複したマイグレーションファイルを自動削除
4. **マイグレーション適用**: 未適用のマイグレーションを自動実行
5. **エラー処理**: 失敗時は既存データベースの使用継続

### 起動ログ例
```
🔧 データベースマイグレーション確認中...
📁 初回起動: マイグレーション環境を初期化中...
✅ マイグレーション環境初期化完了
📊 新規データベース: 初期マイグレーションを作成中...
✅ 初期データベースセットアップ完了
```

## 初回セットアップ（手動実行時）

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. マイグレーションの初期化（通常は自動実行される）
```bash
# 自動セットアップスクリプトを実行（手動の場合）
python setup_migration.py

# または手動で実行
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 日常的な使用方法

### 自動マイグレーション（推奨）

#### 1. モデルファイルを変更
`app/models.py`でテーブル構造を変更

#### 2. アプリケーションを再起動
```bash
# アプリケーション再起動でマイグレーションが自動実行される
python app.py
# または
uvicorn asgi:app --reload
```

**注意**: 自動マイグレーションは新しいマイグレーションファイルを生成せず、既存の未適用マイグレーションのみを適用します。

### 手動マイグレーション（高度な使用）

#### 1. モデルファイルを変更
`app/models.py`でテーブル構造を変更

#### 2. マイグレーションファイルを生成
```bash
flask db migrate -m "変更内容の説明"
```

#### 3. マイグレーションを適用
```bash
flask db upgrade
# または次回起動時に自動適用される
```

### 例: 新しいカラムを追加

```python
# app/models.py
class Knowledge(db.Model):
    # 既存のフィールド...
    view_count = db.Column(db.Integer, default=0)  # 新しいフィールド
```

```bash
flask db migrate -m "Add view_count to knowledge table"
flask db upgrade
```

## よく使うコマンド

### マイグレーション状態の確認
```bash
flask db current    # 現在のマイグレーション
flask db history    # マイグレーション履歴
flask db show       # 特定のマイグレーション詳細
```

### マイグレーションの操作
```bash
flask db upgrade           # 最新まで適用
flask db upgrade +2        # 2つ先まで適用
flask db downgrade         # 1つ前に戻す
flask db downgrade base    # 初期状態に戻す
```

### マイグレーション管理
```bash
flask db revision -m "説明"  # 空のマイグレーション作成
flask db stamp head         # 現在の状態を最新としてマーク
```

## トラブルシューティング

### 既存データベースからの移行

既存の`knowledge.db`がある場合：

1. **自動セットアップ（推奨）**
   ```bash
   python setup_migration.py
   ```

2. **手動セットアップ**
   ```bash
   flask db init
   flask db migrate -m "Initial migration from existing database"
   flask db stamp head  # 既存DBを最新状態としてマーク
   ```

### マイグレーションエラーの対処

#### 1. 競合の解決
```bash
flask db merge heads  # 複数のheadがある場合
```

#### 2. マイグレーションファイルの手動編集
`migrations/versions/`内のファイルを直接編集

#### 3. 強制リセット（データ損失注意）
```bash
rm -rf migrations/
flask db init
flask db migrate -m "Fresh start"
flask db upgrade
```

## ファイル構造

```
project/
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_migration.py
│       ├── 002_add_view_count.py
│       └── ...
├── instance/
│   └── knowledge.db
└── app/
    ├── models.py
    └── ...
```

## 本番環境での注意点

### デプロイ前の確認
```bash
# マイグレーションのテスト
flask db upgrade --sql  # SQLを確認（実行はしない）
flask db upgrade        # 実際に適用
```

### バックアップの推奨
```bash
# デプロイ前にDBをバックアップ
cp instance/knowledge.db instance/knowledge.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 本番環境でのマイグレーション
```bash
# 本番環境での実行例
export FLASK_ENV=production
flask db upgrade
```

## 重複マイグレーションファイルの問題と対策

### 問題
リロード時に重複したマイグレーションファイル（例：`eb5d79af6ca9_initial_database_schema.py`）が作成される場合があります。

### 自動解決
アプリケーションに重複ファイル自動削除機能が実装されているため、起動時に自動的にクリーンアップされます：

```
⚠️  重複した初期マイグレーションファイルが見つかりました: 3個
🗑️  重複ファイルを削除: eb5d79af6ca9_initial_database_schema.py
🗑️  重複ファイルを削除: f1a2b3c4d5e6_initial_database_schema.py
✅ 重複マイグレーションファイル 2個を削除しました
```

### 手動解決（必要に応じて）
```bash
# migrations/versions/ 内の重複ファイルを手動削除
rm migrations/versions/*_initial_database_schema.py
# 最新の1つだけを残す
```

## ファイル構造と説明

### migrationsフォルダ構成
```
migrations/
├── alembic.ini          # Alembic設定ファイル（必須）
├── env.py              # マイグレーション実行環境（必須）
├── script.py.mako      # マイグレーションファイルのテンプレート（必須）
└── versions/
    └── *.py            # 個別のマイグレーションファイル
```

### 各ファイルの役割
- **alembic.ini**: Alembicの設定（ログレベル、テンプレートなど）
- **env.py**: FlaskアプリとAlembicの連携、マイグレーション実行ロジック
- **script.py.mako**: 新しいマイグレーションファイル生成時のテンプレート
- **versions/*.py**: 実際のスキーマ変更を記述したマイグレーションファイル

### gitで管理すべきファイル
```gitignore
# 含める（✅）
migrations/alembic.ini
migrations/env.py
migrations/script.py.mako
migrations/versions/*.py

# 除外する（❌）
instance/
*.db
*.sqlite
```

## 関連ファイル
- `setup_migration.py` - 初回セットアップスクリプト（手動実行用）
- `app/__init__.py` - Flask-Migrate統合とアプリケーションファクトリー
- `app/database.py` - 自動マイグレーション機能の実装
- `app/models.py` - データベースモデル定義
- `requirements.txt` - Flask-Migrate依存関係