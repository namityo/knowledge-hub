# ナレッジベースシステム

包括的なナレッジ共有プラットフォーム - Flask + REST API + 日本時間対応

## 🚀 概要

企業や組織向けの高機能ナレッジ共有システムです。Webインターフェースと外部アプリケーション向けREST APIの両方を提供し、効率的な知識管理を実現します。

## ✨ 主要機能

### 📝 コンテンツ管理
- **記事作成・編集**: リアルタイムMarkdownプレビュー付きエディタ
- **ファイル添付**: 複数ファイルアップロード（16MB制限、拡張子フィルタ）
- **タグシステム**: 色分けタグでの分類・フィルタリング
- **下書き機能**: 公開前の編集・保存
- **検索機能**: タイトル・本文・コメント横断検索

### 👥 ユーザー機能
- **ヘッダー認証**: X-User-IDヘッダーによるユーザー識別
- **権限管理**: 作成者のみ編集・削除可能
- **いいね機能**: 記事・コメントへのリアクション
- **個人フィルタ**: 自分の投稿・いいねした投稿の表示

### 💬 コミュニケーション
- **コメントシステム**: Markdown対応コメント機能
- **いいね機能**: 記事・コメント両方に対応
- **ソーシャル機能**: ユーザー間のインタラクション

### 🔌 REST API
- **外部連携**: 認証付きREST APIで外部アプリと連携
- **日本時間対応**: JST自動変換でのデータ提供
- **フィルタリング**: 日付・作成者・タグでの絞り込み
- **ページネーション**: 効率的な大量データ取得

## 🛠️ セットアップ

### 前提条件
- Python 3.7+
- Git

### インストール手順

1. **リポジトリクローン**
```bash
git clone <repository-url>
cd knowledge_app
```

2. **仮想環境のアクティベート**
```bash
# Windows
activate.bat

# または手動で
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **アプリケーション起動**
```bash
python app.py
```

5. **アクセス**
- Web UI: http://127.0.0.1:5000
- API: http://127.0.0.1:5000/api/v1/

## 🔧 環境変数設定

### 必須設定
```bash
# API認証（本番環境では必須）
export API_KEY="your-secure-api-key"

# システム名のカスタマイズ
export SYSTEM_TITLE="Corporate Knowledge Base"
```

### ユーザー認証設定
```bash
# ユーザーIDヘッダー名（デフォルト: X-User-ID）
export USER_ID_HEADER_NAME="X-User-ID"

# ユーザーID検証パターン（正規表現）
export USER_ID_PATTERN="^[a-zA-Z0-9_-]{3,20}$"

# デフォルトユーザーID（ヘッダー未提供時）
export DEFAULT_USER_ID="anonymous"
```

### データベース設定
```bash
# データベースディレクトリ
export DATABASE_DIR="./data"
export DATABASE_FILENAME="knowledge.db"

# または完全なデータベースURL
export DATABASE_URL="sqlite:///C:/data/knowledge.db"
```

### ファイルアップロード設定
```bash
# 最大ファイルサイズ（MB）
export MAX_FILE_SIZE_MB="32"

# 許可ファイル拡張子（カンマ区切り）
export ALLOWED_FILE_EXTENSIONS="pdf,doc,docx,txt,png,jpg,jpeg"
```

### 監査ログ設定
```bash
# ログディレクトリ
export AUDIT_LOG_DIR="./logs"
export AUDIT_LOG_FILENAME="knowledge_audit.log"
```

### API設定
```bash
# APIキーヘッダー名（デフォルト: X-API-Key）
export API_KEY_HEADER_NAME="X-API-Key"
```

## 🌐 REST API仕様

### 認証
すべてのAPIエンドポイント（ヘルスチェック除く）でAPIキー認証が必要です。

```bash
# 認証ヘッダー
X-API-Key: your-api-key
```

### エンドポイント一覧

#### 📋 記事取得
```bash
# 最新記事一覧
GET /api/v1/articles/latest?limit=10&offset=0&author=user123&tag=Python&since=2025-07-13

# 特定記事詳細
GET /api/v1/articles/{id}

