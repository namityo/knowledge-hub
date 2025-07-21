#!/usr/bin/env python3
"""
データベース初期化とマイグレーション管理

アプリケーション起動時のデータベース設定と自動マイグレーション機能を提供
"""

import os
from pathlib import Path
import re


def cleanup_duplicate_migrations():
    """重複したマイグレーションファイルをクリーンアップ"""
    migrations_path = Path('migrations/versions')
    if not migrations_path.exists():
        return
    
    # 既存のマイグレーションファイルを取得
    migration_files = list(migrations_path.glob('*.py'))
    
    # 'initial_database_schema' という名前のファイルを特定
    initial_migrations = [
        f for f in migration_files 
        if 'initial_database_schema' in f.name.lower()
    ]
    
    if len(initial_migrations) > 1:
        print(f"⚠️  重複した初期マイグレーションファイルが見つかりました: {len(initial_migrations)}個")
        
        # 最新のファイル以外を削除
        initial_migrations.sort(key=lambda x: x.stat().st_mtime)
        files_to_remove = initial_migrations[:-1]  # 最新以外
        
        for file_path in files_to_remove:
            print(f"🗑️  重複ファイルを削除: {file_path.name}")
            file_path.unlink()
        
        print(f"✅ 重複マイグレーションファイル {len(files_to_remove)}個を削除しました")


def auto_migrate_database(app, db):
    """アプリケーション起動時にデータベースのマイグレーションを自動実行"""
    
    with app.app_context():
        try:
            # migrationsフォルダの存在確認
            migrations_path = Path('migrations')
            
            # Flask-Migrateが利用可能かチェック
            try:
                from flask_migrate import init, migrate, upgrade, current
                print("🔧 データベースマイグレーション確認中...")
            except ImportError:
                print("⚠️  Flask-Migrateがインストールされていません。通常のdb.create_all()を使用します。")
                db.create_all()
                print("✅ データベーステーブル作成完了")
                return
            
            if not migrations_path.exists():
                print("📁 初回起動: マイグレーション環境を初期化中...")
                init()
                print("✅ マイグレーション環境初期化完了")
            
            # 重複マイグレーションファイルのクリーンアップ
            cleanup_duplicate_migrations()
            
            # 既存マイグレーションファイルの確認
            versions_path = migrations_path / 'versions'
            existing_migrations = list(versions_path.glob('*.py')) if versions_path.exists() else []
            
            try:
                # 現在のマイグレーション状態を確認
                current_rev = current()
                
                if current_rev is None and not existing_migrations:
                    # 新規データベースで初回マイグレーションが存在しない場合のみ作成
                    print("📊 新規データベース: 初期マイグレーションを作成中...")
                    migrate(message="Initial database schema")
                    upgrade()
                    print("✅ 初期データベースセットアップ完了")
                elif current_rev is None and existing_migrations:
                    # マイグレーションファイルは存在するが、データベースに記録がない場合
                    print("⚠️  既存のマイグレーションファイルが見つかりました。最新状態としてマークします...")
                    upgrade()
                    print("✅ データベースを既存マイグレーション状態に更新完了")
                else:
                    # 通常のマイグレーション適用
                    print(f"🔄 マイグレーション適用中... (現在: {current_rev})")
                    upgrade()
                    print("✅ マイグレーション適用完了")
                    
            except Exception as migrate_error:
                print(f"⚠️  マイグレーション処理中にエラー: {migrate_error}")
                
                # フォールバック: 既存のデータベースがある場合はそのまま使用
                db_instance_path = Path('instance')
                db_files = list(db_instance_path.glob('*.db')) if db_instance_path.exists() else []
                if db_files:
                    print("📊 既存データベースをそのまま使用します")
                else:
                    print("🔧 フォールバック: 基本テーブル作成を実行")
                    db.create_all()
                    print("✅ 基本テーブル作成完了")
                    
        except Exception as e:
            print(f"❌ データベース初期化エラー: {e}")
            print("🔧 フォールバック: 基本テーブル作成を実行")
            db.create_all()
            print("✅ 基本テーブル作成完了")


def setup_database_migration(app, db):
    """データベースとマイグレーションの初期設定"""
    from flask_migrate import Migrate
    
    # マイグレーションの初期化
    migrate = Migrate(app, db)
    
    # アプリケーション起動時にマイグレーションを自動実行
    auto_migrate_database(app, db)
    
    return migrate