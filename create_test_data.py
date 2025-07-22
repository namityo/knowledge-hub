#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
包括的テストデータ作成スクリプト

最新の機能に対応したテストデータを生成：
- 20件の記事
- タグシステム
- いいね機能
- コメント機能
- 添付ファイル
- 下書き機能
- 複数ユーザー
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import random

# アプリケーションのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Knowledge, Comment, Like, CommentLike, Attachment, Tag, ViewHistory

def create_test_data():
    """包括的なテストデータを作成"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 テストデータ作成を開始します...")
        
        # 既存データクリア
        print("📝 既存データをクリア中...")
        db.drop_all()
        db.create_all()
        
        # 1. タグデータの作成
        print("🏷️  タグデータを作成中...")
        tags_data = [
            {"name": "Python", "color": "#3776ab"},
            {"name": "JavaScript", "color": "#f7df1e"},
            {"name": "Flask", "color": "#000000"},
            {"name": "React", "color": "#61dafb"},
            {"name": "データベース", "color": "#ff6b35"},
            {"name": "API", "color": "#ff9500"},
            {"name": "セキュリティ", "color": "#dc3545"},
            {"name": "パフォーマンス", "color": "#28a745"},
            {"name": "デザイン", "color": "#6f42c1"},
            {"name": "テスト", "color": "#17a2b8"},
            {"name": "ドキュメント", "color": "#6c757d"},
            {"name": "ベストプラクティス", "color": "#fd7e14"},
            {"name": "トラブルシューティング", "color": "#e83e8c"},
            {"name": "チュートリアル", "color": "#20c997"},
            {"name": "Tips", "color": "#ffc107"},
            {"name": "初心者", "color": "#007bff"},
            {"name": "プロダクション", "color": "#dc3545"},
            {"name": "開発環境", "color": "#28a745"},
            {"name": "CI/CD", "color": "#6f42c1"},
            {"name": "Docker", "color": "#0db7ed"}
        ]
        
        tags = {}
        for tag_data in tags_data:
            tag = Tag(
                name=tag_data["name"],
                color=tag_data["color"],
                usage_count=0,
                created_by="admin"
            )
            db.session.add(tag)
            tags[tag_data["name"]] = tag
        
        db.session.commit()
        print(f"   ✅ {len(tags_data)}個のタグを作成しました")
        
        # 2. ユーザーリスト
        users = ["admin", "developer", "designer", "tester", "manager", "intern"]
        
        # 3. 記事データの作成
        print("📚 記事データを作成中...")
        
        articles_data = [
            {
                "title": "Pythonプログラミング完全ガイド",
                "content": """# Pythonプログラミング完全ガイド

## 概要
Pythonは読みやすく、書きやすいプログラミング言語です。データサイエンス、Web開発、自動化など様々な分野で活用されています。

## 基本構文

### 変数と型
```python
# 基本的な変数定義
name = "Python"
version = 3.9
is_popular = True

# リストと辞書
languages = ["Python", "JavaScript", "Java"]
info = {"name": "Python", "year": 1991}
```

### 制御構文
```python
# 条件分岐
if version >= 3:
    print("Python 3系です")
elif version >= 2:
    print("Python 2系です")
else:
    print("古いバージョンです")

# ループ処理
for lang in languages:
    print(f"言語: {lang}")

for i in range(5):
    print(f"数値: {i}")
```

## 関数とクラス

### 関数定義
```python
def greet(name, language="Python"):
    return f"Hello {name}, welcome to {language}!"

def calculate_area(width, height):
    \"\"\"面積を計算する関数\"\"\"
    return width * height

# 関数の使用
message = greet("Developer")
area = calculate_area(10, 20)
```

### クラス定義
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"私は{self.name}、{self.age}歳です"
    
    def is_adult(self):
        return self.age >= 18

# クラスの使用
person = Person("田中", 25)
print(person.introduce())
```

## ライブラリとパッケージ

### 標準ライブラリ
```python
import datetime
import json
import os

# 現在時刻
now = datetime.datetime.now()
print(f"現在時刻: {now}")

# JSON処理
data = {"name": "Python", "version": 3.9}
json_str = json.dumps(data, ensure_ascii=False)
```

### 外部ライブラリ
```python
# requests (HTTP通信)
import requests

response = requests.get("https://api.example.com/data")
data = response.json()

# pandas (データ分析)
import pandas as pd

df = pd.read_csv("data.csv")
df.head()
```

Pythonの豊富な機能を活用して、効率的なプログラミングを楽しみましょう！""",
                "author": "admin",
                "tags": ["Python", "チュートリアル", "初心者"],
                "is_draft": False
            },
            {
                "title": "モダンJavaScript開発のベストプラクティス",
                "content": """# モダンJavaScript開発のベストプラクティス

## ES6+の活用

### アロー関数
```javascript
// 従来の関数
function add(a, b) {
    return a + b;
}

// アロー関数
const add = (a, b) => a + b;

// 配列操作
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const sum = numbers.reduce((acc, n) => acc + n, 0);
```

### 分割代入
```javascript
// オブジェクトの分割代入
const user = { name: "田中", age: 30, email: "tanaka@example.com" };
const { name, age } = user;

