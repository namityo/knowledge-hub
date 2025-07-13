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