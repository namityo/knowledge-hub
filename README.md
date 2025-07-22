# ナレッジベース

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)

企業・組織向けナレッジ共有システム。完全オフライン対応、日本語インターフェース、REST API付き。

## ✨ 特徴

- 📝 **Markdownエディタ** - リアルタイムプレビュー付き
- 🏷️ **タグシステム** - 色付きタグで分類・検索
- 💬 **コメント・いいね** - Markdown対応コメント機能
- 📊 **人気記事ランキング** - 閲覧数・いいね・コメント別
- 🔌 **REST API** - 外部連携用API（日本時間対応）
- 🚫 **完全オフライン** - CDN不使用、全アセットローカル
- 🔐 **セキュリティ** - ヘッダー認証、監査ログ

## 🚀 クイックスタート

```bash
# クローン
git clone https://github.com/your-username/knowledge-hub.git
cd knowledge-hub

# 仮想環境
python -m venv .venv
.venv\Scripts\activate

# インストール・起動
pip install -r requirements.txt
python app.py
```

→ http://127.0.0.1:5000 でアクセス

## ⚙️ 環境変数設定

| 環境変数名 | デフォルト値 | 説明 |
|------------|-------------|------|
| **セキュリティ** |
| `SECRET_KEY` | `dev-fallback-key-change-in-production` | Flaskセッション暗号化キー（**本番必須**） |
| `API_KEY` | なし | REST API認証キー（設定時のみ認証有効） |
| `API_KEY_HEADER_NAME` | `X-API-Key` | API認証ヘッダー名 |
| **システム** |
| `SYSTEM_TITLE` | `ナレッジベース` | アプリケーション表示名 |
| `POPULAR_ARTICLES_COUNT` | `5` | 人気記事ランキング表示件数 |
| **ユーザー認証** |
| `USER_ID_HEADER_NAME` | `X-User-ID` | ユーザーID取得元ヘッダー名 |
| `USER_ID_PATTERN` | `^[a-zA-Z0-9_-]{3,20}$` | ユーザーID検証正規表現 |
| `DEFAULT_USER_ID` | `anonymous` | ヘッダー未提供時のデフォルトユーザー |
| **データベース** |
| `DATABASE_URL` | なし | データベース接続URL（**最優先**） |
| `DATABASE_DIR` | なし | データベース保存ディレクトリ |
| `DATABASE_FILENAME` | `knowledge.db` | データベースファイル名 |
| **ファイルアップロード** |
| `UPLOAD_DIR` | なし | アップロードファイル保存ディレクトリ |
| `MAX_FILE_SIZE_MB` | `16` | 最大アップロードファイルサイズ（MB） |
| `ALLOWED_FILE_EXTENSIONS` | 標準セット | 許可ファイル拡張子（カンマ区切り） |
| **ログ** |
| `AUDIT_LOG_DIR` | なし | 監査ログ保存ディレクトリ |
| `AUDIT_LOG_FILENAME` | `audit.log` | 監査ログファイル名 |


## 🌐 API

### 認証
```
X-API-Key: your-api-key
```

### エンドポイント

| メソッド | エンドポイント | 認証 | 説明 |
|---------|-------------|------|------|
| `GET` | `/api/v1/articles/latest` | ✓ | 最新記事一覧取得 |
| `GET` | `/api/v1/articles/{id}` | ✓ | 特定記事詳細取得 |
| `GET` | `/api/v1/articles/popular` | ✓ | 人気記事ランキング取得 |
| `GET` | `/api/v1/tags` | ✓ | タグ一覧取得 |
| `GET` | `/api/v1/health` | ✗ | ヘルスチェック |

### パラメータ

#### `/api/v1/articles/latest`
| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| `limit` | integer | `10` | 取得件数（最大100） |
| `offset` | integer | `0` | オフセット（ページネーション用） |
| `author` | string | - | 作成者フィルタ |
| `tag` | string | - | タグフィルタ |
| `since` | string | - | 指定日付以降（YYYY-MM-DD形式） |

#### `/api/v1/articles/{id}`
| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| `include_comments` | boolean | `true` | コメント情報を含めるか |

#### `/api/v1/articles/popular`
| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| `limit` | integer | `5` | 取得件数（最大100） |
| `days` | integer | `30` | 集計期間（日数、最大365） |

### 使用例
```bash
# 最新記事を5件取得
GET /api/v1/articles/latest?limit=5

# Python関連記事を検索
GET /api/v1/articles/latest?tag=Python&limit=10

# 記事詳細をコメント付きで取得
GET /api/v1/articles/17?include_comments=true

# 直近7日の人気記事トップ3
GET /api/v1/articles/popular?days=7&limit=3
```

### レスポンス例
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "記事タイトル",
    "author": "user123",
    "created_at": "2025-07-22 12:34:56",
    "tags": [{"name": "Python", "color": "#007bff"}],
    "comments": [
      {
        "content": "コメント",
        "author": "user456",
        "like_count": 2
      }
    ]
  }
}
```

## 🏗️ 技術スタック

- **Flask** 2.3.3 + SQLAlchemy
- **Bootstrap** 5.1.3（ローカル配置）
- **SQLite**（PostgreSQL対応）
- **日本時間** (JST) 対応

## 📁 構成

```
knowledge-hub/
├── app.py              # メインアプリ
├── asgi.py             # ASGI用
├── requirements.txt    # 依存関係
├── app/
│   ├── models.py       # DB モデル
│   ├── routes.py       # Web ルート
│   ├── api.py          # REST API
│   ├── config.py       # 設定
│   └── utils.py        # ユーティリティ
├── templates/          # Jinja2 テンプレート
├── static/             # CSS/JS（ローカル）
├── instance/           # SQLite DB
└── uploads/           # アップロードファイル
```

## 🚀 本番デプロイ

```bash
# ASGI サーバー（推奨）
pip install uvicorn
uvicorn asgi:app --host 0.0.0.0 --port 5000
```

## 🛠️ 開発

```bash
# テストデータ
python create_test_data.py

# マイグレーション（オプション）
pip install flask-migrate
```

### ガイドライン
- CDN使用禁止（完全オフライン対応）
- 日本語UI
- セキュリティ優先

## 🤝 コントリビューション

1. Fork & ブランチ作成
2. 機能実装・バグ修正
3. テスト実行
4. Pull Request


## 📝 ライセンス

MIT License