// 配列の分割代入
const colors = ["red", "green", "blue"];
const [primary, secondary] = colors;
```

### テンプレートリテラル
```javascript
const name = "世界";
const greeting = `こんにちは、${name}！
今日は${new Date().toLocaleDateString()}です。`;
```

## 非同期処理

### Promise
```javascript
function fetchData(url) {
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log("データ取得成功:", data);
            return data;
        })
        .catch(error => {
            console.error("エラー:", error);
            throw error;
        });
}
```

### async/await
```javascript
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const user = await response.json();
        
        const posts = await fetch(`/api/users/${userId}/posts`);
        const userPosts = await posts.json();
        
        return { user, posts: userPosts };
    } catch (error) {
        console.error("ユーザーデータ取得エラー:", error);
        throw error;
    }
}
```

## モジュール化

### ESModules
```javascript
// utils.js
export const formatDate = (date) => {
    return date.toLocaleDateString('ja-JP');
};

export const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

// main.js
import { formatDate, validateEmail } from './utils.js';

const today = formatDate(new Date());
const isValid = validateEmail("test@example.com");
```

## エラーハンドリング

### try-catch-finally
```javascript
async function processData(data) {
    try {
        const processed = await processComplexData(data);
        return processed;
    } catch (error) {
        console.error("処理エラー:", error.message);
        
        // エラー種別による処理分岐
        if (error instanceof ValidationError) {
            throw new Error("データが無効です");
        } else if (error instanceof NetworkError) {
            throw new Error("ネットワークエラーが発生しました");
        } else {
            throw new Error("予期しないエラーが発生しました");
        }
    } finally {
        console.log("処理が完了しました");
    }
}
```

モダンJavaScriptの機能を活用して、保守性の高いコードを書きましょう！""",
                "author": "developer",
                "tags": ["JavaScript", "ベストプラクティス", "開発環境"],
                "is_draft": False
            },
            {
                "title": "Flask REST API開発の実践ガイド",
                "content": """# Flask REST API開発の実践ガイド

## プロジェクト構成

```
flask_api/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── auth.py
│   └── utils.py
├── tests/
├── requirements.txt
└── app.py
```

## 基本的なAPI設計

### アプリケーション初期化
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
    
    db.init_app(app)
    CORS(app)
    
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    return app
```

### モデル定義
```python
from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='posts')
```

### APIエンドポイント
```python
from flask import Blueprint, request, jsonify
from app.models import User, Post, db

api_bp = Blueprint('api', __name__)

@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'created_at': post.created_at.isoformat()
    } for post in posts])
```

## 認証とセキュリティ

### JWT認証
```python
import jwt
from functools import wraps
from flask import current_app, request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]  # "Bearer <token>"
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

@api_bp.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user_id):
    return jsonify({'message': f'Hello user {current_user_id}'})
```

## エラーハンドリング

### カスタムエラーハンドラー
```python
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
```

Flaskを使った堅牢なAPIを構築しましょう！""",
                "author": "developer",
                "tags": ["Flask", "API", "Python", "ベストプラクティス"],
                "is_draft": False
            },
            {
                "title": "Reactコンポーネント設計パターン",
                "content": """# Reactコンポーネント設計パターン

## 関数コンポーネントとHooks

### useState
```jsx
import React, { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>カウント: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                増加
            </button>
            <button onClick={() => setCount(count - 1)}>
                減少
            </button>
        </div>
    );
}
```

### useEffect
```jsx
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchUser = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/api/users/${userId}`);
                const userData = await response.json();
                setUser(userData);
            } catch (error) {
                console.error('ユーザー取得エラー:', error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchUser();
    }, [userId]);
    
    if (loading) return <div>読み込み中...</div>;
    if (!user) return <div>ユーザーが見つかりません</div>;
    
    return (
        <div>
            <h2>{user.name}</h2>
            <p>{user.email}</p>
        </div>
    );
}
```

## カスタムHooks

### API取得Hook
```jsx
import { useState, useEffect } from 'react';

function useApi(url) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('データ取得に失敗しました');
                }
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, [url]);
    
    return { data, loading, error };
}

// 使用例
function PostList() {
    const { data: posts, loading, error } = useApi('/api/posts');
    
    if (loading) return <div>読み込み中...</div>;
    if (error) return <div>エラー: {error}</div>;
    
    return (
        <ul>
            {posts.map(post => (
                <li key={post.id}>{post.title}</li>
            ))}
        </ul>
    );
}
```

## 状態管理パターン

### Context API
```jsx
import React, { createContext, useContext, useReducer } from 'react';

const ThemeContext = createContext();

const themeReducer = (state, action) => {
    switch (action.type) {
        case 'TOGGLE_THEME':
            return {
                ...state,
                isDark: !state.isDark
            };
        case 'SET_THEME':
            return {
                ...state,
                isDark: action.payload
            };
        default:
            return state;
    }
};

