#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge Base Application Entry Point

ナレッジベースアプリケーションのエントリーポイント
app/パッケージからアプリケーションファクトリーをインポートして使用
"""

from app import create_app

# アプリケーションの作成
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=True, use_debugger=True)