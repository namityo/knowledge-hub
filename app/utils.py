import os
import uuid
import mimetypes
from flask import request, flash
from werkzeug.utils import secure_filename
from .models import db, Tag, Attachment
from .config import validate_user_id, allowed_file, DEFAULT_USER_ID, setup_audit_logging, USER_ID_PATTERN, USER_ID_HEADER_NAME

# 監査ログのセットアップ
audit_logger = setup_audit_logging()

def get_current_user_id():
    """HTTPヘッダーからユーザーIDを取得・検証"""
    try:
        user_id = request.headers.get(USER_ID_HEADER_NAME, DEFAULT_USER_ID)
        
        if not validate_user_id(user_id):
            # 無効なユーザーIDの場合はエラーログを出力してデフォルトユーザーIDを返す
            audit_logger.warning(f"Invalid user ID format: '{user_id}' - Pattern: {USER_ID_PATTERN}")
            return DEFAULT_USER_ID
        
        return user_id
    except RuntimeError:
        # リクエストコンテキスト外（テストデータ作成時など）
        return 'system'

def handle_file_uploads(knowledge_id, author, app_config):
    """ファイルアップロード処理の共通化"""
    uploaded_files = request.files.getlist('attachments')
    for file in uploaded_files:
        if file and file.filename:
            if not allowed_file(file.filename):
                flash(f'ファイル "{file.filename}" は許可されていない形式です。', 'error')
                continue
            
            # 安全なファイル名を生成
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            stored_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # ファイルを保存
            file_path = os.path.join(app_config['UPLOAD_FOLDER'], stored_filename)
            try:
                file.save(file_path)
            except Exception as e:
                flash(f'ファイル "{file.filename}" の保存に失敗しました。', 'error')
                continue
            
            # ファイルサイズとMIMEタイプを取得
            file_size = os.path.getsize(file_path)
            mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
            
            # 添付ファイル情報をDBに保存
            attachment = Attachment(
                filename=original_filename,
                stored_filename=stored_filename,
                file_size=file_size,
                mime_type=mime_type,
                knowledge_id=knowledge_id,
                uploaded_by=author
            )
            db.session.add(attachment)
    
    # ドラッグ&ドロップでアップロードされた画像の関連付けを更新
    orphaned_attachments = Attachment.query.filter_by(knowledge_id=None, uploaded_by=author).all()
    for attachment in orphaned_attachments:
        attachment.knowledge_id = knowledge_id
    
    # 10%の確率で古い孤立ファイルをクリーンアップ（負荷分散）
    import random
    if random.random() < 0.1:
        try:
            cleanup_orphaned_attachments()
        except Exception as e:
            audit_logger.error(f"Background cleanup failed: {e}")

def cleanup_orphaned_attachments():
    """孤立した添付ファイルをクリーンアップ"""
    import os
    from datetime import datetime, timezone, timedelta
    from flask import current_app
    
    cleaned_count = 0
    
    # 1. 24時間以上前に作成されたknowledge_id=Nullのファイル
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    orphaned_files = Attachment.query.filter(
        Attachment.knowledge_id.is_(None),
        Attachment.created_at < cutoff_time
    ).all()
    
    for attachment in orphaned_files:
        if current_app:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment.stored_filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    audit_logger.info(f"Cleaned up orphaned file: {attachment.stored_filename}")
            except OSError as e:
                audit_logger.error(f"Failed to delete orphaned file {file_path}: {e}")
        
        db.session.delete(attachment)
        cleaned_count += 1
    
    # 2. データベースレコードが存在しないファイル（記事削除時の残骸）
    if current_app:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            # データベースに存在するファイル名のセットを作成
            existing_files = set()
            all_attachments = Attachment.query.all()
            for attachment in all_attachments:
                existing_files.add(attachment.stored_filename)
            
            # アップロードフォルダ内の実ファイルをチェック
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                if os.path.isfile(file_path) and filename not in existing_files:
                    try:
                        # ファイルが7日以上古い場合のみ削除（安全のため）
                        file_mtime = os.path.getmtime(file_path)
                        file_age = datetime.now().timestamp() - file_mtime
                        if file_age > (7 * 24 * 3600):  # 7日
                            os.remove(file_path)
                            audit_logger.info(f"Cleaned up dangling file: {filename}")
                            cleaned_count += 1
                    except OSError as e:
                        audit_logger.error(f"Failed to delete dangling file {file_path}: {e}")
    
    if cleaned_count > 0:
        db.session.commit()
        audit_logger.info(f"Cleaned up {cleaned_count} orphaned/dangling files")