export function ThemeProvider({ children }) {
    const [state, dispatch] = useReducer(themeReducer, { isDark: false });
    
    return (
        <ThemeContext.Provider value={{ state, dispatch }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within ThemeProvider');
    }
    return context;
}
```

## コンポーネント合成

### Compound Components
```jsx
function Tabs({ children, defaultTab }) {
    const [activeTab, setActiveTab] = useState(defaultTab);
    
    return (
        <div className="tabs">
            {React.Children.map(children, child =>
                React.cloneElement(child, { activeTab, setActiveTab })
            )}
        </div>
    );
}

function TabList({ children, activeTab, setActiveTab }) {
    return (
        <div className="tab-list">
            {React.Children.map(children, (child, index) =>
                React.cloneElement(child, { 
                    isActive: activeTab === index,
                    onClick: () => setActiveTab(index)
                })
            )}
        </div>
    );
}

function Tab({ children, isActive, onClick }) {
    return (
        <button 
            className={`tab ${isActive ? 'active' : ''}`}
            onClick={onClick}
        >
            {children}
        </button>
    );
}

// 使用例
function App() {
    return (
        <Tabs defaultTab={0}>
            <TabList>
                <Tab>タブ1</Tab>
                <Tab>タブ2</Tab>
                <Tab>タブ3</Tab>
            </TabList>
        </Tabs>
    );
}
```

効率的なReactアプリケーションを構築するためのパターンを活用しましょう！""",
                "author": "developer",
                "tags": ["React", "JavaScript", "デザイン", "ベストプラクティス"],
                "is_draft": False
            },
            {
                "title": "データベース設計の基本原則",
                "content": """# データベース設計の基本原則

## 正規化

### 第1正規形（1NF）
- すべての属性が原子的（分割不可能）
- 繰り返しグループの排除

```sql
-- 悪い例
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    phones VARCHAR(200)  -- "090-1234-5678,03-1234-5678"
);

-- 良い例
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE customer_phones (
    id INT PRIMARY KEY,
    customer_id INT,
    phone VARCHAR(20),
    phone_type VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### 第2正規形（2NF）
- 1NFを満たす
- 部分関数従属の排除

```sql
-- 悪い例（注文詳細テーブル）
CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),  -- product_idに依存
    product_price DECIMAL(10,2), -- product_idに依存
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- 良い例
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### 第3正規形（3NF）
- 2NFを満たす
- 推移関数従属の排除

```sql
-- 悪い例
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100), -- department_idに推移的に依存
    department_location VARCHAR(100) -- department_idに推移的に依存
);

-- 良い例
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

## インデックス設計

### 単一カラムインデックス
```sql
-- よく検索されるカラムにインデックス
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_date ON orders(created_at);

-- 外部キーにはインデックスが必要
CREATE INDEX idx_order_user_id ON orders(user_id);
```

### 複合インデックス
```sql
-- 複数条件での検索用
CREATE INDEX idx_product_category_price ON products(category_id, price);

-- ORDER BY用
CREATE INDEX idx_order_user_date ON orders(user_id, created_at DESC);

-- カバリングインデックス
CREATE INDEX idx_user_profile_covering 
ON users(status) 
INCLUDE (name, email, created_at);
```

## パフォーマンス最適化

### クエリ最適化
```sql
-- EXISTS vs IN
-- 大きなテーブルの場合はEXISTSが効率的
SELECT u.name 
FROM users u 
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.user_id = u.id 
    AND o.created_at >= '2024-01-01'
);

-- ページネーション
-- OFFSETは避けてカーソルベースを使用
SELECT * FROM posts 
WHERE id > :last_id 
ORDER BY id 
LIMIT 20;

-- 範囲検索の最適化
SELECT * FROM logs 
WHERE created_at >= '2024-01-01' 
AND created_at < '2024-02-01'
AND status = 'active';
```

### パーティショニング
```sql
-- 日付によるパーティショニング
CREATE TABLE logs (
    id BIGINT,
    message TEXT,
    created_at TIMESTAMP,
    user_id INT
) PARTITION BY RANGE (created_at);

CREATE TABLE logs_2024_01 PARTITION OF logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE logs_2024_02 PARTITION OF logs
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## 制約とトリガー

### 制約
```sql
-- チェック制約
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) CHECK (price > 0),
    stock_quantity INT CHECK (stock_quantity >= 0),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'discontinued'))
);

-- ユニーク制約
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL
);
```

### トリガー
```sql
-- 更新日時の自動設定
CREATE OR REPLACE FUNCTION update_modified_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_posts_modified_time
    BEFORE UPDATE ON posts
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_time();

-- 在庫管理
CREATE OR REPLACE FUNCTION update_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE id = NEW.product_id;
    
    IF (SELECT stock_quantity FROM products WHERE id = NEW.product_id) < 0 THEN
        RAISE EXCEPTION '在庫が不足しています';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## バックアップとリカバリ

### 定期バックアップ
```bash
#!/bin/bash
# 日次バックアップスクリプト
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/db"

# フルバックアップ
pg_dump -U postgres -h localhost mydb > $BACKUP_DIR/full_backup_$DATE.sql

# 増分バックアップ（WALファイル）
pg_basebackup -U postgres -h localhost -D $BACKUP_DIR/base_backup_$DATE -Ft -z -P

# 古いバックアップの削除（7日以上）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

効率的で拡張性のあるデータベース設計を心がけましょう！""",
                "author": "admin",
                "tags": ["データベース", "設計", "パフォーマンス", "ベストプラクティス"],
                "is_draft": False
            },
            {
                "title": "API設計のベストプラクティス",
                "content": """# API設計のベストプラクティス

## RESTful設計原則

### リソース指向設計
```
Good:
GET    /api/users          # ユーザー一覧取得
GET    /api/users/123      # 特定ユーザー取得
POST   /api/users          # ユーザー作成
PUT    /api/users/123      # ユーザー更新
DELETE /api/users/123      # ユーザー削除