# 人気記事一覧（いいね数順）
GET /api/v1/articles/popular?limit=10&since=2025-07-13
```

#### 🏷️ タグ管理
```bash
# タグ一覧（使用回数順）
GET /api/v1/tags
```

#### 🔍 ヘルスチェック
```bash
# API稼働確認（認証不要）
GET /api/v1/health
```

### レスポンス例
```json
{
  "status": "success",
  "data": {
    "articles": [
      {
        "id": 17,
        "title": "Webアプリケーション開発の基礎",
        "content": "# Webアプリケーション開発の基礎...",
        "author": "user123",
        "created_at": "2025-07-13 13:09:57",
        "updated_at": "2025-07-13 13:09:57",
        "like_count": 5,
        "comment_count": 3,
        "attachment_count": 2,
        "tags": [
          {
            "id": 1,
            "name": "Python",
            "color": "#3776ab"
          }
        ],
        "is_draft": false
      }
    ],
    "pagination": {
      "total": 50,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

### 日付フィルタ対応形式
- `2025-07-13` (YYYY-MM-DD)
- `2025-07-13 10:30:00` (YYYY-MM-DD HH:MM:SS)
- `2025-07-13 10:30` (YYYY-MM-DD HH:MM)
- `2025/07/13` (YYYY/MM/DD)
- `20250713` (YYYYMMDD)

## 🏗️ アーキテクチャ

### システム構成
```
knowledge_app/
├── app.py                 # アプリケーションエントリーポイント
├── app/
│   ├── __init__.py       # アプリケーションファクトリー
│   ├── api.py            # REST APIエンドポイント
│   ├── routes.py         # Webルート
│   ├── models.py         # データベースモデル
│   ├── config.py         # 設定管理
│   └── utils.py          # ユーティリティ関数
├── templates/
│   ├── base.html         # ベーステンプレート
│   ├── index.html        # 記事一覧
│   ├── view.html         # 記事詳細
│   ├── form_editor.html  # 作成・編集フォーム
│   └── drafts.html       # 下書き一覧
├── static/
│   ├── css/              # スタイルシート（Bootstrap 5 + カスタム）
│   ├── js/               # JavaScript（Bootstrap + Highlight.js + Marked.js）
│   └── webfonts/         # Font Awesomeフォント
└── instance/
    └── knowledge.db      # SQLiteデータベース
```

### データベーススキーマ
- **Knowledge**: 記事本体（タイトル、内容、作成者、タグ）
- **Comment**: コメント機能（Markdown対応）
- **Like**: いいね機能（記事・コメント）
- **Attachment**: ファイル添付（UUID名前付け）
- **Tag**: タグシステム（色付き、使用回数追跡）

### 技術スタック
- **Backend**: Flask 2.3.3 + SQLAlchemy + pytz
- **Frontend**: Bootstrap 5.1.3 + Font Awesome 6.0.0 + Highlight.js
- **Database**: SQLite（PostgreSQL対応可能）
- **API**: REST API（JSON + Unicode対応）

## 🔐 セキュリティ機能

### 認証・認可
- **API認証**: 環境変数ベースのAPIキー認証
- **ユーザー識別**: HTTPヘッダーベースの認証
- **権限制御**: 作成者のみ編集・削除可能

### ファイルセキュリティ
- **拡張子制限**: ホワイトリスト方式
- **サイズ制限**: 設定可能な最大ファイルサイズ
- **UUID命名**: ファイル名の衝突・推測防止

### 監査機能
- **操作ログ**: 全データベース操作の記録
- **ユーザー追跡**: 操作者の完全な記録
- **無効ID検出**: 不正なユーザーIDの警告

## 🚀 本番環境デプロイ

### 基本構成（推奨）
```
Production Environment:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│  Reverse Proxy  │────│  Flask App      │
│   (CloudFlare)  │    │   (Nginx)       │    │  (Gunicorn)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │   Database      │
                                               │ (PostgreSQL)    │
                                               └─────────────────┘
```

### 1. サーバー準備（Ubuntu/CentOS）

#### システム更新
```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor

# CentOS
sudo yum update -y
sudo yum install python3 python3-pip nginx postgresql postgresql-server supervisor
```

#### 専用ユーザー作成
```bash
# アプリケーション専用ユーザー
sudo useradd -m -s /bin/bash knowledge
sudo usermod -aG sudo knowledge

# ユーザー切り替え
sudo su - knowledge
```

### 2. アプリケーション配置

#### コード配置
```bash
# アプリケーションディレクトリ作成
sudo mkdir -p /opt/knowledge
sudo chown knowledge:knowledge /opt/knowledge
cd /opt/knowledge

# リポジトリクローン
git clone <your-repository-url> .

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. データベースセットアップ（PostgreSQL）

#### PostgreSQL設定
```bash
# PostgreSQLサービス開始
sudo systemctl start postgresql
sudo systemctl enable postgresql

# データベース作成
sudo -u postgres psql
```

```sql
-- PostgreSQL内で実行
CREATE DATABASE knowledge_prod;
CREATE USER knowledge_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE knowledge_prod TO knowledge_user;
\q
```

### 4. 本番環境変数設定

#### 環境設定ファイル作成
```bash
# 環境変数ファイル
sudo nano /opt/knowledge/.env
```

```bash
# /opt/knowledge/.env
# === セキュリティ設定 ===
SECRET_KEY="$(openssl rand -base64 32)"
API_KEY="$(openssl rand -base64 32)"

# === データベース設定 ===
DATABASE_URL="postgresql://knowledge_user:secure_password_here@localhost/knowledge_prod"

# === システム設定 ===
SYSTEM_TITLE="Corporate Knowledge Base"
FLASK_ENV="production"

# === ユーザー認証 ===
USER_ID_HEADER_NAME="X-User-ID"
USER_ID_PATTERN="^[a-zA-Z0-9_-]{3,20}$"
DEFAULT_USER_ID="anonymous"

# === ファイルアップロード ===
MAX_FILE_SIZE_MB="10"
ALLOWED_FILE_EXTENSIONS="pdf,doc,docx,xls,xlsx,ppt,pptx,txt,csv,png,jpg,jpeg"

# === ログ設定 ===
AUDIT_LOG_DIR="/var/log/knowledge"
AUDIT_LOG_FILENAME="audit.log"

# === API設定 ===
API_KEY_HEADER_NAME="X-API-Key"
```

#### ログディレクトリ作成
```bash
# ログディレクトリ作成
sudo mkdir -p /var/log/knowledge
sudo chown knowledge:knowledge /var/log/knowledge
sudo chmod 755 /var/log/knowledge
```

### 5. Gunicorn設定

#### Gunicorn設定ファイル
```bash
# /opt/knowledge/gunicorn.conf.py
cat > gunicorn.conf.py << 'EOF'
# Gunicorn設定
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5

# ログ設定
accesslog = "/var/log/knowledge/gunicorn_access.log"
errorlog = "/var/log/knowledge/gunicorn_error.log"
loglevel = "info"

# プロセス設定
user = "knowledge"
group = "knowledge"
tmp_upload_dir = None
preload_app = True

# セキュリティ
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF
```

#### 起動スクリプト作成
```bash
# /opt/knowledge/start.sh
cat > start.sh << 'EOF'
#!/bin/bash
set -e

# 環境変数読み込み
source /opt/knowledge/.env
source /opt/knowledge/venv/bin/activate

# データベース初期化（初回のみ）
cd /opt/knowledge
python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

# Gunicorn起動
exec gunicorn -c gunicorn.conf.py app:app
EOF

chmod +x start.sh
```

### 6. Supervisor設定（プロセス管理）

#### Supervisor設定
```bash
# /etc/supervisor/conf.d/knowledge.conf
sudo tee /etc/supervisor/conf.d/knowledge.conf << 'EOF'
[program:knowledge]
command=/opt/knowledge/start.sh
directory=/opt/knowledge
user=knowledge
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/knowledge/supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/opt/knowledge/venv/bin"

[group:knowledge-app]
programs=knowledge
EOF
```

#### Supervisor起動
```bash
# 設定リロード
sudo supervisorctl reread
sudo supervisorctl update

# アプリケーション起動
sudo supervisorctl start knowledge

# 状態確認
sudo supervisorctl status
```

### 7. Nginx設定（リバースプロキシ）

#### Nginx設定ファイル
```bash
# /etc/nginx/sites-available/knowledge
sudo tee /etc/nginx/sites-available/knowledge << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # SSL設定（Let's Encrypt推奨）
    # listen 443 ssl http2;
    # ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # セキュリティヘッダー
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 静的ファイル配信
    location /static/ {
        alias /opt/knowledge/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # アップロードファイル配信
    location /uploads/ {
        alias /opt/knowledge/app/uploads/;
        expires 1h;
    }

    # アプリケーション
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # タイムアウト設定
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # バッファ設定
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # API専用設定（レート制限）
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ファイルアップロード制限
    client_max_body_size 50M;
    
    # ログ設定
    access_log /var/log/nginx/knowledge_access.log;
    error_log /var/log/nginx/knowledge_error.log;
}

# レート制限設定
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
}
EOF
```

#### Nginx有効化
```bash
# サイト有効化
sudo ln -s /etc/nginx/sites-available/knowledge /etc/nginx/sites-enabled/

# 設定テスト
sudo nginx -t

# Nginx再起動
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 8. SSL証明書設定（Let's Encrypt）

```bash
# Certbot インストール
sudo apt install certbot python3-certbot-nginx

# SSL証明書取得
sudo certbot --nginx -d your-domain.com

# 自動更新設定
sudo crontab -e
# 以下を追加
0 12 * * * /usr/bin/certbot renew --quiet
```

### 9. ファイアウォール設定

```bash
# UFW設定（Ubuntu）
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# または iptables（CentOS）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 10. 監視・バックアップ

#### ログローテーション設定
```bash
# /etc/logrotate.d/knowledge
sudo tee /etc/logrotate.d/knowledge << 'EOF'
/var/log/knowledge/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su knowledge knowledge
}
EOF
```

#### データベースバックアップ
```bash
# 自動バックアップスクリプト
# /opt/knowledge/backup.sh
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/knowledge/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# データベースバックアップ
pg_dump knowledge_prod > $BACKUP_DIR/db_backup_$DATE.sql

# 古いバックアップ削除（30日以上）
find $BACKUP_DIR -name "*.sql" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# cron設定（毎日2時にバックアップ）
echo "0 2 * * * /opt/knowledge/backup.sh" | sudo crontab -u knowledge -
```

### 11. ヘルスチェック

#### システム状態確認スクリプト
```bash
# /opt/knowledge/health_check.sh
cat > health_check.sh << 'EOF'
#!/bin/bash

echo "=== Knowledge Base System Health Check ==="
echo "Date: $(date)"
echo

# Supervisor状態
echo "1. Application Status:"
sudo supervisorctl status knowledge

# Nginx状態
echo -e "\n2. Nginx Status:"
sudo systemctl is-active nginx

# データベース接続
echo -e "\n3. Database Connection:"
pg_isready -h localhost -p 5432 -U knowledge_user

# API ヘルスチェック
echo -e "\n4. API Health:"
curl -s http://localhost/api/v1/health | python3 -m json.tool

# ディスク使用量
echo -e "\n5. Disk Usage:"
df -h /opt/knowledge

# メモリ使用量
echo -e "\n6. Memory Usage:"
free -h

echo -e "\n=== Health Check Complete ==="
EOF

chmod +x health_check.sh
```

### 12. 本番環境起動手順

```bash
# 1. 最終確認
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status postgresql

# 2. アプリケーション再起動
sudo supervisorctl restart knowledge

# 3. アクセステスト
curl http://your-domain.com/api/v1/health

# 4. ログ確認
tail -f /var/log/knowledge/supervisor.log
tail -f /var/log/nginx/knowledge_access.log
```

### セキュリティチェックリスト

- ✅ 強力なパスワード・APIキーの設定
- ✅ SSL/TLS証明書の設定
- ✅ ファイアウォールの設定
- ✅ 定期バックアップの設定
- ✅ ログローテーションの設定
- ✅ システム監視の設定
- ✅ 不要ポートの閉鎖
- ✅ 最新セキュリティパッチの適用

## 📊 監視・運用

### ログ監視
```bash
# 監査ログの確認
tail -f logs/audit.log

# エラーログの監視
tail -f app.log
```

### API使用状況
```bash
# ヘルスチェック
curl -X GET http://localhost:5000/api/v1/health

# 認証テスト
curl -H "X-API-Key: your-key" http://localhost:5000/api/v1/articles/latest
```

## 🔗 外部連携例

### JavaScript/Node.js
```javascript
const apiKey = 'your-api-key';
const baseUrl = 'http://localhost:5000/api/v1';

async function getLatestArticles() {
    const response = await fetch(`${baseUrl}/articles/latest`, {
        headers: { 'X-API-Key': apiKey }
    });
    return await response.json();
}
```

### Python
```python
import requests

def get_articles_since(date, api_key):
    headers = {'X-API-Key': api_key}
    params = {'since': date, 'limit': 50}
    
    response = requests.get(
        'http://localhost:5000/api/v1/articles/latest',
        headers=headers,
        params=params
    )
    return response.json()
```

## 🐛 トラブルシューティング

### よくある問題

1. **APIキーエラー**
```bash
# エラー: "APIキーが必要です"
# 解決: API_KEY環境変数を設定
export API_KEY="your-secret-key"
```

2. **日本語文字化け**
```bash
# 確認: Content-Typeヘッダー
curl -I http://localhost:5000/api/v1/articles/1
# 正常: application/json; charset=utf-8
```

3. **ファイルアップロードエラー**
```bash
# 確認: 許可拡張子とサイズ制限
echo $ALLOWED_FILE_EXTENSIONS
echo $MAX_FILE_SIZE_MB
```

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

1. フォークしてブランチ作成
2. 機能追加・バグ修正
3. テスト実行
4. プルリクエスト作成

## 📞 サポート

- Issues: GitHub Issues
- Documentation: CLAUDE.md
- API Reference: /api/v1/health

---

**🎯 企業向けナレッジ管理の完全ソリューション**

Web UI + REST API + セキュリティ + 日本語完全対応