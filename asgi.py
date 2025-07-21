#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ASGI Entry Point for Uvicorn
uvicorn用のASGIエントリーポイント

Usage:
  uvicorn asgi:app --host 127.0.0.1 --port 5000 --reload
"""

from asgiref.wsgi import WsgiToAsgi
from app import create_app

def create_asgi_app():
    """ASGI対応のアプリケーション作成"""
    # 通常のFlaskアプリケーションを作成
    flask_app = create_app()
    
    # WSGIアプリケーションをASGIに変換
    asgi_app = WsgiToAsgi(flask_app)
    
    return asgi_app

# ASGIアプリケーションの作成
app = create_asgi_app()

if __name__ == '__main__':
    import uvicorn
    
    # Uvicornでの起動設定
    uvicorn.run(
        "asgi:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info",
        access_log=True
    )