Bad:
GET    /api/getUsers
POST   /api/createUser
POST   /api/updateUser
POST   /api/deleteUser
```

### ネストしたリソース
```
GET    /api/users/123/posts           # ユーザーの投稿一覧
GET    /api/users/123/posts/456       # 特定ユーザーの特定投稿
POST   /api/users/123/posts           # ユーザーの投稿作成
DELETE /api/users/123/posts/456       # 投稿削除

# 深いネストは避ける（最大2レベル）
Bad: /api/users/123/posts/456/comments/789/likes
Good: /api/comments/789/likes
```

## HTTPステータスコード

### 成功レスポンス
```
200 OK          # 正常に処理完了
201 Created     # リソース作成成功
202 Accepted    # 非同期処理受付
204 No Content  # 正常完了、レスポンスボディなし
```

### エラーレスポンス
```
400 Bad Request         # リクエストが不正
401 Unauthorized        # 認証が必要
403 Forbidden          # アクセス権限なし
404 Not Found          # リソースが存在しない
409 Conflict           # リソースの競合
422 Unprocessable Entity # バリデーションエラー
429 Too Many Requests   # レート制限
500 Internal Server Error # サーバー内部エラー
```

## レスポンス設計

### 一貫したレスポンス形式
```json
# 成功レスポンス
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}

# エラーレスポンス
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "バリデーションエラーが発生しました",
    "details": [
      {
        "field": "email",
        "message": "有効なメールアドレスを入力してください"
      }
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "abc123"
  }
}
```

### ページネーション
```json
{
  "status": "success",
  "data": [
    { "id": 1, "name": "Item 1" },
    { "id": 2, "name": "Item 2" }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false,
    "links": {
      "first": "/api/items?page=1",
      "next": "/api/items?page=2",
      "last": "/api/items?page=5"
    }
  }
}
```

## バージョニング

### URL Path Versioning
```
/api/v1/users
/api/v2/users
```

### Header Versioning
```
GET /api/users
Accept: application/vnd.api+json;version=1
```

### Query Parameter Versioning
```
/api/users?version=1
```

## 認証とセキュリティ

### JWT認証
```javascript
// リクエストヘッダー
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// トークン更新
POST /api/auth/refresh
{
  "refresh_token": "refresh_token_here"
}
```

### API Key認証
```javascript
// ヘッダー認証
{
  "X-API-Key": "your-api-key-here"
}

// クエリパラメータ認証（非推奨）
GET /api/users?api_key=your-api-key
```

## レート制限

### ヘッダー情報
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
Retry-After: 3600
```

### レスポンス例
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "リクエスト制限を超えました",
    "retry_after": 3600
  }
}
```

## フィルタリングとソート

### クエリパラメータ
```
GET /api/users?status=active&role=admin
GET /api/users?sort=created_at&order=desc
GET /api/users?fields=id,name,email
GET /api/users?q=search_term
GET /api/users?created_after=2024-01-01
```

### 複雑な検索
```json
POST /api/users/search
{
  "filters": {
    "status": ["active", "pending"],
    "created_at": {
      "gte": "2024-01-01",
      "lte": "2024-12-31"
    },
    "role": "admin"
  },
  "sort": [
    { "field": "created_at", "order": "desc" },
    { "field": "name", "order": "asc" }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20
  }
}
```

## ドキュメント化

### OpenAPI Specification
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: ユーザー一覧取得
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
```

## テスト戦略

### テスト例
```javascript
describe('User API', () => {
  test('GET /api/users should return user list', async () => {
    const response = await request(app)
      .get('/api/users')
      .expect(200);
    
    expect(response.body.status).toBe('success');
    expect(response.body.data).toBeInstanceOf(Array);
  });
  
  test('POST /api/users should create user', async () => {
    const userData = {
      name: 'John Doe',
      email: 'john@example.com'
    };
    
    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201);
    
    expect(response.body.data.email).toBe(userData.email);
  });
});
```

優れたAPI設計で、使いやすく保守性の高いAPIを構築しましょう！""",
                "author": "developer",
                "tags": ["API", "設計", "ベストプラクティス", "セキュリティ"],
                "is_draft": False
            },
            {
                "title": "Webセキュリティ対策の完全ガイド",
                "content": """# Webセキュリティ対策の完全ガイド

## OWASP Top 10 対策

### 1. インジェクション攻撃対策

#### SQLインジェクション
```python
# 悪い例
query = f"SELECT * FROM users WHERE email = '{user_email}'"
cursor.execute(query)

# 良い例 - パラメータ化クエリ
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (user_email,))

# ORMを使用
user = User.query.filter_by(email=user_email).first()
```

#### NoSQLインジェクション
```javascript
// 悪い例
db.users.find({ email: req.body.email });

// 良い例 - バリデーション
const email = typeof req.body.email === 'string' ? req.body.email : '';
db.users.find({ email: email });
```

### 2. 認証の不備対策

#### パスワードハッシュ化
```python
import bcrypt

# パスワードハッシュ化
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# パスワード検証
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# 使用例
hashed_password = hash_password("user_password")
is_valid = verify_password("user_password", hashed_password)
```

#### 多要素認証（MFA）
```python
import pyotp

def generate_secret():
    return pyotp.random_base32()

def generate_qr_code(user_email, secret):
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name="Your App Name"
    )
    return qrcode.make(totp_uri)

def verify_totp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)
```

### 3. 機密データ漏洩対策