def handle_tags(knowledge, tags_string, author):
    """タグ処理の共通化"""
    if not tags_string:
        return
    
    # 既存のタグ関連付けをクリア
    knowledge.tags.clear()
    
    # タグ文字列をパース（カンマ区切り）
    tag_names = [name.strip() for name in tags_string.split(',') if name.strip()]
    
    for tag_name in tag_names:
        # タグ名の長さ制限
        if len(tag_name) > 50:
            flash(f'タグ "{tag_name}" が長すぎます（最大50文字）。', 'warning')
            continue
        
        # 既存のタグを検索または新規作成
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name, created_by=author)
            db.session.add(tag)
        
        # 使用回数を増加
        if tag.usage_count is None:
            tag.usage_count = 1
        else:
            tag.usage_count += 1
        
        # ナレッジにタグを関連付け
        if tag not in knowledge.tags:
            knowledge.tags.append(tag)

def get_bulk_view_counts(knowledge_list, days=None):
    """複数の記事の閲覧数を一括取得（N+1問題を回避）
    
    Note: 単一記事の場合は knowledge.get_view_count() を使用
    """
    from .models import ViewHistory, db
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func
    
    if not knowledge_list:
        return {}
    
    knowledge_ids = [k.id for k in knowledge_list]
    
    # 基本クエリ
    query = db.session.query(
        ViewHistory.knowledge_id,
        func.count(ViewHistory.id).label('view_count')
    ).filter(ViewHistory.knowledge_id.in_(knowledge_ids))
    
    # 期間指定がある場合
    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(ViewHistory.viewed_at >= cutoff_date)
    
    # 結果を辞書に変換
    results = query.group_by(ViewHistory.knowledge_id).all()
    return {result.knowledge_id: result.view_count for result in results}

def get_bulk_like_counts(knowledge_list, days=None):
    """複数の記事のいいね数を一括取得（N+1問題を回避）
    
    Note: 単一記事の場合は knowledge.get_like_count() を使用
    """
    from .models import Like, db
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func
    
    if not knowledge_list:
        return {}
    
    knowledge_ids = [k.id for k in knowledge_list]
    
    # 基本クエリ
    query = db.session.query(
        Like.knowledge_id,
        func.count(Like.id).label('like_count')
    ).filter(Like.knowledge_id.in_(knowledge_ids))
    
    # 期間指定がある場合
    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(Like.created_at >= cutoff_date)
    
    # 結果を辞書に変換
    results = query.group_by(Like.knowledge_id).all()
    return {result.knowledge_id: result.like_count for result in results}

def get_bulk_comment_counts(knowledge_list, days=None):
    """複数の記事のコメント数を一括取得（N+1問題を回避）
    
    Note: 単一記事の場合は knowledge.get_comment_count() を使用
    """
    from .models import Comment, db
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func
    
    if not knowledge_list:
        return {}
    
    knowledge_ids = [k.id for k in knowledge_list]
    
    # 基本クエリ
    query = db.session.query(
        Comment.knowledge_id,
        func.count(Comment.id).label('comment_count')
    ).filter(Comment.knowledge_id.in_(knowledge_ids))
    
    # 期間指定がある場合
    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(Comment.created_at >= cutoff_date)
    
    # 結果を辞書に変換
    results = query.group_by(Comment.knowledge_id).all()
    return {result.knowledge_id: result.comment_count for result in results}

def get_bulk_engagement_stats(knowledge_list, days=None):
    """複数の記事のエンゲージメント統計を一括取得（閲覧・いいね・コメント）
    
    Args:
        knowledge_list: Knowledge オブジェクトのリスト
        days: 期間指定（None=全期間、30=直近30日など）
    
    Returns:
        dict: {knowledge.id: {'views': count, 'likes': count, 'comments': count}}
    
    Note: 個別記事の場合は以下の統一APIを使用:
        - knowledge.get_view_count()     # 総閲覧数
        - knowledge.get_like_count()     # 総いいね数
        - knowledge.get_comment_count()  # 総コメント数
    """
    view_counts = get_bulk_view_counts(knowledge_list, days)
    like_counts = get_bulk_like_counts(knowledge_list, days)
    comment_counts = get_bulk_comment_counts(knowledge_list, days)
    
    # 全記事のIDでデフォルト値0の辞書を作成
    stats = {}
    for knowledge in knowledge_list:
        stats[knowledge.id] = {
            'views': view_counts.get(knowledge.id, 0),
            'likes': like_counts.get(knowledge.id, 0),
            'comments': comment_counts.get(knowledge.id, 0)
        }
    
    return stats