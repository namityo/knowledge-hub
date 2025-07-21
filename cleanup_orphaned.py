#!/usr/bin/env python3
"""
孤立した添付ファイルをクリーンアップするスクリプト
"""

import sys
import os
from datetime import datetime

def main():
    """メイン処理"""
    print("=== 孤立添付ファイル クリーンアップ ===")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Flaskアプリケーションコンテキストを作成
        from app import create_app
        from app.utils import cleanup_orphaned_attachments
        
        app = create_app()
        
        with app.app_context():
            # クリーンアップ実行
            cleanup_orphaned_attachments()
            print("✅ クリーンアップが正常に完了しました")
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("app.pyが存在し、依存関係がインストールされていることを確認してください")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()