#### 暗号化
```python
from cryptography.fernet import Fernet

# 暗号化キー生成
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# データ暗号化
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

# データ復号化
def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data).decode()
```

#### 環境変数管理
```python
import os
from dotenv import load_dotenv

load_dotenv()

# 機密情報は環境変数から取得
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
API_KEY = os.getenv('API_KEY')

# 設定クラス
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-key-for-dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

### 4. XML外部エンティティ（XXE）対策

```python
import xml.etree.ElementTree as ET

# 悪い例
def parse_xml_unsafe(xml_data):
    return ET.fromstring(xml_data)

# 良い例 - セキュアなパーサー
from defusedxml import ElementTree as SafeET

def parse_xml_safe(xml_data):
    return SafeET.fromstring(xml_data)
```

### 5. アクセス制御の不備対策

#### 認可チェック
```python
from functools import wraps
from flask import g, abort

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user:
                abort(401)
            
            if not g.current_user.has_permission(permission):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin/users')
@require_permission('admin.users.read')
def admin_users():
    return render_template('admin/users.html')
```

### 6. セキュリティ設定ミス対策

#### セキュリティヘッダー
```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# セキュリティヘッダーの設定
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
    }
)

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

### 7. XSS（クロスサイトスクリプティング）対策

#### 入力サニタイゼーション
```python
import bleach
from markupsafe import Markup

# HTMLサニタイゼーション
def sanitize_html(html_content):
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    
    clean_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    return Markup(clean_html)

# テンプレートでの自動エスケープ
from jinja2 import Environment, select_autoescape

env = Environment(autoescape=select_autoescape(['html', 'xml']))
```

### 8. CSRF（クロスサイトリクエストフォージェリ）対策

```python
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
csrf = CSRFProtect(app)

# フォームでCSRFトークン使用
# {{ csrf_token() }} をテンプレートに追加

# AJAX用CSRFトークン
@app.route('/csrf-token')
def csrf_token():
    return jsonify({'csrf_token': generate_csrf()})
```

## セキュリティテスト

### 自動化セキュリティテスト
```python
import requests
import unittest

class SecurityTest(unittest.TestCase):
    
    def test_sql_injection(self):
        # SQLインジェクション攻撃テスト
        malicious_input = "'; DROP TABLE users; --"
        response = requests.post('/api/login', json={
            'email': malicious_input,
            'password': 'test'
        })
        self.assertNotEqual(response.status_code, 500)
    
    def test_xss_protection(self):
        # XSS攻撃テスト
        malicious_script = "<script>alert('XSS')</script>"
        response = requests.post('/api/comments', json={
            'content': malicious_script
        })
        self.assertNotIn('<script>', response.text)
    
    def test_authentication_required(self):
        # 認証が必要なエンドポイントのテスト
        response = requests.get('/api/admin/users')
        self.assertEqual(response.status_code, 401)
```

## 監査とログ

### セキュリティログ
```python
import logging
from datetime import datetime

# セキュリティイベントログ
security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('security.log')
security_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)

def log_security_event(event_type, user_id, ip_address, details):
    security_logger.warning(
        f"SECURITY_EVENT: {event_type} | "
        f"User: {user_id} | "
        f"IP: {ip_address} | "
        f"Details: {details}"
    )

# 使用例
@app.route('/api/login', methods=['POST'])
def login():
    # ログイン試行のログ
    log_security_event(
        'LOGIN_ATTEMPT',
        request.json.get('email'),
        request.remote_addr,
        'Login attempt'
    )
    
    # 失敗時のログ
    if not authenticate_user(email, password):
        log_security_event(
            'LOGIN_FAILURE',
            email,
            request.remote_addr,
            'Invalid credentials'
        )
        return jsonify({'error': 'Invalid credentials'}), 401
```

セキュリティは継続的な取り組みです。定期的な監査と最新の脅威情報の確認を心がけましょう！""",
                "author": "admin",
                "tags": ["セキュリティ", "ベストプラクティス", "OWASP"],
                "is_draft": False
            },
            # ... 続きの記事データ（文字数制限のため一部省略）
        ]
        
        # 追加の記事データ（簡潔版）
        additional_articles = [
            {
                "title": "Docker入門：コンテナ化の基礎",
                "content": "# Docker入門：コンテナ化の基礎\n\nDockerを使ったアプリケーションのコンテナ化について学びます。\n\n## Dockerの基本概念\n- イメージとコンテナ\n- Dockerfile\n- Docker Compose\n\n## 実践例\n```dockerfile\nFROM python:3.9\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nEXPOSE 5000\nCMD [\"python\", \"app.py\"]\n```",
                "author": "developer",
                "tags": ["Docker", "コンテナ", "DevOps"],
                "is_draft": False
            },
            {
                "title": "Git版本管理のワークフロー",
                "content": "# Git版本管理のワークフロー\n\n効果的なGitワークフローについて解説します。\n\n## ブランチ戦略\n- main/master: 本番環境\n- develop: 開発環境\n- feature/: 機能開発\n- hotfix/: 緊急修正\n\n## 基本コマンド\n```bash\ngit checkout -b feature/new-feature\ngit add .\ngit commit -m \"Add new feature\"\ngit push origin feature/new-feature\n```",
                "author": "developer",
                "tags": ["Git", "バージョン管理", "開発環境"],
                "is_draft": False
            },
            {
                "title": "レスポンシブWebデザインの実装",
                "content": "# レスポンシブWebデザインの実装\n\nモバイルファーストのレスポンシブデザインを学びます。\n\n## メディアクエリ\n```css\n/* Mobile First */\n.container {\n  width: 100%;\n  padding: 1rem;\n}\n\n@media (min-width: 768px) {\n  .container {\n    max-width: 750px;\n    margin: 0 auto;\n  }\n}\n\n@media (min-width: 1200px) {\n  .container {\n    max-width: 1140px;\n  }\n}\n```",
                "author": "designer",
                "tags": ["CSS", "デザイン", "レスポンシブ"],
                "is_draft": False
            },
            {
                "title": "テスト駆動開発（TDD）の実践",
                "content": "# テスト駆動開発（TDD）の実践\n\nTDDのサイクルと実装方法を学びます。\n\n## TDDサイクル\n1. Red: 失敗するテストを書く\n2. Green: テストを通すコードを書く\n3. Refactor: コードをリファクタリング\n\n## Pythonでの例\n```python\nimport unittest\n\nclass TestCalculator(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n    \n    def test_divide_by_zero(self):\n        with self.assertRaises(ValueError):\n            divide(10, 0)\n```",
                "author": "tester",
                "tags": ["テスト", "TDD", "品質管理"],
                "is_draft": False
            },
            {
                "title": "CI/CDパイプライン構築ガイド",
                "content": "# CI/CDパイプライン構築ガイド\n\n継続的インテグレーション・デプロイメントの設定方法を解説します。\n\n## GitHub Actions設定\n```yaml\nname: CI/CD Pipeline\n\non:\n  push:\n    branches: [ main ]\n  pull_request:\n    branches: [ main ]\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v2\n    - name: Set up Python\n      uses: actions/setup-python@v2\n      with:\n        python-version: 3.9\n    - name: Install dependencies\n      run: |\n        pip install -r requirements.txt\n    - name: Run tests\n      run: |\n        pytest\n```",
                "author": "manager",
                "tags": ["CI/CD", "自動化", "DevOps"],
                "is_draft": False
            },
            {
                "title": "マイクロサービスアーキテクチャ入門",
                "content": "# マイクロサービスアーキテクチャ入門\n\nマイクロサービスの設計原則と実装パターンを学びます。\n\n## 設計原則\n- 単一責任の原則\n- 独立したデプロイ\n- データの分散\n- 障害の分離\n\n## サービス間通信\n- REST API\n- Message Queue\n- Event Sourcing\n\n## 課題と対策\n- 分散トランザクション\n- サービス発見\n- 監視とログ\n- セキュリティ",
                "author": "admin",
                "tags": ["アーキテクチャ", "マイクロサービス", "設計"],
                "is_draft": False
            },
            {
                "title": "パフォーマンス最適化テクニック",
                "content": "# パフォーマンス最適化テクニック\n\nWebアプリケーションの高速化手法を紹介します。\n\n## フロントエンド最適化\n- 画像圧縮・最適化\n- CSS/JSの最小化\n- CDNの活用\n- 遅延読み込み\n\n## バックエンド最適化\n- データベースインデックス\n- クエリ最適化\n- キャッシュ戦略\n- 非同期処理\n\n## 測定ツール\n- Lighthouse\n- PageSpeed Insights\n- Chrome DevTools\n- New Relic",
                "author": "developer",
                "tags": ["パフォーマンス", "最適化", "Tips"],
                "is_draft": False
            },
            {
                "title": "プロジェクト管理のベストプラクティス",
                "content": "# プロジェクト管理のベストプラクティス\n\nアジャイル開発とプロジェクト管理の手法を学びます。\n\n## スクラム手法\n- スプリント計画\n- デイリースタンドアップ\n- スプリントレビュー\n- レトロスペクティブ\n\n## ツール活用\n- Jira\n- Trello\n- Slack\n- Confluence\n\n## チーム運営\n- 透明性の確保\n- 継続的改善\n- コミュニケーション\n- 品質管理",
                "author": "manager",
                "tags": ["プロジェクト管理", "アジャイル", "チーム"],
                "is_draft": False
            },
            {
                "title": "新人エンジニア向け学習ロードマップ",
                "content": "# 新人エンジニア向け学習ロードマップ\n\n効率的なスキル習得のための学習計画を提案します。\n\n## 第1段階：基礎固め（1-3ヶ月）\n- プログラミング基礎\n- データ構造とアルゴリズム\n- Git/GitHub\n- Linux基本操作\n\n## 第2段階：Web開発（3-6ヶ月）\n- HTML/CSS/JavaScript\n- フレームワーク学習\n- データベース基礎\n- API設計\n\n## 第3段階：実践力向上（6-12ヶ月）\n- 実際のプロジェクト参加\n- コードレビュー\n- テスト作成\n- デプロイ経験\n\n## 継続学習\n- 技術書籍読書\n- 勉強会参加\n- OSS貢献\n- ブログ執筆",
                "author": "manager",
                "tags": ["初心者", "学習", "エンジニア"],
                "is_draft": False
            },
            {
                "title": "コードレビューの効果的な進め方",
                "content": "# コードレビューの効果的な進め方\n\n質の高いコードレビューのポイントを解説します。\n\n## レビュアーの心得\n- 建設的なフィードバック\n- 具体的な改善案の提示\n- 学習機会としての活用\n- 時間をかけた丁寧な確認\n\n## レビュー観点\n- 機能要件の満足\n- コードの可読性\n- パフォーマンス\n- セキュリティ\n- テストカバレッジ\n\n## ツール活用\n- GitHub Pull Request\n- GitLab Merge Request\n- Bitbucket Pull Request\n- レビューチェックリスト\n\n## 改善サイクル\n定期的なレビュー観点の見直しとチーム内での知見共有を行いましょう。",
                "author": "developer",
                "tags": ["コードレビュー", "品質管理", "チーム"],
                "is_draft": False
            },
            {
                "title": "技術選定の判断基準と考慮事項",
                "content": "# 技術選定の判断基準と考慮事項\n\nプロジェクトに最適な技術を選択するための指針を示します。\n\n## 評価軸\n- 学習コスト\n- 開発生産性\n- パフォーマンス\n- 拡張性\n- コミュニティサポート\n- ライセンス\n\n## プロジェクト要件\n- 開発期間\n- チームスキル\n- 予算制約\n- 運用要件\n- セキュリティ要件\n\n## 意思決定プロセス\n1. 要件整理\n2. 候補技術リストアップ\n3. 評価マトリクス作成\n4. プロトタイプ作成\n5. チーム合意形成\n\n技術選定は将来の保守性も考慮した戦略的判断が重要です。",
                "author": "admin",
                "tags": ["技術選定", "プロジェクト管理", "戦略"],
                "is_draft": False
            },
            {
                "title": "リモートワーク環境での開発効率化",
                "content": "# リモートワーク環境での開発効率化\n\n在宅開発での生産性向上のコツを紹介します。\n\n## 環境構築\n- 高性能なPC/Mac\n- 複数モニタ\n- ergonomicキーボード\n- 快適な椅子\n- 安定したネット回線\n\n## ツール活用\n- Visual Studio Code\n- Docker Desktop\n- VPN接続\n- クラウドIDE\n- 画面共有ツール\n\n## コミュニケーション\n- 定期的な1on1\n- チャットツール活用\n- ビデオ会議\n- 非同期コミュニケーション\n- ドキュメント共有\n\n## ワークライフバランス\n適切な休憩時間の確保と明確な勤務時間の設定が重要です。",
                "author": "developer",
                "tags": ["リモートワーク", "生産性", "環境構築"],
                "is_draft": False
            }
        ]
        
        # 全記事データをマージ
        all_articles = articles_data + additional_articles
        
        # 記事作成
        created_articles = []
        for i, article_data in enumerate(all_articles):
            # 作成日時を過去数日に分散
            days_ago = random.randint(1, 30)
            created_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
            updated_time = created_time + timedelta(hours=random.randint(0, 48))
            
            article = Knowledge(
                title=article_data["title"],
                content=article_data["content"],
                author=article_data["author"],
                created_at=created_time,
                updated_at=updated_time,
                is_draft=article_data.get("is_draft", False)
            )
            db.session.add(article)
            db.session.flush()  # IDを取得するため
            
            # タグの関連付け
            for tag_name in article_data.get("tags", []):
                if tag_name in tags:
                    article.tags.append(tags[tag_name])
                    tags[tag_name].usage_count += 1
            
            created_articles.append(article)
        
        db.session.commit()
        print(f"   ✅ {len(created_articles)}件の記事を作成しました")
        
        # 4. いいね・コメントデータの作成
        print("❤️  いいね・コメントデータを作成中...")
        
        comments_data = [
            "素晴らしい記事ですね！とても参考になりました。",
            "実装例がわかりやすくて助かります。",
            "この手法は知りませんでした。今度試してみます。",
            "質問：これをProduction環境で使う場合の注意点はありますか？",
            "ありがとうございます。自分のプロジェクトでも活用させていただきます。",
            "追加情報：別のアプローチとして○○という方法もあります。",
            "詳細な解説をありがとうございます。",
            "初心者にもわかりやすい説明で助かりました。",
            "コード例が実践的でとても良いですね。",
            "続編も楽しみにしています！"
        ]
        
        total_likes = 0
        total_comments = 0
        
        for article in created_articles:
            # ランダムでいいねを追加
            like_count = random.randint(0, 8)
            liked_users = random.sample(users, min(like_count, len(users)))
            
            for user in liked_users:
                if user != article.author:  # 自分の記事にはいいねできない
                    like = Like(
                        user_id=user,
                        knowledge_id=article.id,
                        created_at=article.created_at + timedelta(hours=random.randint(1, 72))
                    )
                    db.session.add(like)
                    total_likes += 1
            
            # ランダムでコメントを追加
            comment_count = random.randint(0, 4)
            for _ in range(comment_count):
                commenter = random.choice([u for u in users if u != article.author])
                comment_content = random.choice(comments_data)
                
                comment = Comment(
                    content=comment_content,
                    author=commenter,
                    knowledge_id=article.id,
                    created_at=article.created_at + timedelta(hours=random.randint(2, 96))
                )
                db.session.add(comment)
                db.session.flush()  # IDを取得
                
                # コメントにもランダムでいいねを追加
                comment_like_count = random.randint(0, 3)
                comment_liked_users = random.sample(users, min(comment_like_count, len(users)))
                
                for user in comment_liked_users:
                    if user != comment.author:  # 自分のコメントにはいいねできない
                        comment_like = CommentLike(
                            user_id=user,
                            comment_id=comment.id,
                            created_at=comment.created_at + timedelta(hours=random.randint(1, 24))
                        )
                        db.session.add(comment_like)
                
                total_comments += 1
        
        # 下書き記事をいくつか作成
        print("📝 下書き記事を作成中...")
        draft_articles = [
            {
                "title": "GraphQL入門（執筆中）",
                "content": "# GraphQL入門\n\n## 概要\nGraphQLについて学習中です...\n\n（この記事は現在執筆中です）",
                "author": "developer",
                "tags": ["GraphQL", "API"],
                "is_draft": True
            },
            {
                "title": "Kubernetes運用ガイド（下書き）",
                "content": "# Kubernetes運用ガイド\n\nコンテナオーケストレーションについて...\n\n（まだ未完成です）",
                "author": "admin",
                "tags": ["Kubernetes", "DevOps"],
                "is_draft": True
            }
        ]
        
        for draft_data in draft_articles:
            draft = Knowledge(
                title=draft_data["title"],
                content=draft_data["content"],
                author=draft_data["author"],
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(10, 120)),
                is_draft=True
            )
            db.session.add(draft)
            db.session.flush()
            
            # 下書きにもタグを追加
            for tag_name in draft_data.get("tags", []):
                if tag_name in tags:
                    draft.tags.append(tags[tag_name])
        
        db.session.commit()
        
        print(f"   ✅ {total_likes}個のいいね、{total_comments}個のコメントを作成しました")
        print(f"   ✅ {len(draft_articles)}件の下書き記事を作成しました")
        
        # 5. 統計情報の表示
        print("\n📊 作成されたテストデータの統計:")
        print(f"   📚 記事総数: {Knowledge.query.count()}件")
        print(f"   📖 公開記事: {Knowledge.query.filter_by(is_draft=False).count()}件")
        print(f"   📝 下書き記事: {Knowledge.query.filter_by(is_draft=True).count()}件")
        print(f"   🏷️  タグ総数: {Tag.query.count()}個")
        print(f"   ❤️  いいね総数: {Like.query.count()}個")
        print(f"   💬 コメント総数: {Comment.query.count()}個")
        print(f"   👥 ユーザー数: {len(users)}人")
        
        # タグ使用回数トップ5
        popular_tags = Tag.query.order_by(Tag.usage_count.desc()).limit(5).all()
        print(f"\n🔥 人気タグ TOP5:")
        for i, tag in enumerate(popular_tags, 1):
            print(f"   {i}. {tag.name} ({tag.usage_count}回使用)")
        
        # 6. 閲覧履歴データの作成
        print("\n👀 閲覧履歴データを作成中...")
        
        # 公開記事のみを対象にする
        published_articles = Knowledge.query.filter_by(is_draft=False).all()
        total_views = 0
        
        # 過去30日間の閲覧履歴を作成
        for article in published_articles:
            # 記事ごとに異なる人気度を設定（IDが小さいほど人気）
            base_popularity = max(1, 21 - article.id)  # ID 1-20の記事で人気度を調整
            view_probability = min(0.8, base_popularity / 20)  # 最大80%の確率
            
            # 過去30日間にわたって閲覧履歴を分散
            for days_ago in range(30):
                view_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
                
                # 各ユーザーが各日にこの記事を閲覧するかどうかを決定
                for user in users:
                    # 自分の記事は閲覧しない
                    if user == article.author:
                        continue
                    
                    # 確率的に閲覧するかどうか決定
                    if random.random() < view_probability:
                        # 同日の重複をチェック（実際のアプリと同じロジック）
                        existing_view = ViewHistory.query.filter(
                            ViewHistory.user_id == user,
                            ViewHistory.knowledge_id == article.id,
                            db.func.date(ViewHistory.viewed_at) == view_date.date()
                        ).first()
                        
                        if not existing_view:
                            # 日中のランダムな時間を設定
                            random_hour = random.randint(8, 22)  # 8時から22時の間
                            random_minute = random.randint(0, 59)
                            view_time = view_date.replace(
                                hour=random_hour, 
                                minute=random_minute, 
                                second=random.randint(0, 59)
                            )
                            
                            view_history = ViewHistory(
                                user_id=user,
                                knowledge_id=article.id,
                                viewed_at=view_time
                            )
                            db.session.add(view_history)
                            total_views += 1
        
        db.session.commit()
        print(f"   ✅ {total_views}件の閲覧履歴を作成しました")
        
        # 更新された統計情報の表示
        print("\n📊 作成されたテストデータの統計:")
        print(f"   📚 記事総数: {Knowledge.query.count()}件")
        print(f"   📖 公開記事: {Knowledge.query.filter_by(is_draft=False).count()}件")
        print(f"   📝 下書き記事: {Knowledge.query.filter_by(is_draft=True).count()}件")
        print(f"   🏷️  タグ総数: {Tag.query.count()}個")
        print(f"   ❤️  いいね総数: {Like.query.count()}個")
        print(f"   💬 コメント総数: {Comment.query.count()}個")
        print(f"   👀 閲覧履歴総数: {ViewHistory.query.count()}件")
        print(f"   👥 ユーザー数: {len(users)}人")
        
        print("\n✅ テストデータの作成が完了しました！")
        print("🚀 アプリケーションを起動して確認してください:")
        print("   python app.py")

if __name__ == '__main__':
    create_test_data()